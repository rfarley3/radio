from __future__ import print_function
from threading import Thread
import subprocess
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
        self._wpipe = None

    def __str__(self):
        return ('Stream(station=%s,name=%s,url=%s,desc=%s,art=%s)' %
                (self.station, self.name, self.url, self.desc, self.art))

    def __repr__(self):
        return str(self)

    @property
    def is_playing(self):
        return self._is_playing

    def play(self):
        self._is_playing = True
        self._is_paused = False
        self.thread = Thread(
            target=mpg123,
            args=(self.url, self.get_wpipe, self.reader))
        self.thread.daemon = True
        self.thread.start()

    def get_wpipe(self, wpipe):
        self._wpipe = wpipe

    def writer(self, data):
        self._wpipe.stdin.write(data)

    def pause(self):
        self.writer('q'.encode('ascii'))
        self._is_paused = True

    def stop(self):
        self.writer('q'.encode('ascii'))
        self._is_playing = False

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


def mpg123(url, get_p, stream_reader):
    # mpg123 command line mp3 stream player
    # does unbuffered output, so the subprocess...readline snip works
    # -C allows keyboard presses to send commands:
    #    space is pause/resume, q is quit, +/- control volume
    # -@ tells it to read (for stream/playlist info) filenames/URLs from url
    subp_cmd = ["mpg123", "-f", VOL, "-C", "-@", url]
    try:
        p = subprocess.Popen(
            subp_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
    except OSError as e:
        raise Exception('OSError %s when executing %s' % (e, subp_cmd))
    get_p(p)
    for line in iter(p.stdout.readline, b''):
        out = bytes.decode(line)
        out = out.strip()
        stream_reader(out)
