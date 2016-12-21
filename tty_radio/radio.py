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
import sys
import textwrap
import os
import subprocess
import re
import math

from . import (
    VOL,
    COMPACT_TITLES
)
from .color import colors
# from .stationfile import


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
