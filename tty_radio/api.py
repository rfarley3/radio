from __future__ import print_function
import platform
PY3 = False
if platform.python_version().startswith('3'):
    PY3 = True
import json
import requests
import os
from bottle import (
    run,
    route, post, put, delete,
    request,  # response, hook
)
if PY3:
    from urllib.parse import unquote
else:
    from urllib import unquote

from .radio import Radio


BOTTLE_DEBUG = False
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
        # UI Functions
        route('/')(self.frontend)
        # route('/', method='OPTIONS')(self.options_handler)
        # route('/<path:path>', method='OPTIONS')(self.options_handler)
        # hook('after_request')(self.enable_cors)

        # API functions
        # v1
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

        # API functions
        # v1.1
        route('/api/v1.1/stations')(self.stations)
        route('/api/v1.1/stations/<station>')(self.station)
        route('/api/v1.1/stations/<station>/streams')(self.streams)
        route('/api/v1.1/stations/<station>/streams/<stream>')(self.stream)
        route('/api/v1.1/streams')(self.streams)
        route('/api/v1.1/streams/<station>')(self.streams)
        route('/api/v1.1/streams/<station>/<stream>')(self.stream)
        route('/api/v1.1/player')(self.status)
        post('/api/v1.1/player')(self.play)
        post('/api/v1.1/player/<station>/<stream>')(self.play)
        put('/api/v1.1/player')(self.pause)
        delete('/api/v1.1/player')(self.stop)
        run(host=self.host, port=self.port,
            debug=BOTTLE_DEBUG, quiet=not BOTTLE_DEBUG)

    # def enable_cors(self):
    #     '''Add headers to enable CORS'''
    #     _allow_origin = '*'
    #     _allow_methods = 'PUT, GET, POST, DELETE, OPTIONS'
    #     _allow_headers = ('Authorization, Origin, Accept, ' +
    #                       'Content-Type, X-Requested-With'
    #     response.headers['Access-Control-Allow-Origin'] = _allow_origin
    #     response.headers['Access-Control-Allow-Methods'] = _allow_methods
    #     response.headers['Access-Control-Allow-Headers'] = _allow_headers

    # def options_handler(path=None):
    #     '''Respond to all OPTIONS requests with a 200 status'''
    #     return

    def frontend(self):
        static_dir = os.path.abspath(os.path.dirname(__file__))
        static_html = os.path.join(static_dir, 'index.html')
        with open(static_html, 'r') as f:
            html = f.read()
        return html + '\n'

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

    # TODO incl streams w/ station data
    def station(self, station):
        station = unquote(station)
        success = False
        name = None
        ui_n = None
        file = None
        rebuild = None
        found_st = self.radio.station_obj(station)
        if found_st is not None:
            success = True
            name = found_st.name
            ui_n = found_st.ui_name
            file = found_st.file
            rebuild = found_st.rebuild
        resp = {
            'name': name,
            'ui_name': ui_n,
            'file': file,
            'rebuild': rebuild,
        }
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def stream(self, station, stream):
        station_search = unquote(station)
        stream = unquote(stream)
        success = False
        station = None
        name = None
        url = None
        desc = None
        art = None
        meta_name = None
        meta_song = None
        is_playing = None
        is_paused = None
        found_stn = self.radio.station_obj(station_search)
        if found_stn is not None:
            # print('fstn %s' % found_stn)
            # print('searching %s' % stream)
            found_stm = found_stn.stream_obj(stream)
            if found_stm is not None:
                # print('fstm %s' % found_stm)
                success = True
                station = found_stm.station
                name = found_stm.name
                url = found_stm.url
                desc = found_stm.desc
                art = found_stm.art
                meta_name = found_stm.meta_name
                meta_song = found_stm.meta_song
                is_playing = found_stm.is_playing
                is_paused = found_stm.is_paused
        resp = {
            'station': station,
            'name': name,
            'url': url,
            'desc': desc,
            'art': art,
            'meta_name': meta_name,
            'meta_song': meta_song,
            'is_playing': is_playing,
            'is_paused': is_paused,
        }
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    # TODO incl streams w/ station data
    def stations(self):
        success = True
        resp = {
            'stations': self.radio.stations
        }
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def streams(self, station=None):
        if station is not None:
            station = unquote(station)
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
        station = unquote(station)
        if stream is not None:
            stream = unquote(stream)
        success = self.radio.set(station, stream)
        resp = 'Setting active stream to %s %s' % (station, stream)
        return json.dumps({'success': success, 'resp': resp}) + '\n'

    def play(self, station=None, stream=None):
        # Any conditions when auto-stop make sense?
        if self.radio.is_playing and not self.radio.is_paused:
            success = False
            resp = 'Failure: stop/pause before playing'
            return json.dumps({'success': success, 'resp': resp}) + '\n'
        if station is not None:
            station = unquote(station)
        if stream is not None:
            stream = unquote(stream)
        if (station is not None and stream is not None and
                (self.radio.station != station or
                 self.radio.stream != stream)):
            if not self.radio.set(station, stream):
                success = False
                resp = 'Failure: could not set the station/stream'
                return json.dumps({'success': success, 'resp': resp}) + '\n'
        (station, stream) = self.radio.play()
        success = True
        resp = 'Playing %s %s' % (station, stream)
        if station is None or stream is None:
            success = False
            resp = 'Failure: could not play'
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
    version = 'v1.1'

    def __init__(self, addr=None):
        self.host = '127.0.0.1'
        self.port = PORT
        if addr is not None:
            (self.host, self.port) = addr

    def url(self, endpoint):
        return ('http://%s:%s/api/%s/%s' %
                (self.host, self.port, self.version, endpoint))

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

    def put(self, endpoint, data={}):
        try:
            resp = requests.put(self.url(endpoint), data=json.dumps(data))
        except requests.ConnectionError as e:
            raise ApiConnError(e)
        try:
            resp_val = json.loads(resp.text)
        except ValueError as e:
            # remote server fails and kills connection or returns nothing
            raise ApiConnError(e)
        return resp_val

    def delete(self, endpoint):
        try:
            resp = requests.delete(self.url(endpoint))
        except requests.ConnectionError as e:
            raise ApiConnError(e)
        try:
            resp_val = json.loads(resp.text)
        except ValueError as e:
            # remote server fails and kills connection or returns nothing
            raise ApiConnError(e)
        return resp_val

    def status(self, station=None):
        rjson = self.get('player')
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def station(self, station):
        rjson = self.get('stations/%s' % station)
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
        rjson = self.get('stations/%s/streams/%s' % (station, stream))
        # aso streams/<station>/<stream>
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return None
        return rjson['resp']

    def streams(self, station=None):
        if station is None:
            rjson = self.get('streams')
        else:
            rjson = self.get('stations/%s/streams' % station)
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return []
        return rjson['resp']['streams']

    def play(self, station=None, stream=None):
        url = 'player'
        if station is not None and stream is not None:
            url = 'player/%s/%s' % (station, stream)
        rjson = self.post(url)
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True

    def pause(self):
        rjson = self.put('player')
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True

    def stop(self):
        rjson = self.delete('player')
        if rjson is None or not rjson['success']:
            print('API request failure: %s' % rjson)
            return False
        return True
