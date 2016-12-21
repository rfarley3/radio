#!/usr/bin/env python
from __future__ import print_function
import sys
import getopt
from os.path import expanduser

from . import (
    BANNER,
    FAVS_CHAN_FILENAME,  # TODO remove import
    SOMA_CHAN_FILENAME,  # TODO remove import
)
from .radio import (
    do_ui,
    term_hw)
from .color import colors
from .banner import bannerize


USAGE = """Usage %s [-h|--help|-s|--soma]
\t-h or --help\tThis help message
\t-s or --soma\tRun in SomaFM mode

Python script for direct listening to online music streams.
Built-in compatibility with SomaFM.
Scrapes respective websites for urls and metadata.
Puts it all into a nice list for you to select from, then calls mpg123.
And let's not forget the pretty ASCII art...
"""


def usage():
    print(USAGE % sys.argv[0])
    (term_w, term_h) = term_hw()
    (banner, font) = bannerize("ASCII Art, FTW!", term_w)
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
        opts, args = getopt.getopt(sys.argv[1:], "hs:", ["help", "soma"])
    except getopt.GetoptError:
        usage()
    for opt, arg in opts:
        # print("here")
        if opt in("-s", "--soma"):
            mode = "soma"
            chan_filename = SOMA_CHAN_FILENAME
        elif opt in("-h", "--help"):
            usage()
        else:
            usage()
    # we want the home directory to find/store the channels file
    home = expanduser("~")
    do_ui(mode, home, chan_filename)
    return 0


if __name__ == "__main__":
    sys.exit(main())
