from __future__ import print_function
import platform
PY3 = False
if platform.python_version().startswith('3'):
    PY3 = True
import csv
import os
import sys
import time
from os.path import (
    expanduser,
    join as path_join,
    getmtime as os_getmtime
)
from bs4 import BeautifulSoup
if PY3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

from . import (
    FAVS_CHAN_FILENAME,
    SOMA_CHAN_FILENAME,
    FAVS_DEFAULT,
    CHAN_AGE_LIMIT,
    SOMA_PARSE_URL,
    SOMA_STREAM_BASE_URL,
    SOMA_STREAM_END_URL
)
from .color import colors
from .album import gen_art


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


def get_fname(mode):
    # TODO OS agnostic $HOME
    home = expanduser('~')
    if mode == 'soma':
        fname = SOMA_CHAN_FILENAME
    else:  # mode == 'favs'
        fname = FAVS_CHAN_FILENAME
    return path_join(home, fname)


def build_favs(outfile):
    print("Building new file from default favs...")
    csv_chan_file = open(outfile, 'w')
    csv_chan_file.write(FAVS_DEFAULT)
    csv_chan_file.close()
    return


def build_soma(outfile):
    # Scrapes channels from somafm.com
    # original at https://gist.github.com/roamingryan/2343819
    # mod'ed Feb 2014
    #   store name and desc seo; add img url
    #   handle specific bad streams
    page = urlopen(SOMA_PARSE_URL)
    soup = BeautifulSoup(page, "html.parser")
    chan_instances = soup.findAll('li', {"class": "cbshort"})

    print("Building new file from somafm.com...")
    if PY3:
        # per doc TypeError: 'str' does not support the buffer interface
        csv_chan_file = open(outfile, 'w', newline='')
    else:
        csv_chan_file = open(outfile, 'w')
    chan_writer = csv.writer(csv_chan_file)
    for inst in chan_instances:
        stream_url_short = inst.find('a')['href'].replace("/", "")
        # for some reason, the following aren't at the expected URL
        # use: http://somafm.com/ + stream_url_short + /directstreamlinks.html
        #   and look under MP3 128kb for Direct Server: http://fqdn:port
        # consider doing this longer procedure for all channels
        # but for now, just hard code those that don't play well
        if stream_url_short == "airwaves":
            stream_url = "http://uwstream2.somafm.com:5400"
        elif stream_url_short == "earwaves":
            stream_url = "http://sfstream1.somafm.com:5100"
        else:
            stream_url = (SOMA_STREAM_BASE_URL +
                          stream_url_short +
                          SOMA_STREAM_END_URL)
        stream_name = inst.find('a').find('img')['alt'].split(":")[0]
        stream_img  = SOMA_PARSE_URL + inst.find('a').find('img')['src']
        stream_desc = inst.find('p').string
        csv_row = [stream_url, stream_name, stream_desc, stream_img]
        chan_writer.writerow(csv_row)
        # so ascii art gets a page each
        # os.system('cls' if os.name == 'nt' else 'clear')
        print("  %s, %s, %s" % (stream_url, stream_name, stream_desc))
        art = gen_art(stream_img, 80, 40)
        if art is not None:
            print(art)
    csv_chan_file.close()
    return


def assert_stationfile(mode):
    filename = get_fname(mode)
    rebuild = False
    if not os.path.exists(filename):
        with colors("red"):
            print("File(%s) missing, rebuilding" % filename)
        rebuild = True
    elif mode != 'favs':
        age_limit = time.time() - (60 * 60 * 24 * CHAN_AGE_LIMIT)
        chan_age = os_getmtime(filename)
        # on except of getmtime set chan_age = 0
        # if channel file older than X days rebuild
        if chan_age < age_limit:
            with colors("red"):
                print("File(%s) is too old, backing up and rebuilding" %
                      filename)
            rebuild = True
            # TODO OS agnostic mv
            os.system("mv " + filename + " " + filename + ".bck")
    if not rebuild:
        return
    if mode == 'favs':
        build_favs(filename)
    elif mode == 'soma':
        build_soma(filename)
    with colors("red"):
        print("Finished building channel file")


def get_stations(mode):
    assert_stationfile(mode)
    try:
        csv_fd = open(get_fname(mode), 'r')
    except IOError as e:
        with colors("red"):
            print("Error (%s) opening channel, please run again." % e)
        sys.exit(1)
    i = 0
    chans = {}
    for row in csv.reader(csv_fd):
        # Skip rows that don't have three columns or rows that begin with '#'
        if len(row) != 4 or row[0][0] == '#':
            continue
        for j in range(len(row)):
            row[j] = row[j].strip()
            # if j == 1 or j == 2:
            #     print("chans[" + str(i) + "][" + str(j) + "]: '" +
            #           row[j] + "'")
        chans[i] = row
        i += 1
    return chans
