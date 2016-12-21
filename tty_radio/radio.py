from __future__ import print_function
########################################
# Streaming radio terminal client
# v0.1.4           Convert to pyradio
# v0.1.3 25Sep2014 Added proxy support
# v0.1.2  7Aug2014 Added favs
# v0.1.1  6Mar2014 Added Di.FM
# v0.0.0           based on https://gist.github.com/roamingryan/2343819
# Designed to use mpg123, but you can use any player that doesn't buffer stdout
#
# To use:
#   run radio or radio -h to see all the argument options
#   select station at prompt, by number in left column
#   enjoy
#
# TODO
#   generate and use pls/m3u files as web-parsed storage
#      possibly move web-scrape to CLarg and only on demand (but alert if old)
#      detect if stations fail
#      perhaps get direct links for Soma
#   ability to CRUD a favorites playlist
#
import platform
PY3 = False
if platform.python_version().startswith('3'):
    PY3 = True
import csv
import sys
import textwrap
import time
import random
import os
import subprocess
import re
import math
from bs4 import BeautifulSoup
if PY3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen


from . import (
    VOL,
    CHAN_AGE_LIMIT,
    FAVS_DEFAULT,
    SOMA_PARSE_URL,
    COMPACT_TITLES,
    SOMA_STREAM_BASE_URL,
    SOMA_STREAM_END_URL
)
from .color import colors
from .banner import bannerize
from .album import gen_art


def buildFavsChannelFile(outfile):
    print("Building new channels file from default favs...")
    csv_chan_file = open(outfile, 'w')
    csv_chan_file.write(FAVS_DEFAULT)
    csv_chan_file.close()
    return


def buildSomaChannelFile(outfile):
    # Scrapes channels from somafm.com
    # original at https://gist.github.com/roamingryan/2343819
    # mod'ed by x0rion Feb 2014
    #   store name and desc seo; add img url
    #   handle specific bad streams
    page = urlopen(SOMA_PARSE_URL)
    soup = BeautifulSoup(page, "html.parser")
    chan_instances = soup.findAll('li', {"class": "cbshort"})

    print("Building new channels file from somafm.com...")
    if PY3:
        csv_chan_file = open(outfile, 'w', newline='')  # per doc to avoid TypeError: 'str' does not support the buffer interface
    else:
        csv_chan_file = open(outfile, 'w')
    chan_writer = csv.writer(csv_chan_file)

    for inst in chan_instances:
        stream_url_short = inst.find('a')['href'].replace("/", "")
        # for some reason, the following aren't at the expected URL
        # use: http://somafm.com/ + stream_url_short + /directstreamlinks.html and look under MP3 128kb for Direct Server: http://fqdn:port
        # consider doing this longer procedure for all channels
        # but for now, just hard code the ones that don't play well with the current code
        if stream_url_short == "airwaves":
            stream_url = "http://uwstream2.somafm.com:5400"
        elif stream_url_short == "earwaves":
            stream_url = "http://sfstream1.somafm.com:5100"
        else:
            stream_url  = SOMA_STREAM_BASE_URL + stream_url_short + SOMA_STREAM_END_URL
        stream_name = inst.find('a').find('img')['alt'].split(":")[0]
        stream_img  = SOMA_PARSE_URL + inst.find('a').find('img')['src']
        stream_desc = inst.find('p').string
        csv_row = [stream_url, stream_name, stream_desc, stream_img]
        chan_writer.writerow(csv_row)
        # os.system('cls' if os.name == 'nt' else 'clear')  # so ascii art gets a page each
        print("  %s, %s, %s" % (stream_url, stream_name, stream_desc))
        print(gen_art(stream_img, 80, 40))
    # add in some other manual ones
    # https://theclassicalstation.org/internet.shtml
    # http://audio-mp3.ibiblio.org:8000/wcpe.mp3 <- direct
    chan_writer.writerow(['http://www.ibiblio.org/wcpe/wcpe.pls', 'WCPE Classical', 'TheClassicalStation.org 24/7 classical music from Wake Forest, NC', 'http://theclassicalstation.org/images/wcpe_footer.jpg'])
    # goto http://www.wnrn.org/listen/ get link at "Load Stream" drop the final .m3u(or look at file at URL contents)
    chan_writer.writerow(['http://broadcast.wnrn.org:8000/wnrn.mp3', 'WNRN Cville', 'Independent Radio', 'http://www.wnrn.org/wp-content/themes/WNRN/images/logo2.gif'])
    csv_chan_file.close()
    return


def getStations(filename, mode):
    # if channel file older than X days rebuild
    try:
        chan_age = os.path.getctime(filename)
    except:
        chan_age = 0
    age_limit = time.time() - (60 * 60 * 24 * CHAN_AGE_LIMIT)
    if mode != "favs" and chan_age < age_limit:
        with colors("red"):
            print("The channels file(%s) is too old, moving to bck so new one can be built" % filename)
        os.system("mv " + filename + " " + filename + ".bck")

    # see if the channel file exists, catch other errors to
    # if it doesn't exist, try to rebuild it and carry on
    try:
        csv_fd = open(filename, 'r')
    except IOError as e:
        # The file doesn't exist, we need to build it!
        with colors("red"):
            print("The channels file(%s) doesn't exist; it needs to be rebuilt." % filename)
        if mode == "favs":
            buildFavsChannelFile(filename)
            # print("Error the favs file(%s) must be built manually; exiting."%filename)
            # sys.exit(1)
        elif mode == "soma":
            buildSomaChannelFile(filename)
        with colors("red"):
            print("Finished building channel file")  # ", please run again."
        # one last try to open the rebuilt file
        try:
            csv_fd = open(filename, 'r')
        except IOError as e:
            with colors("red"):
                print("Error (%s) opening channel, please run again." % e)
            sys.exit(1)

    chan_Csv = csv.reader(csv_fd)

    i = 0
    chans = {}
    for row in chan_Csv:
        # Skip rows that don't have three columns or rows that begin with  #
        if len(row) != 4 or row[0][0] == '#':
            continue
        for j in range(len(row)):
            row[j] = row[j].strip()
            # if j == 1 or j == 2: print("chans[" + str(i) + "][" + str(j) + "]: '" + row[j] + "'")
        chans[i] = row
        i += 1
    return chans


def printStations(chans, term_w, mode):
    keys = list(chans.keys())
    line_cnt = 0
    if len(keys) == 0:
        print("Exiting, empty channels file, delete it and rerun")
        sys.exit(1)
    keys.sort()
    # sets up infor to pretty print station data
    # for i in keys:
    # get left column width
    name_len = max([len(chans[a][1]) for a in chans]) + 1
    desc_len = term_w - name_len
    # the first line has the name, each subsequent line has whitespace up to column begin mark
    # desc_first_line_fmt = "{{0:{0}}}".format(desc_len)
    # desc_nth_line_fmt   = ' ' * (name_len + 4) + desc_first_line_fmt
    # print the stations
    for i in keys:
        # print " %i) %s"%(i,chans[i][1])
        with colors("yellow"):
            sys.stdout.write(" %2d" % i + " ) " + chans[i][1] + ' ' * (name_len - len(chans[i][1])))
        with colors("green"):
            # print("desc" + desc[i])
            lines = textwrap.wrap(chans[i][2], desc_len - 6)
            line_cnt += len(lines)
            print(lines[0])
            for line in lines[1:]:
                print(' ' * (name_len + 6) + line)
    # gen_line_cnt = line_cnt

    # print the hard coded access to the other station files pt 1
    if mode == "soma":
        with colors("yellow"):
            sys.stdout.write(" %2d" % len(keys) + " ) Favorites" + ' ' * (name_len - len("Favorites")))
        with colors("green"):
            lines = []
            lines = textwrap.wrap("Enter " + str(len(keys)) + " or 'f' to show favorite channels", desc_len - 6)
            line_cnt += len(lines)
            print(lines[0])
            for line in lines[1:]:
                print(' ' * (name_len + 6) + line)
    elif mode == "favs":
        with colors("yellow"):
            sys.stdout.write(" %2d" % len(keys) + " ) SomaFM" + ' ' * (name_len - len("SomaFM")))
        with colors("green"):
            lines = []
            lines = textwrap.wrap("Enter " + str(len(keys)) + " or 's' to show SomaFM channels", desc_len - 6)
            line_cnt += len(lines)
            print(lines[0])
            for line in lines[1:]:
                print(' ' * (name_len + 6) + line)
    # return(keys, gen_line_cnt)
    return(keys, line_cnt - 1)


def playStation(url, prefix, show_deets=1):
    # mpg123 command line mp3 stream player, does unbuffered output, so the subprocess...readline snip works
    # -C allows keyboard presses to send commands: space is pause/resume, q is quit, +/- control volume
    # -@ tells it to read (for stream/playlist info) filenames/URLs from within the file located at the next arg
    subp_cmd = ["mpg123", "-f", VOL, "-C", "-@", url]
    try:
        p = subprocess.Popen(subp_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except OSError as e:
        raise Exception('OSError %s when executing %s' % (e, subp_cmd))
    # "le='([^']*)';" -> Song title didn't parse(StreamTitle='Stone Soup Soldiers - Pharaoh's Tears';StreamUrl='http://SomaFM.com/suburbsofgoa/';)
    # Can't rely on no ' within title, so use ; eg "le='([^;]*)';"
    title_re = re.compile("le='([^;]*)';")

    delete_cnt = 0
    has_deeted = False
    has_titled = False
    for line in iter(p.stdout.readline, b''):
        out = bytes.decode(line)
        out = out.strip()
        if show_deets and not has_deeted and out[0:8] == "ICY-NAME":
            station_deets = out[10:]
            if station_deets[0:3] != "Def":  # bc it's kinda poser having so much 'defcon' all over your screen
                # print(">>> " +  station_deets)
                (term_w, term_h) = resetDimensions()
                lines = textwrap.wrap(station_deets, term_w - len(prefix))
                print(prefix + lines[0])
                for line in lines[1:]:
                    print(' ' * len(prefix) + line)
            has_deeted = True
        elif out[0:8] == "ICY-META":
            out = out[10:]
            # print(">>> " +  out)
            title_m = title_re.search(out)
            try:
                song_title = title_m.group(1)
            except:
                song_title = "Song title didn't parse(" + out + ")"
            # confine song title to single line to look good
            (term_w, term_h) = resetDimensions()
            if len(song_title) > (term_w - len(prefix)):
                song_title = song_title[0:(term_w - len(prefix))]
            # this will delete the last song, and reuse its line (so output only has one song title line)
            if COMPACT_TITLES:
                if has_titled:
                    # deleteChars(delete_cnt)
                    deletePromptChars(delete_cnt)
                else:
                    has_titled = True
                print(prefix + song_title)  # , end='')
                sys.stdout.flush()
                delete_cnt = len(song_title) + len(prefix)
            else:
                print(prefix + song_title)
    return delete_cnt


def deleteChars(num_chars):
    print('\b' * num_chars, end='')  # move cursor to beginning of text to remove
    print(' '  * num_chars, end='')  # overwrite/delete all previous text
    print('\b' * num_chars, end='')  # reset cursor for new text
    return


# \033[A moves cursor up 1 line; ' ' overwrites text, '\b' resets cursor to start of line
# if the term is narrow enough, you need to go up multiple lines
def deletePromptChars(num_chars):
    # determine lines to move up, there is at least 1 bc user pressed enter to give input
    # when they pressed Enter, the cursor went to beginning of the line
    (term_w, term_h) = resetDimensions()
    move_up = int(math.ceil(float(num_chars) / float(term_w)))
    print("\033[A" * move_up + ' ' * num_chars + '\b' * (num_chars), end='')
    return


def resetDimensions():
    try:
        # *nix get terminal/console width
        rows, columns = os.popen('stty size', 'r').read().split()
        width  = int(columns)
        height = int(rows)
        return (width, height)
        # print("term width: %d"% width)
    except:
        return (80, 40)
