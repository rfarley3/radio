from __future__ import print_function
import json
import requests
from bottle import run, route, post, request

from . import DEBUG


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

    def run(self):
        route('/api/v1/')(self.index)
        route('/api/v1/status')(self.status)
        route('/api/v1/stations')(self.stations)
        route('/api/v1/streams')(self.streams)
        route('/api/v1/<station>/streams')(self.streams)
        post('/api/v1/<station>')(self.set)
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

    def stations(self):
        success = True
        resp = {
            'stations': [st.name for st in self.radio.stations]
        }
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def streams(self, station=None):
        streams = []
        for st in self.radio.stations:
            if station is None or st.name == station:
                streams.extend(st.streams)
        success = True
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

    def status(self):
        rjson = self.get('status')
        if not rjson['success']:
            print('API request failure: %s' % rjson)
            return {}
        return rjson['resp']

    def stations(self):
        rjson = self.get('stations')
        if not rjson['success']:
            print('API request failure: %s' % rjson)
            return []
        return rjson['resp']['stations']

    def streams(self, station=None):
        if station is None:
            rjson = self.get('streams')
        else:
            rjson = self.get('%s/streams' % station)
        if not rjson['success']:
            print('API request failure: %s' % rjson)
            return []
        return rjson['resp']['streams']

    def set(self, station, stream):
        rjson = self.post('%s/%s' % (station, stream))
        if not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True

    def play(self, station_stream=None):
        if station_stream is not None:
            station, stream = station_stream
            self.set(station, stream)
            # TODO error check
        rjson = self.get('play')
        if not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True

    def pause(self):
        rjson = self.get('pause')
        if not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True

    def stop(self):
        rjson = self.get('stop')
        if not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True
