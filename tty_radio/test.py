#!/usr/bin/env python
from time import sleep, time
import sys
from json import loads
from threading import Thread
from tty_radio.radio import Radio
from tty_radio.stream import mpg_running
from tty_radio.api import Server, Client


def test_obj():  # noqa
    r = Radio()
    i = 0
    print('%02d>>> r:%s' % (i, r))
    i += 1
    print('%02d>>> r.stations:%s' % (i, r.stations))
    i += 1
    if r.play()[0] is not None or mpg_running():
        print('%02d>>> Failed play without set' % i)
        sys.exit(1)
    r.set('favs')
    print('%02d>>> r.station:%s' % (i, r.station))
    i += 1
    print('%02d>>> r._station:%s' % (i, r._station))
    i += 1
    print('%02d>>> r._station.streams:%s' % (i, r._station.streams))
    i += 1
    if not r.set('favs', 'BAGeL Radio'):
        print('%02d>>> Failed initial set' % i)
        sys.exit(1)
    print('%02d>>> Playing' % i)
    i += 1
    t1 = time()
    if r.play()[1] is None:
        print('%02d>>> Failed play 1' % i)
        sys.exit(1)
    while r.song is None:
        sleep(1)
    print('%02d>>> Play 1 wait was %s' % (i, int(time() - t1)))
    i += 1
    if not mpg_running():
        print('%02d>>> Failed play 1' % i)
        sys.exit(1)
    print('%02d>>> r.song:%s' % (i, r.song))
    i += 1
    print('%02d>>> Pausing' % i)
    i += 1
    t1 = time()
    r.pause()
    while not r.is_paused:
        sleep(1)
    print('%02d>>> Pause wait was %s' % (i, int(time() - t1)))
    i += 1
    if mpg_running():
        print('%02d>>> Failed pause 1' % i)
        sys.exit(1)
    print('%02d>>> Playing' % i)
    i += 1
    t1 = time()
    if r.play()[1] is None:
        print('%02d>>> Failed play 2' % i)
        sys.exit(1)
    while r.song is None:
        sleep(1)
    print('%02d>>> Play 2 wait was %s' % (i, int(time() - t1)))
    i += 1
    if not mpg_running():
        print('%02d>>> Failed play 2' % i)
        sys.exit(1)
    print('%02d>>> Stopping' % i)
    i += 1
    t1 = time()
    r.stop()
    while r.is_playing:
        sleep(1)
    if mpg_running():
        print('%02d>>> Failed stop 1' % i)
        sys.exit(1)
    print('%02d>>> Stop wait was %s' % (i, int(time() - t1)))
    i += 1
    if not r.set('favs', 'WCPE Classical'):
        print('%02d>>> Failed stop and set' % i)
        sys.exit(1)
    print('%02d>>> r.stream:%s' % (i, r.stream))
    i += 1
    print('%02d>>> r._stream:%s' % (i, r._stream))
    i += 1
    print('%02d>>> Playing' % i)
    i += 1
    t1 = time()
    if r.play()[1] is None or not mpg_running():
        print('%02d>>> Failed play 3' % i)
        sys.exit(1)
    while r._stream.meta_name is None:
        sleep(1)
    print('%02d>>> Play 3 wait was %s' % (i, int(time() - t1)))
    i += 1
    if r.play()[0] is not None:
        print('%02d>>> Failed play during an active play' % i)
        sys.exit(1)
    if not r.set('favs'):
        print('%02d>>> Failed set test 1' % i)
        sys.exit(1)
    if not r.set('favs', 'WCPE Classical'):
        print('%02d>>> Failed set test 2' % i)
        sys.exit(1)
    if r.set('favs', 'BAGeL Radio'):
        print('%02d>>> Failed set test 3' % i)
        sys.exit(1)
    print('%02d>>> Stopping' % i)
    i += 1
    t1 = time()
    r.stop()
    while r.is_playing:
        sleep(1)
    if mpg_running():
        print('%02d>>> Failed stop 2' % i)
        sys.exit(1)
    print('%02d>>> Stop wait was %s' % (i, int(time() - t1)))
    if r.set('ewqrewrwer'):
        print('%02d>>> Failed set test 4' % i)
        sys.exit(1)
    if r.set('favs', 'ewqrewrwer'):
        print('%02d>>> Failed set test 5' % i)
        sys.exit(1)
    sys.exit(0)


def test_api_serv():  # noqa
    r = Radio()
    s = Server(radio=r)
    i = 0
    r = s.index()
    print('%02d>>> s.index:%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.status()
    print('%02d>>> s.status:%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.stations()
    print('%02d>>> s.stations:%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.streams()
    print('%02d>>> s.streams:%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.streams('favs')
    print('%02d>>> s.streams(favs):%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.streams('ewqrewrwer')
    print('%02d>>> s.streams(ewqrewrwer):%s' % (i, r))
    i += 1
    if loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.set('favs')
    print('%02d>>> s.set(favs):%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.set('ewqrewrwer')
    print('%02d>>> s.set(ewqrewrwer):%s' % (i, r))
    i += 1
    if loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.set('favs', 'ewqrewrwer')
    print('%02d>>> s.set(favs,ewqrewrwer):%s' % (i, r))
    i += 1
    if loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.set('favs', 'WCPE Classical')
    print('%02d>>> s.set(favs,WCPE Classical):%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.play()
    print('%02d>>> s.play:%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    sleep(10)
    r = s.play()
    print('%02d>>> double s.play:%s' % (i, r))
    i += 1
    if loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.set('favs', 'BAGeL Radio')
    print('%02d>>> set during play s.set(favs,BAGeL Radio):%s' % (i, r))
    i += 1
    if loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.pause()
    print('%02d>>> s.pause:%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    sleep(2)
    # double pause currently allowed
    # r = s.pause()
    # print('%02d>>> double s.pause:%s' % (i, r))
    # i += 1
    # if loads(r)['success']:
    #     print('%02d>>> Failed' % i)
    #     sys.exit(1)
    r = s.play()
    print('%02d>>> s.play:%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    sleep(10)
    r = s.status()
    print('%02d>>> s.status:%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.stop()
    print('%02d>>> s.stop:%s' % (i, r))
    i += 1
    if not loads(r)['success']:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = s.stop()
    # double stop currently allowed
    # print('%02d>>> double s.stop:%s' % (i, r))
    # i += 1
    # if loads(r)['success']:
    #     print('%02d>>> Failed' % i)
    #     sys.exit(1)
    sys.exit(0)


def test_api_client():  # noqa
    r = Radio()
    s = Server(radio=r)
    st = Thread(target=s.run)
    st.daemon = True
    st.start()
    sleep(1)
    c = Client()
    i = 0
    r = c.status()
    print('%02d>>> c.status:%s' % (i, r))
    i += 1
    if r is None:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = c.stations()
    print('%02d>>> c.stations:%s' % (i, r))
    i += 1
    if len(r) == 0:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    print('%02d>>> c.streams' % i)
    r = c.streams()
    # print('%02d>>> c.streams:%s' % (i, r))
    i += 1
    if len(r) == 0:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    print('%02d>>> c.streams(favs):' % i)
    r = c.streams('favs')
    i += 1
    if len(r) == 0:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    print('%02d>>> c.streams(ewqrewrwer):' % i)
    r = c.streams('ewqrewrwer')
    i += 1
    if len(r) != 0:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    print('%02d>>> c.play(favs,ewqrewrwer)' % i)
    r = c.play('favs', 'ewqrewrwer')
    # print('%02d>>> c.play(favs,ewqrewrwer):%s' % (i, r))
    i += 1
    if r:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = c.play('favs', 'BAGeL Radio')
    print('%02d>>> c.play(favs,BAGeL Radio):%s' % (i, r))
    i += 1
    if not r:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    sleep(10)
    r = c.pause()
    print('%02d>>> c.pause:%s' % (i, r))
    i += 1
    if not r:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = c.stop()
    print('%02d>>> c.stop:%s' % (i, r))
    i += 1
    if not r:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    sleep(2)
    r = c.play('favs', 'WCPE Classical')
    print('%02d>>> c.play(favs,WCPE Classical):%s' % (i, r))
    i += 1
    if not r:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    sleep(10)
    r = c.status()
    print('%02d>>> c.status:%s' % (i, r))
    i += 1
    if r is None:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    r = c.stop()
    print('%02d>>> c.stop():%s' % (i, r))
    i += 1
    if not r:
        print('%02d>>> Failed' % i)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    # test_obj()
    # test_api_serv()
    test_api_client()
