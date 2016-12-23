from __future__ import print_function
from threading import Thread
from time import sleep
from subprocess import (
    Popen,
    PIPE,
    STDOUT,
    check_output,
    CalledProcessError)
import re

from . import VOL


class Stream(object):
    def __init__(self, station, name, url, desc, art, reader):
        self.station = station
        self.name = name
        self.url = url
        self.desc = desc
        self.art = art
        self.station_reader = reader
        self.meta_name = None
        self.meta_song = None
        self._is_playing = False
        self._is_paused = False
        self._subproc = None

    def __str__(self):
        return ('Stream(station=%s,name=%s,url=%s,desc=\"%s\",art=%s)' %
                (self.station, self.name, self.url, self.desc, self.art))

    def __repr__(self):
        return str(self)

    @property
    def is_playing(self):
        return self._is_playing

    @property
    def is_paused(self):
        return self._is_paused

    def play(self):
        self.thread = Thread(
            target=mpg123,
            args=(self.url, self.get_subproc, self.reader))
        self.thread.daemon = True
        self.thread.start()
        while not mpg_running():
            sleep(0.5)
        self._is_playing = True
        self._is_paused = False

    def get_subproc(self, subproc):
        self._subproc = subproc

    def kill_subproc(self):
        self._subproc.terminate()

    def pause(self):
        self.kill_subproc()
        while mpg_running():
            sleep(0.5)
        self._is_paused = True
        # since we are killing the proc forget everything
        self.meta_song = None
        self.meta_name = None

    def stop(self):
        self.kill_subproc()
        while mpg_running():
            sleep(0.5)
        self._is_playing = False
        # since we are killing the proc forget everything
        self.meta_song = None
        self.meta_name = None

    def reader(self, inp):
        if (self.meta_name is None and
                len(inp) > 10 and
                inp[0:8] == "ICY-NAME"):
            self.meta_name = parse_name(inp[10:])
        if len(inp) > 10 and inp[0:8] == "ICY-META":
            song = parse_song(inp[10:])
            if song is not None and len(song) == 0:
                song = None
            self.meta_song = song
        self.station_reader(inp)


def mpg_running():
    # searching for mpg123 reveals an orphaned process in parens (mpg123)
    # so search for 'mpg123 '
    try:
        grep = check_output("ps | grep -v grep | grep 'mpg123 '", shell=True)
    except CalledProcessError:
        return False
    grep = grep.decode('ascii').strip()
    if len(grep) > 1:
        # print('%s' % grep)
        return True
    return False


def parse_name(station_deets):
    # TODO custom parsers inherited from station/stream
    # bc it's kinda poser having so much 'defcon' all over your screen
    if station_deets[0:3] == "Def":
        # print(">>> " +  station_deets)
        return ''
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


def mpg123(url, get_p, stream_reader):
    # mpg123 command line mp3 stream player
    # does unbuffered output, so the subprocess...readline snip works
    # -C allows keyboard presses to send commands:
    #    space is pause/resume, q is quit, +/- control volume
    # -@ tells it to read (for stream/playlist info) filenames/URLs from url
    subp_cmd = ["mpg123", "-f", VOL, "-@", url]
    try:
        p = Popen(subp_cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    except OSError as e:
        raise Exception('OSError %s when executing %s' % (e, subp_cmd))
    get_p(p)
    for line in iter(p.stdout.readline, b''):
        out = bytes.decode(line)
        out = out.strip()
        stream_reader(out)
