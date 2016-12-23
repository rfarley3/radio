from __future__ import print_function
import json
import requests
from bottle import run, route, post, request

from . import DEBUG
from .radio import Radio


PORT = 7887


def load_request(possible_keys):
    """Given list of possible keys, return any matching post data"""
    pdata = json.load(request.body)
    for k in possible_keys:
        if k not in pdata:
            pdata[k] = None
    return pdata


class ApiConnError(BaseException):
    pass


class Server(object):
    def __init__(self, addr=None, radio=None):
        self.host = '127.0.0.1'
        self.port = PORT
        if addr is not None:
            (self.host, self.port) = addr
        self.radio = radio
        if radio is None:
            self.radio = Radio()

    def run(self):
        route('/api/v1/')(self.index)
        route('/api/v1/status')(self.status)
        route('/api/v1/stations')(self.stations)
        route('/api/v1/streams')(self.streams)
        route('/api/v1/<station>/streams')(self.streams)
        route('/api/v1/<station>')(self.station)
        post('/api/v1/<station>')(self.set)
        route('/api/v1/<station>/<stream>')(self.stream)
        post('/api/v1/<station>/<stream>')(self.set)
        route('/api/v1/play')(self.play)
        route('/api/v1/pause')(self.pause)
        route('/api/v1/stop')(self.stop)
        run(host=self.host, port=self.port, debug=DEBUG)

    # TODO load a js frontend
    def index(self):
        success = True
        resp = 'TTY Radio API is running'
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def status(self):
        success = True
        resp = {
            'currently_streaming': self.radio.is_playing,
            'station': self.radio.station,
            'stream': self.radio.stream,
            'song': self.radio.song
        }
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def station(self, station):
        found_st = self.radio.station_obj(station)
        success = False
        name = None
        ui_b = None
        file = None
        rebuild = None
        if found_st is not None:
            success = True
            name = found_st.name
            ui_b = found_st.ui_banner
            file = found_st.file
            rebuild = found_st.rebuild
        resp = {
            'name': name,
            'ui_banner': ui_b,
            'file': file,
            'rebuild': rebuild,
        }
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def stream(self, station, stream):
        found_stn = self.radio.station_obj(station)
        if found_stn is None:
            # TODO resp
            return json.dumps({'success': False}) + '\n'
        fount_stm = found_stn.stream_obj(stream)
        if fount_stm is None:
            # TODO resp
            return json.dumps({'success': False}) + '\n'
        success = True
        resp = {
            'station': fount_stm.station,
            'name': fount_stm.name,
            'url': fount_stm.url,
            'desc': fount_stm.desc,
            'art': fount_stm.art,
            'meta_name': fount_stm.None,
            'meta_song': fount_stm.None,
            'is_playing': fount_stm.False,
            'is_paused': fount_stm.False,
        }
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def stations(self):
        success = True
        resp = {
            'stations': self.radio.stations
        }
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def streams(self, station=None):
        streams = []
        for st in self.radio._stations:
            if station is None or st.name == station:
                streams_str = [str(s) for s in st.streams]
                streams.extend(streams_str)
        success = True
        if (station is not None and
                station not in [st.name for st in self.radio._stations]):
            success = False
        resp = {
            'streams': streams
        }
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def set(self, station, stream=None):
        success = self.radio.set(station, stream)
        resp = 'Setting active stream to %s %s' % (station, stream)
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def play(self):
        (station, stream) = self.radio.play()
        success = True
        resp = 'Playing %s %s' % (station, stream)
        if station is None or stream is None:
            success = False
            resp = 'Failure: set first, or stop any currently playing'
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def pause(self):
        (station, stream) = self.radio.pause()
        success = True
        resp = 'Pausing %s %s' % (station, stream)
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def stop(self):
        (station, stream) = self.radio.stop()
        success = True
        resp = 'Stopping %s %s' % (station, stream)
        return json.dumps({'success': success, 'resp': resp}) + '\n'


class Client(object):
    """Importable Python object to wrap REST calls"""
    def __init__(self, addr=None):
        self.host = '127.0.0.1'
        self.port = PORT
        if addr is not None:
            (self.host, self.port) = addr

    def url(self, endpoint):
        return 'http://%s:%s/api/v1/%s' % (self.host, self.port, endpoint)

    def get(self, endpoint):
        try:
            resp = requests.get(self.url(endpoint))
        except requests.ConnectionError as e:
            raise ApiConnError(e)
        try:
            resp_val = json.loads(resp.text)
        except ValueError as e:
            # remote server fails and kills connection or returns nothing
            raise ApiConnError(e)
        return resp_val

    def post(self, endpoint, data={}):
        try:
            resp = requests.post(self.url(endpoint), data=json.dumps(data))
        except requests.ConnectionError as e:
            raise ApiConnError(e)
        try:
            resp_val = json.loads(resp.text)
        except ValueError as e:
            # remote server fails and kills connection or returns nothing
            raise ApiConnError(e)
        return resp_val

    def status(self, station=None):
        rjson = self.get('status')
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def station(self):
        rjson = self.get('station')
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def stations(self):
        rjson = self.get('stations')
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return []
        return rjson['resp']['stations']

    def stream(self, station, stream):
        rjson = self.get('%s/%s' % (station, stream))
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def streams(self, station=None):
        if station is None:
            rjson = self.get('streams')
        else:
            rjson = self.get('%s/streams' % station)
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return []
        return rjson['resp']['streams']

    def set(self, station, stream):
        rjson = self.post('%s/%s' % (station, stream))
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True

    def play(self, station_stream=None):
        if station_stream is not None:
            station, stream = station_stream
            self.set(station, stream)
            # TODO error check
        rjson = self.get('play')
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True

    def pause(self):
        rjson = self.get('pause')
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True

    def stop(self):
        rjson = self.get('stop')
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True
