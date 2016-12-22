from __future__ import print_function

from .station import (Favs, Soma)


class Radio(Object):
    def __init__(self):
        self._station = None
        self._stream = None
        self._stations = [
            Favs(),
            Soma()]

    def __str__(self):
        return 'Radio(station=%s,stream=%s)' % (self.station, self.stream)

    def __repr__(self):
        return str(self)

    @property
    def station(self):
        if self._station is None:
            return None
        return self._station.name

    @station.setter
    def station(self, station_name):
        if station_name != self.station:
            self.set(station)

    @property
    def stream(self):
        if self._stream is None:
            return None
        return self._stream.name

    @property
    def stations(self):
        return [st.name for st in self._stations]

    @property
    def song(self):
        if self._stream is None:
            return None
        return self._stream.song

    @property
    def is_playing(self):
        if self._stream is not None and self._stream._is_playing:
            return True
        return False

    def set(self, station_name, stream_name=None):
        if stream_name is None and station_name == self.station:
            return True
        if station_name == self.station and stream_name == self.stream:
            return True
        if self.is_playing:
            print('Error, stop stream before set')
            return False
        station = None
        objs = [st for st in self._stations if st.name == station_name]
        if len(objs) != 1:
            print('Error, no matching station')
            return False
        self._station = objs[0]
        self._stream = None
        if stream_name is None:
            return True
        streams = self._station.streams
        objs = [st for st in streams if st.name == stream_name]
        if len(objs) != 1:
            print('Error, no matching stream')
            return False
        self._stream = objs[0]
        return True

    def play(self, station_stream=None):
        if self.is_playing:
            print('Error, pause/stop stream before play')
            return (None, None)
        if station_stream is not None:
            station, stream = station_stream
            self.set(station, stream)
        if self.station is None or self.stream is None:
            print('Error, no station/stream set')
            return (None, None)
        # if not set, then carp
        self._stream.play()
        return (self.station, self.stream)

    def pause(self):
        self._stream.pause()
        return (self.station, self.stream)

    def stop(self):
        station_orig = self.station
        stream_orig = self.stream
        self._stream.stop()
        self._station = None
        self._stream = None
        return (station_orig, stream_orig)
