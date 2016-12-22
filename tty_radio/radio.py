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
#   make Station class to hold:
#     web-scraper
#     file builder
#     main menu banner
#     menu "other stations"/mode switch items
#     custom deets filters
#
import platform
PY3 = False
if platform.python_version().startswith('3'):
    PY3 = True
import sys
import textwrap
import os
import subprocess
import re
import math
from io import StringIO
if PY3:
    get_input = input
else:
    get_input = raw_input


from . import (
    VOL,
    COMPACT_TITLES
)
from .color import colors
from .banner import bannerize
from .album import gen_art
from .stationfile import get_stations


def print_stations(chans, term_w, mode):
    keys = list(chans.keys())
    line_cnt = 0
    if len(keys) == 0:
        print("Exiting, empty channels file, delete it and rerun")
        sys.exit(1)
    keys.sort()
    # set up to pretty print station data
    # get left column width
    name_len = max([len(chans[a][1]) for a in chans]) + 1
    desc_len = term_w - name_len
    # the first line has the name
    # each subsequent line has whitespace up to column begin mark
    # desc_first_line_fmt = "{{0:{0}}}".format(desc_len)
    # desc_nth_line_fmt   = ' ' * (name_len + 4) + desc_first_line_fmt
    # print the stations
    for i in keys:
        # print " %i) %s"%(i,chans[i][1])
        with colors("yellow"):
            sys.stdout.write(
                " %2d" % i + " ) " + chans[i][1] +
                ' ' * (name_len - len(chans[i][1])))
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
            sys.stdout.write(
                " %2d" % len(keys) + " ) Favorites" +
                ' ' * (name_len - len("Favorites")))
        with colors("green"):
            lines = []
            lines = textwrap.wrap(
                "Enter " + str(len(keys)) +
                " or 'f' to show favorite channels",
                desc_len - 6)
            line_cnt += len(lines)
            print(lines[0])
            for line in lines[1:]:
                print(' ' * (name_len + 6) + line)
    elif mode == "favs":
        with colors("yellow"):
            sys.stdout.write(
                " %2d" % len(keys) + " ) SomaFM" +
                ' ' * (name_len - len("SomaFM")))
        with colors("green"):
            lines = []
            lines = textwrap.wrap(
                "Enter " + str(len(keys)) +
                " or 's' to show SomaFM channels",
                desc_len - 6)
            line_cnt += len(lines)
            print(lines[0])
            for line in lines[1:]:
                print(' ' * (name_len + 6) + line)
    # return(keys, gen_line_cnt)
    return(keys, line_cnt - 1)


def play_station(url, prefix, show_deets=1):
    # mpg123 command line mp3 stream player
    # does unbuffered output, so the subprocess...readline snip works
    # -C allows keyboard presses to send commands:
    #    space is pause/resume, q is quit, +/- control volume
    # -@ tells it to read (for stream/playlist info) filenames/URLs from url
    subp_cmd = ["mpg123", "-f", VOL, "-C", "-@", url]
    try:
        p = subprocess.Popen(
            subp_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    except OSError as e:
        raise Exception('OSError %s when executing %s' % (e, subp_cmd))
    # example to parse:
    # StreamTitle='Stone Soup Soldiers - Pharaoh's Tears';StreamUrl='http://SomaFM.com/suburbsofgoa/';)  # noqa
    title_re = re.compile("le='([^;]*)';")

    delete_cnt = 0
    has_deeted = False
    has_titled = False
    for line in iter(p.stdout.readline, b''):
        out = bytes.decode(line)
        out = out.strip()
        if show_deets and not has_deeted and out[0:8] == "ICY-NAME":
            station_deets = out[10:]
            # bc it's kinda poser having so much 'defcon' all over your screen
            if station_deets[0:3] != "Def":
                # print(">>> " +  station_deets)
                (term_w, term_h) = term_hw()
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
            except:  # TODO find actual exception
                song_title = "Song title didn't parse(" + out + ")"
            # confine song title to single line to look good
            (term_w, term_h) = term_hw()
            if len(song_title) > (term_w - len(prefix)):
                song_title = song_title[0:(term_w - len(prefix))]
            # this will delete the last song, and reuse its line
            # (so output only has one song title line)
            if COMPACT_TITLES:
                if has_titled:
                    # del_chars(delete_cnt)
                    del_prompt(delete_cnt)
                else:
                    has_titled = True
                print(prefix + song_title)  # , end='')
                sys.stdout.flush()
                delete_cnt = len(song_title) + len(prefix)
            else:
                print(prefix + song_title)
    return delete_cnt


def del_chars(num_chars):
    print('\b' * num_chars, end='')  # move cursor to beginning of text
    print(' '  * num_chars, end='')  # overwrite/delete all previous text
    print('\b' * num_chars, end='')  # reset cursor for new text
    return


# \033[A moves cursor up 1 line
# ' ' overwrites text
# '\b' resets cursor to start of line
# if the term is narrow enough, you need to go up multiple lines
def del_prompt(num_chars):
    # determine lines to move up, there is at least 1
    # bc user pressed enter to give input
    # when they pressed Enter, the cursor went to beginning of the line
    (term_w, term_h) = term_hw()
    move_up = int(math.ceil(float(num_chars) / float(term_w)))
    print("\033[A" * move_up + ' ' * num_chars + '\b' * (num_chars), end='')
    return


def term_hw():
    try:
        # *nix get terminal/console width
        rows, columns = os.popen('stty size', 'r').read().split()
    except:  # TODO get actual exeption
        return (80, 40)
    try:
        width  = int(columns)
        height = int(rows)
        return (width, height)
        # print("term width: %d"% width)
    except ValueError:
        return (80, 40)


def get_chan(mode, keys):
    # ######
    # get user input
    #     if next_mode != '':
    #     if next_mode == 'f':
    #         mode = 'favs'
    #     elif next_mode == 's':
    #         mode = 'soma'
    # next_mode = ''
    chan_num = None
    while chan_num not in keys:
        try:
            chan_num = get_input("\nPlease select a channel [q to quit]: ")
        except SyntaxError:
            continue
        if not chan_num:
            continue
        chan_num = str(chan_num).strip().lower()
        if len(chan_num) == 0:
            continue
        try:
            chan_num = int(chan_num)
            if chan_num < len(keys):
                return (chan_num, None)
            # the final row is not a stream, but a mode change
            if mode == 'favs' and chan_num == len(keys):
                return (None, 'soma')
            if mode == 'soma' and chan_num == len(keys):
                return (None, 'favs')
        except ValueError:
            pass
        ctrl_char = chan_num[0]
        if ctrl_char not in ['q', 'e', 's', 'f']:
            continue
        if (ctrl_char == 'q' or ctrl_char == 'e'):
            return (None, 'q')
        if ctrl_char == 'f':
            return (None, 'favs')
        if ctrl_char == 's':
            return (None, 'soma')
    # should never be here


def radio(mode):
    """list possible stations, read user input, and call player"""
    # when the player is exited, this loop happens again
    while(1):
        (term_w, term_h) = term_hw()
        chans = get_stations(mode)
        # ######
        # print stations
        title = "unknown"
        if mode == 'favs':
            title = "Radio Tuner"
        elif mode == 'soma':
            title = "SomaFM Tuner"
        with colors("red"):
            (banner, font) = bannerize(title, term_w)
            b_IO = StringIO(banner)
            b_h = len(b_IO.readlines())
            print(banner)  # , end='')
            b_h += 1
        (keys, line_cnt) = print_stations(chans, term_w, mode)
        loop_line_cnt = line_cnt + b_h + 2
        loop_line_cnt += 1
        if term_h > loop_line_cnt:
            print('\n' * (term_h - loop_line_cnt - 1))
        (chan_num, mode) = get_chan(mode, keys)
        if mode == 'q':
            return
        # no chan given, must have been a mode change, refresh list
        if chan_num is None:
            continue
        # ######
        # otherwise chan num specified, so call player
        display_album(chans[chan_num])
        display_banner(chans[chan_num])
        play_chan(chans[chan_num])


def display_album(chan):
    if chan[3] == "":
        return
    print("ASCII Printout of Station's Logo:")
    (term_w, term_h) = term_hw()
    art = gen_art(chan[3], term_w, term_h)
    if art is not None:
        print(art)


def display_banner(chan):
    unhappy = True
    while unhappy:
        (term_w, term_h) = term_hw()
        font = "unknown"
        with colors("yellow"):
            (banner, font) = bannerize(chan[1], term_w)
            b_IO = StringIO(banner)
            b_height = len(b_IO.readlines())
            if term_h > (b_height + 3):  # Playing, Station Name, Song Title
                print('\n' * (term_h - b_height - 2))
            print(banner, end='')
        with colors("purple"):
            prompt = "Press enter if you like banner"
            prompt += " (font: " + font + "), else any char then enter "
            try:
                happiness = get_input(prompt)
            except SyntaxError:
                happiness = ''
            del_prompt(len(prompt) + len(happiness))
            if len(happiness) == 0:
                unhappy = False
                msg1 = "Playing station, enjoy..."
                msg2 = "[pause/quit=q; vol=+/-]"
                if term_w > (len(msg1) + len(msg2)):
                    print(msg1 + ' ' + msg2)
                else:
                    print(msg1)
                    print(msg2)
            else:
                print("")  # empty line for pretty factor


def play_chan(chan):
    replay = True
    show_station_deets = True
    while replay:
        with colors("blue"):
            prefix = ">>> "
            delete_cnt = play_station(
                chan[0],
                prefix,
                show_station_deets)
            del_prompt(delete_cnt)
        with colors("purple"):
            # it will reach here anytime the player stops executing
            # (eg it has an exp, failure, etc)
            # but ideally it'll only reach here when the user presses
            # q (exiting the player) to "pause" it
            # you can't use mpg123's 'pause' cmd (spacebar) bc it'll
            # fail a minute or two after resuming (buffer errors)
            # for some reason it literally pauses the music,
            # buffering the stream until unpaused
            # behavior we want is to stop recving the stream
            # (like turning off a radio)
            prompt = "Paused. Press enter to Resume; q to quit. "
            reloop = get_input(prompt)
            # if the user inputs anything other than pressing
            # return/enter, then loop will quit
            if len(reloop) != 0:
                replay = False
            else:
                # for prettiness we don't want to reprint the station
                # details (name, etc) upon replaying within this loop
                show_station_deets = False
                # we also want to get rid of that prompt
                # to make room for the song name data again
                del_prompt(len(prompt) + len(prefix))
                sys.stdout.flush()
                # this play->pause->loop should never accumulate lines
                # in the output (except for the first Enter they press
                # at a prompt and even then, it's just an empty line)
