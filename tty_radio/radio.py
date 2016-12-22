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
#      possibly move web-scraper to CLarg and only on demand (but alert if old)
#      detect if stations fail
#      perhaps get direct links for Soma
#   ability to CRUD a favorites playlist
#   make Station class to hold:
#     web-scraper
#     file builder
#     main menu banner
#     menu "other stations"/station switch items
#     custom deets filters
#   custom colors for stations/streams
#   use pr_blk in print_streams
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
from .stationfile import get_station_streams


def print_streams(streams, term_w, station):
    keys = list(streams.keys())
    line_cnt = 0
    if len(keys) == 0:
        print("Exiting, empty station file, delete it and rerun")
        sys.exit(1)
    keys.sort()
    # set up to pretty print station data
    # get left column width
    name_len = max([len(streams[a][1]) for a in streams]) + 1
    desc_len = term_w - name_len
    # the first line has the name
    # each subsequent line has whitespace up to column begin mark
    # desc_first_line_fmt = "{{0:{0}}}".format(desc_len)
    # desc_nth_line_fmt   = ' ' * (name_len + 4) + desc_first_line_fmt
    # print the stations
    for i in keys:
        # print " %i) %s"%(i,streams[i][1])
        with colors("yellow"):
            sys.stdout.write(
                " %2d" % i + " ) " + streams[i][1] +
                ' ' * (name_len - len(streams[i][1])))
        with colors("green"):
            # print("desc" + desc[i])
            lines = textwrap.wrap(streams[i][2], desc_len - 6)
            line_cnt += len(lines)
            print(lines[0])
            for line in lines[1:]:
                print(' ' * (name_len + 6) + line)

    # print the hard coded access to the other station files pt 1
    if station == "soma":
        with colors("yellow"):
            sys.stdout.write(
                " %2d" % len(keys) + " ) Favorites" +
                ' ' * (name_len - len("Favorites")))
        with colors("green"):
            lines = []
            lines = textwrap.wrap(
                "Enter " + str(len(keys)) +
                " or 'f' to show favorite streams",
                desc_len - 6)
            line_cnt += len(lines)
            print(lines[0])
            for line in lines[1:]:
                print(' ' * (name_len + 6) + line)
    elif station == "favs":
        with colors("yellow"):
            sys.stdout.write(
                " %2d" % len(keys) + " ) SomaFM" +
                ' ' * (name_len - len("SomaFM")))
        with colors("green"):
            lines = []
            lines = textwrap.wrap(
                "Enter " + str(len(keys)) +
                " or 's' to show SomaFM streams",
                desc_len - 6)
            line_cnt += len(lines)
            print(lines[0])
            for line in lines[1:]:
                print(' ' * (name_len + 6) + line)
    return (keys, line_cnt - 1)


def do_mpg123(url, prefix, show_deets=1):
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
    delete_cnt = 0
    has_deeted = False
    has_titled = False
    for line in iter(p.stdout.readline, b''):
        out = bytes.decode(line)
        out = out.strip()
        if show_deets and not has_deeted and out[0:8] == "ICY-NAME":
            parsed = parse_name(out[10:])
            if parsed is not None:
                pr_blk(parsed, prefix)
            has_deeted = True
        elif out[0:8] == "ICY-META":
            parsed = parse_song(out[10:])
            # confine song title to single line to look good
            song_title = pr_blk(parsed, prefix, chomp=True, do_pr=False)
            # this will delete the last song, and reuse its line
            # (so output only has one song title line)
            if COMPACT_TITLES:
                if has_titled:
                    del_prompt(delete_cnt)
                else:
                    has_titled = True
            print(song_title)
            sys.stdout.flush()
            delete_cnt = len(song_title)
    return delete_cnt


def parse_name(station_deets):
    # bc it's kinda poser having so much 'defcon' all over your screen
    if station_deets[0:3] == "Def":
        # print(">>> " +  station_deets)
        return None
    return station_deets


def parse_song(metadata):
    # example to parse:
    # StreamTitle='Stone Soup Soldiers - Pharaoh's Tears';StreamUrl='http://SomaFM.com/suburbsofgoa/';)  # noqa
    title_re = re.compile("le='([^;]*)';")
    # print(">>> " +  out)
    title_m = title_re.search(metadata)
    title = "Song title didn't parse(" + metadata + ")"
    try:
        title = title_m.group(1)
    except:  # TODO find actual exception
        return title
    title = re.sub(r'\s{2,}-', ' -', title)
    return title


def pr_blk(buf, prefix='', prefix_len=None, chomp=False, do_pr=True):
    if buf is None or buf == '':
        if not do_pr:
            return ''
        return
    if prefix_len is None:
        prefix_len = len(prefix)
    (term_w, term_h) = term_hw()
    if chomp and len(buf) > (term_w - prefix_len):
        msg = prefix + buf[0:(term_w - prefix_len)]
        if not do_pr:
            return msg
        print(msg)
    lines = textwrap.wrap(buf, term_w - prefix_len)
    msg = prefix + lines[0]
    for line in lines[1:]:
        msg += ' ' * prefix_len + line
    if not do_pr:
        return msg
    print(msg)


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
    (w, h) = (80, 40)
    try:
        # *nix get terminal/console width
        rows, columns = os.popen('stty size', 'r').read().split()
    except ValueError:
        return (w, h)
    try:
        w = int(columns)
        h = int(rows)
    except ValueError:
        pass
    # print("term width: %d"% width)
    return (w, h)


def read_input():
    try:
        stream_num = get_input("\nPlease select a stream [q to quit]: ")
    except SyntaxError:
        return
    if not stream_num:
        return
    stream_num = str(stream_num).strip().lower()
    if len(stream_num) == 0:
        return
    return stream_num


def try_as_int(stream_num, station, max_val):
    try:
        stream_num = int(stream_num)
    except ValueError:
        return None
    # keys[len] is the other station
    if stream_num < 0 or stream_num > max_val:
        return None
    # the final row is not a stream, but a station change
    if stream_num == max_val:
        if station == 'favs':
            return (None, 'soma')
        # else station == 'soma'
        return (None, 'favs')
    return (stream_num, station)


def get_choice(station, keys):
    """Get user choice of stream to play, or station to change"""
    stream_num = None
    while stream_num not in keys:
        stream_num = read_input()
        if stream_num is None:
            continue
        ctrl_char = stream_num[0]
        if ctrl_char not in ['q', 'e', 's', 'f']:
            retval = try_as_int(stream_num, station, len(keys))
            if retval is None:
                continue
            else:
                return retval
        if (ctrl_char == 'q' or ctrl_char == 'e'):
            return (None, 'q')
        if ctrl_char == 'f':
            return (None, 'favs')
        if ctrl_char == 's':
            return (None, 'soma')
    # should never be here


def radio(station):
    """list possible stations, read user input, and call player"""
    # when the player is exited, this loop happens again
    while(1):
        (term_w, term_h) = term_hw()
        streams = get_station_streams(station)
        # ######
        # print stations
        title = "Radio Tuner"
        if station == 'soma':
            title = "SomaFM Tuner"
        with colors("red"):
            (banner, font) = bannerize(title, term_w)
            b_IO = StringIO(banner)
            b_h = len(b_IO.readlines())
            print(banner)  # , end='')
            b_h += 1
        (keys, line_cnt) = print_streams(streams, term_w, station)
        loop_line_cnt = line_cnt + b_h + 2
        loop_line_cnt += 1
        if term_h > loop_line_cnt:
            print('\n' * (term_h - loop_line_cnt - 1))
        (stream_num, station) = get_choice(station, keys)
        if station == 'q':
            return
        # no stream given, must have been a station change, refresh list
        if stream_num is None:
            continue
        # ######
        # otherwise stream num specified, so call player
        display_album(streams[stream_num])
        display_banner(streams[stream_num])
        play_stream(streams[stream_num])


def display_album(stream):
    if stream[3] == "":
        return
    print("ASCII Printout of Station's Logo:")
    (term_w, term_h) = term_hw()
    art = gen_art(stream[3], term_w, term_h)
    if art is not None:
        print(art)


def display_banner(stream):
    unhappy = True
    while unhappy:
        (term_w, term_h) = term_hw()
        font = "unknown"
        with colors("yellow"):
            (banner, font) = bannerize(stream[1], term_w)
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
                msg1 = "Playing stream, enjoy..."
                msg2 = "[pause/quit=q; vol=+/-]"
                if term_w > (len(msg1) + len(msg2)):
                    print(msg1 + ' ' + msg2)
                else:
                    print(msg1)
                    print(msg2)
            else:
                print("")  # empty line for pretty factor


def play_stream(stream):
    replay = True
    show_station_deets = True
    while replay:
        with colors("blue"):
            prefix = ">>> "
            delete_cnt = do_mpg123(
                stream[0],
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
