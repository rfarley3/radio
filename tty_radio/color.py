from __future__ import print_function
import sys


class colors:
    COLORS = {
        'purple': '\033[95m',
        'blue'  : '\033[94m',
        'green' : '\033[92m',
        'yellow': '\033[93m',
        'red'   : '\033[91m',
        'endc'  : '\033[0m',
    }

    def __init__(self, color, out=sys.stdout):
        self.color = color
        self.out = out

    def __enter__(self):
        self.out.write(self.COLORS[self.color])

    def __exit__(self, type, value, traceback):
        self.out.write(self.COLORS['endc'])
