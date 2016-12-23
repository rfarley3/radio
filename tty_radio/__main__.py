#!/usr/bin/env python
from __future__ import print_function
import sys
from time import sleep
from threading import Thread
from getopt import getopt, GetoptError

from .ui import ui
from .api import Server
from .ui import term_wh
from .color import colors
from .banner import bannerize



USAGE = """\
Usage %s [-h|--help]
\t-h or --help\tThis help message

To use Terminal UI:
  Select station at prompt, by entering number found in left column
  Enjoy

About:
  RESTful service for listening to online music streams.
  Built-in compatibility with SomaFM.
  Add custom station scrapers or manually add to ~/.tty_radio-favs.csv.
  Organizes your stations into a list to select from, then calls mpg123.
  (You can use any player that doesn't buffer stdout.)
  And let's not forget the pretty ASCII art...
"""


def usage():
    print(USAGE % sys.argv[0])
    (term_w, term_h) = term_wh()
    (banner, font) = bannerize('ASCII Art, FTW!', term_w)
    with colors('purple'):  # or blue, green, yellow, red
        print(banner)
    print('Font: ' + font)


# TODO add entry point to scrape/CRUD station files
# TODO host option to opts
def main(do_ui, args=sys.argv[1:]):
    try:
        opts, args = getopt(args, 'h', ['help'])
    except GetoptError:
        usage()
        return 2
    for opt, arg in opts:
        if opt in ['-h', '--help']:
            usage()
            return 0
        else:
            usage()
            return 1
    s = Server()
    if not do_ui:
        s.run()
        return 0
    st = Thread(target=s.run)
    st.daemon = True
    st.start()
    sleep(0.5)
    ui()
    # TODO clean up thread, mpg123
    return 0


def main_ui():
    return main(True)


def main_serv():
    return main(False)


if __name__ == "__main__":
    sys.exit(main_serv())
