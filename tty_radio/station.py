from __future__ import print_function
import platform
PY3 = False
if platform.python_version().startswith('3'):
    PY3 = True
from os import rename
import csv
from bs4 import BeautifulSoup
from time import time
from os.path import (
    expanduser,
    join as path_join,
    getmtime as getmtime,
    isfile as isfile)
if PY3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

from . import DEBUG
from .stream import Stream

# maximum age of any channel file before rebuilding it
CHAN_AGE_LIMIT = 7  # in days
FILE_PREFIX = '.tty_radio-'
FILE_EXT = '.csv'


class Station(object):
    ui_name = 'Radio'

    def __init__(self, name, rebuild=True):
        self.name = name
        self.rebuild = rebuild
        # TODO OS agnostic $HOME
        home = expanduser('~')
        fname = FILE_PREFIX + name + FILE_EXT
        self.file = path_join(home, fname)
        self.check_file()
        self.streams = []
        self.init_streams()

    def __str__(self):
        return ('Station(name=%s,rebuild=%s,file=%s)' %
                (self.name, self.rebuild, self.file))

    def __repr__(self):
        return str(self)

    def build_file(self):
        raise Exception('Not implemented')
        """
        Manually building some of the URLs:
        * WCPE Classical
            * https://theclassicalstation.org/internet.shtml
            * http://audio-mp3.ibiblio.org:8000/wcpe.mp3 <- direct
            * http://www.ibiblio.org/wcpe/wcpe.pls,WCPE Classical,"TheClassicalStation.org 24/7 classical music from Wake Forest, NC",http://theclassicalstation.org/images/wcpe_footer.jpg
        * WNRN
            * goto http://www.wnrn.org/listen/ get link at "Load Stream" drop the final .m3u(or look at file at URL contents)
            * http://broadcast.wnrn.org:8000/wnrn.mp3,WNRN Cville,Independent Radio,http://www.wnrn.org/wp-content/themes/WNRN/images/logo2.gif
        """  # noqa

    def check_file(self):
        if not isfile(self.file):
            self.build_file()
        # if channel file older than X days rebuild
        age_limit = time() - (60 * 60 * 24 * CHAN_AGE_LIMIT)
        if self.rebuild and getmtime(self.file) < age_limit:
            # on except of getmtime set chan_age = 0
            rename(self.file, self.file + ".bck")
            self.build_file()

    def init_streams(self):
        with open(self.file, 'r') as f:
            for row in csv.reader(f):
                # Skip rows that don't have three columns or
                #   rows that begin with '#'
                if len(row) != 4 or row[0][0] == '#':
                    continue
                row = [col.strip() for col in row]
                self.streams.append(
                    Stream(
                        self.name,
                        row[1],
                        row[0],
                        row[2],
                        row[3],
                        self.reader))

    def stream_obj(self, stream):
        possibles = [st for st in self.streams if stream == st.name]
        if len(possibles) != 1:
            return None
        return possibles[0]

    def reader(self, line):
        if DEBUG:
            print('station sees: %s' % line)


class Soma(Station):
    ui_name = 'SomaFM'

    def __init__(self):
        self.parse_url = "http://somafm.com"
        self.stream_url_base = "http://ice.somafm.com/"
        super(Soma, self).__init__(name='soma', rebuild=True)

    def build_file(self):
        # Scrapes channels from somafm.com
        # original at https://gist.github.com/roamingryan/2343819
        # mod'ed Feb 2014
        #   store name and desc seo; add img url
        #   handle specific bad streams
        page = urlopen(self.parse_url)
        soup = BeautifulSoup(page, "html.parser")
        chan_instances = soup.findAll('li', {"class": "cbshort"})
        print("Building new file from somafm.com...")
        if PY3:
            # per doc TypeError: 'str' does not support the buffer interface
            csv_file = open(self.file, 'w', newline='')
        else:
            csv_file = open(self.file, 'w')
        chan_writer = csv.writer(csv_file)
        for inst in chan_instances:
            stream_url_short = inst.find('a')['href'].replace("/", "")
            # for some reason, the following aren't at the expected URL
            # use: http://somafm.com/ +
            #    stream_url_short +
            #    /directstreamlinks.html
            #   and look under MP3 128kb for Direct Server: http://fqdn:port
            # consider doing this longer procedure for all channels
            # but for now, just hard code those that don't play well
            # format of stream url
            # original py script template: http://ice.somafm.com/<NAME>
            # but that isn't doc'ed on soma's site anywhere
            # what is the preferred/polite link?
            # from: http://somafm.com/lush/directstreamlinks.html:
            #   http://somafm.com/<NAME>.pls  for 128 Kb
            #   http://somafm.com/<NAME>24.pls  for 24 Kb
            #   but this doesn't load in mpg123 at all
            # from other links on somafm site:
            #   http://somafm.com/play/<NAME>
            #   but this doesn't load in mpg123 at all
            # mpg123 can handle the "direct links",
            # but to parse for these would
            # require requesting each channel's directstreamlinks.html
            if stream_url_short == "airwaves":
                stream_url = "http://uwstream2.somafm.com:5400"
            elif stream_url_short == "earwaves":
                stream_url = "http://sfstream1.somafm.com:5100"
            else:
                stream_url = (self.stream_url_base +
                              stream_url_short)
            stream_name = inst.find('a').find('img')['alt'].split(":")[0]
            stream_img  = self.parse_url + inst.find('a').find('img')['src']
            stream_desc = inst.find('p').string
            csv_row = [stream_url, stream_name, stream_desc, stream_img]
            chan_writer.writerow(csv_row)
            # so ascii art gets a page each
            # os.system('cls' if os.name == 'nt' else 'clear')
            print("  %s, %s, %s" % (stream_url, stream_name, stream_desc))
        csv_file.close()


class Favs(Station):
    ui_name = 'Favorites'

    def __init__(self):
        super(Favs, self).__init__(name='favs', rebuild=False)

    def build_file(self):
        favs = """\
# CSV of stations columns:
# Stream URL, Station Name, Description, Album Art URL
http://www.ibiblio.org/wcpe/wcpe.pls,WCPE Classical,"TheClassicalStation.org from Wake Forest, NC",http://theclassicalstation.org/images/wcpe_footer.jpg
http://ice.somafm.com/defcon,DEF CON Radio,Music for Hacking,http://somafm.com/img/defcon120.png
http://ice.somafm.com/groovesalad,Groove Salad,Nice chill plate of ambient/downtempo beats and grooves,http://somafm.com/img/groovesalad120.png
http://broadcast.wnrn.org:8000/wnrn.mp3,WNRN Cville,"Charlottesville, VA Independent Radio",http://www.wnrn.org/wp-content/themes/WNRN/images/logo2.gif
http://ice.somafm.com/bagel,BAGeL Radio,What alternative rock radio should sound like,http://somafm.com/img/bagel120.png
http://ice.somafm.com/folkfwd,Folk Forward,"Indie, Alt, and Classic folk",http://somafm.com/img/folkfwd120.jpg
http://ice.somafm.com/lush,Lush,"Electronica with sensuous/mellow vocals, mostly female",http://somafm.com/img/lush-x120.jpg
http://ice.somafm.com/suburbsofgoa,Suburbs of Goa,Desi-influenced Asian world beats and beyond,http://somafm.com/img/sog120.jpg
http://ice.somafm.com/u80s,Underground 80s,Early 80s UK Synthpop and a bit of New Wave,http://somafm.com/img/u80s-120.png
"""  # noqa
        print("Building new file from default favs...")
        with open(self.file, 'w') as f:
            f.write(favs)
