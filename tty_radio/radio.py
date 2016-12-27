from __future__ import print_function

from .station import Favs, Soma


class Radio(object):
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
            self.set(station_name)

    def station_obj(self, station):
        possibles = [st for st in self._stations if station == st.name]
        if len(possibles) != 1:
            return None
        return possibles[0]

    @property
    def stream(self):
        if self._stream is None:
            return None
        return self._stream.name

    @property
    def stations(self):
        # return [st.name for st in self._stations]
        stations = []
        for st in self._stations:
            streams = []
            for stm in st.streams:
                streams.append(stm.name)
            stations.append({
                'name': st.name,
                'ui_name': st.ui_name,
                'streams': streams})
        return stations

    @property
    def song(self):
        if self._stream is None:
            return None
        song = self._stream.meta_song
        if song is None:
            return 'No Title in Metadata'
            # return self._stream.meta_name
        return song

    @property
    def is_playing(self):
        if self._stream is not None and self._stream.is_playing:
            return True
        return False

    @property
    def is_paused(self):
        if self._stream is not None and self._stream.is_paused:
            return True
        return False

    def set(self, station_name, stream_name=None):
        if stream_name is None and station_name == self.station:
            # print('Ignoring, station is same for set')
            return True
        if station_name == self.station and stream_name == self.stream:
            # print('Ignoring, station and stream are same for set')
            return True
        if self.is_playing:
            # print('Error, stop stream before set')
            return False
        obj = self.station_obj(station_name)
        if obj is None:
            # print('Error, no matching station')
            return False
        self._station = obj
        self._stream = None
        if stream_name is None:
            return True
        obj = self._station.stream_obj(stream_name)
        if obj is None:
            # print('Error, no matching stream')
            return False
        self._stream = obj
        return True

    def play(self, station=None, stream=None):
        if self.is_playing and not self.is_paused:
            # print('Error, stop/pause stream before play')
            return (None, None)
        if station is not None and stream is not None:
            self.set(station, stream)
        if self.station is None or self.stream is None:
            # print('Error, no station/stream set')
            return (None, None)
        # if not set, then carp
        self._stream.play()
        return (self.station, self.stream)

    def pause(self):
        self._stream.pause()
        return (self.station, self.stream)

    def stop(self):
        self._stream.stop()
        return (self.station, self.stream)
