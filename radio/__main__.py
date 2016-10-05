#!/usr/bin/env python
from __future__ import print_function
import sys
import platform
PY3 = False
if platform.python_version().startswith('3'):
    PY3 = True
import getopt
from os.path import expanduser
from io import StringIO

if PY3:
    get_input = input
else:
    get_input = raw_input

from .radio import (
    BANNER,
    FAVS_CHAN_FILENAME,
    SOMA_CHAN_FILENAME,
    resetDimensions,
    asciiArtText,
    colors,
    getStations,
    printStations,
    printAsciiArt,
    playStation,
    deletePromptChars)


USAGE = """Usage %s [-h|--help|-s|--soma|-d|--difm] [--proxy <url>]
\t-h or --help\tThis help message
\t-s or --soma\tRun in SomaFM mode
\t-d or --difm\tRun in Di.FM mode
\t-x or --proxy\tSet the proxy server

Python script for direct listening to online music streams.
Built-in compatibility with SomaFM and Di.FM.
Scrapes respective websites for urls and metadata.
Puts it all into a nice list for you to select from, then calls mpg123.
And let's not forget the pretty ASCII art...
"""


def usage():
    print(USAGE % sys.argv[0])
    (term_w, term_h) = resetDimensions()
    (banner, font) = asciiArtText("ASCII Art, FTW!", term_w)
    with colors("purple"):  # or blue, green, yellow, red
        print(banner)
    print("Font: " + font)
    sys.exit(0)


def main():
    sys.stdout.write("\x1b]0;" + BANNER + "\x07")
    # ######
    # handle command line args
    mode = "favs"
    chan_filename = FAVS_CHAN_FILENAME
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hsdx:", ["help", "soma", "difm", "proxy="])
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        # print("here")
        if opt in("-s", "--soma"):
            mode = "soma"
            chan_filename = SOMA_CHAN_FILENAME
        elif opt in("-d", "--difm"):
            mode = "difm"
            chan_filename = DIFM_CHAN_FILENAME
        elif opt in("-x", "--proxy"):
            PROXY = arg
            # print("Using proxy " + PROXY)
        elif opt in("-h", "--help"):
            usage()
        else:
            usage()

    # we want the home directory to find/store the channels file
    home = expanduser("~")

    # ######
    # get the station list
    chans = getStations(home + "/" + chan_filename, mode)

    # ######
    # main loop
    # shows possible stations, takes in user input, and calls player
    # when the player is exited, this loop happens again
    switch_mode = False
    while(1):
        (term_w, term_h) = resetDimensions()
        if switch_mode != '':
            if switch_mode == 'f':
                mode = "favs"
                chan_filename = FAVS_CHAN_FILENAME
            elif switch_mode == 's':
                mode = "soma"
                chan_filename = SOMA_CHAN_FILENAME
            elif switch_mode == 'd':
                mode = "difm"
                chan_filename = DIFM_CHAN_FILENAME
            chans = getStations(home + "/" + chan_filename, mode)
            switch_mode = False

        # ######
        # print stations
        title = "unknown"
        if mode == "favs":
            title = "Radio Tuner"
        elif mode == "soma":
            title = "SomaFM Tuner"
        elif mode == "difm":
            title = "Di.FM Tuner"
        with colors("red"):
            (banner, font) = asciiArtText(title, term_w)
            b_IO = StringIO(banner)
            b_h = len(b_IO.readlines())
            print(banner)  # , end='')
            b_h += 1
        (keys, line_cnt) = printStations(chans, term_w, mode)
        loop_line_cnt = line_cnt + b_h + 2
        loop_line_cnt += 1
        if term_h > loop_line_cnt:
            print('\n' * (term_h - loop_line_cnt - 1))

        # ######
        # get user input
        switch_mode = ''
        chan_num = None
        while chan_num not in keys:
            try:
                chan_num = get_input("\nPlease select a channel [q to quit]: ")
            except SyntaxError:
                chan_num = ''
            except KeyboardInterrupt:
                return 0
            chan_num = str(chan_num)
            if len(chan_num) > 0:
                chan_num = chan_num.lower()
                ctrl_char = chan_num[0]
                if(ctrl_char == 'q' or ctrl_char == 'e'):
                    sys.stdout.write("\x1b]0;" + "\x07")
                    return 0
                # they type in some variant of either difm or somafm or favs
                if ctrl_char == mode[0]:
                    break
                elif mode == "favs" and(ctrl_char == 's' or ctrl_char == 'd'):
                    switch_mode = ctrl_char
                    break
                elif mode == "soma" and(ctrl_char == 'f' or ctrl_char == 'd'):
                    switch_mode = ctrl_char
                    break
                elif mode == "difm" and(ctrl_char == 'f' or ctrl_char == 's'):
                    switch_mode = ctrl_char
                    break
            try:
                chan_num = int(chan_num)
                if mode == "favs":
                    if chan_num == len(keys):
                        switch_mode = 's'
                        break
                    elif chan_num == (len(keys) + 1):
                        switch_mode = 'd'
                        break
                if mode == "soma":
                    if chan_num == len(keys):
                        switch_mode = 'f'
                        break
                    elif chan_num == (len(keys) + 1):
                        switch_mode = 'd'
                        break
                if mode == "difm":
                    if chan_num == len(keys):
                        switch_mode = 'f'
                        break
                    elif chan_num == (len(keys) + 1):
                        switch_mode = 's'
                        break
            except:
                pass

        if switch_mode != '' or (mode == "favs" and ctrl_char == 'f') or(mode == "soma" and ctrl_char == 's') or (mode == "difm" and ctrl_char == 'd'):
            continue

        (term_w, term_h) = resetDimensions()

        # ######
        # call player
        if chans[chan_num][3] != "":
            print("ASCII Printout of Station's Logo:")
            printAsciiArt(chans[chan_num][3], term_w, term_h)
        unhappy = True
        while unhappy:
            (term_w, term_h) = resetDimensions()
            font = "unknown"
            with colors("yellow"):
                (banner, font) = asciiArtText(chans[chan_num][1], term_w)
                b_IO = StringIO(banner)
                b_height = len(b_IO.readlines())
                if term_h > (b_height + 3):  # Playing, Station Name, Song Title
                    print('\n' * (term_h - b_height - 2))
                print(banner, end='')
            with colors("purple"):
                prompt = "Press enter if you like banner (font: " + font + "), else any char then enter "
                try:
                    happiness = get_input(prompt)
                except SyntaxError:
                    happiness = ''
                deletePromptChars(len(prompt) + len(happiness))
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
        replay = True
        show_station_deets = True
        while replay:
            with colors("blue"):
                prefix = ">>> "
                delete_cnt = playStation(chans[chan_num][0], prefix, show_station_deets)
                deletePromptChars(delete_cnt)
            with colors("purple"):
                # it will reach here anytime the player stops executing (eg it has an exp, failure, etc)
                # but ideally it'll only reach here when the user presses q (exiting the player) to "pause" it
                # you can't use mpg123's 'pause' cmd (spacebar) bc it'll fail a minute or two after resuming (buffer errors)
                # for some reason it literally pauses the music, buffering the stream until unpaused
                # behavior we want is to stop recving the stream (like turing off a radio)
                prompt = "Paused. Press enter to Resume; q to quit. "
                reloop = get_input(prompt)
                # if the user inputs anything other than pressing return/enter, then loop will quit
                if len(reloop) != 0:
                    replay = False
                else:
                    # for prettiness we don't want to reprint the station details (name, etc) upon replaying within this loop
                    show_station_deets = False
                    # we also want to get rid of that prompt to make room for the song name data again
                    deletePromptChars(len(prompt) + len(prefix))
                    sys.stdout.flush()
                    # this play->pause->loop should never accumulate lines in the output (except for the first Enter they press at a prompt and even then it's just an empty line)
            # end with
        # end while { show list, play selected station, wait for player to exit }
    return 0


if __name__ == "__main__":
    sys.exit(main())
