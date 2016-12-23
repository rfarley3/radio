#!/usr/bin/env python
from time import sleep, time
import sys
from tty_radio.radio import Radio
from tty_radio.stream import mpg_running


if __name__ == "__main__":
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
