#!/usr/bin/env python
from __future__ import print_function
import sys
from getopt import getopt, GetoptError

from .radio import radio, term_hw
from .color import colors
from .banner import bannerize


USAGE = """\
Usage %s [-h|--help|-s|--soma]
\t-h or --help\tThis help message
\t-s or --soma\tRun in SomaFM mode

Python script for direct listening to online music streams.
Built-in compatibility with SomaFM.
Scrapes known stations' websites for stream urls and metadata.
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


def main(args=sys.argv[1:]):
    try:
        opts, args = getopt(args, "hs:", ["help", "soma"])
    except GetoptError:
        usage()
        return 2
    mode = "favs"
    for opt, arg in opts:
        if opt in("-s", "--soma"):
            mode = "soma"
        elif opt in("-h", "--help"):
            usage()
            return 0
        else:
            usage()
            return 1
    # set term title
    sys.stdout.write("\x1b]0;" + "~=radio tuner=~" + "\x07")
    try:
        radio(mode)
    except KeyboardInterrupt:
        pass
    # clear term title
    sys.stdout.write("\x1b]0;" + "\x07")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
