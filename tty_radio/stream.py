from __future__ import print_function


class Stream(object):
    def __init__(self, station, name, url, desc, art):
        self.station = station
        self.name = name
        self.url = url
        self.desc = desc
        self.art = art
        self.song = None
        self._is_playing = False
        self._is_paused = False

    def __str__(self):
        return 'Station(name=%s,file=%s)' % (self.name, self.file)

    def __repr__(self):
        return str(self)

    def play(self):
        pass

    def pause(self):
        pass

    def stop(self):
        pass
