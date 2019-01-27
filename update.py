#!/usr/bin/env python

import csv
import re
import os
import subprocess
from collections import OrderedDict 

xstr = lambda s: s or ''

def main():
  fetch_schedule_data()
  stations = parse_station_data()
  trips = parse_schedule_data(stations)
  write_schedule_file('north', 'weekday', trips, stations)
  write_schedule_file('south', 'weekday', trips, stations)
  write_schedule_file('north', 'weekend', trips, stations)
  write_schedule_file('south', 'weekend', trips, stations)

def fetch_schedule_data():
  source = 'http://www.caltrain.com/Assets/GTFS/caltrain/CT-GTFS.zip'
  basedir = os.getcwd()
  subprocess.call(['mkdir', '-p', 'downloads'])
  os.chdir('downloads')
  subprocess.call(['rm', 'CT-GTFS.zip'])
  subprocess.call(['curl', '-O', source])
  os.chdir(basedir)
  subprocess.call(['mkdir', '-p', 'CT-GTFS'])
  os.chdir('CT-GTFS')
  subprocess.call(['unzip', '-o', '../downloads/CT-GTFS.zip'])
  os.chdir(basedir)

def parse_station_data():
  _stations = {'north':[], 'south':[], 'labels':{}}
  with open('CT-GTFS/stops.txt', 'rb') as stopsFile:
    stopsReader = csv.reader(stopsFile)
    stopHeaders = next(stopsReader, None)
    for row in stopsReader:
      stop_id = int(row[1])
      for words in ['Diridon', 'Caltrain', 'Station']:
        row[2] = row[2].replace(words, '')
      _stations['labels'][stop_id] = re.sub('\s+', ' ', row[2]).strip()
      if (stop_id % 2 == 1):
        _stations['north'].insert(0, stop_id)
      else:
        _stations['south'].append(stop_id)
  return _stations

def parse_schedule_data(stations):
  _trips = {'weekday':{'north':OrderedDict(), 'south':OrderedDict()},
            'weekend':{'north':OrderedDict(), 'south':OrderedDict()}}
  with open('CT-GTFS/stop_times.txt', 'rb') as timesFile:
    timesReader = csv.reader(timesFile)
    timeHeaders = next(timesReader, None)
    for row in timesReader:
      if (len(row[0]) > 4):
        continue
      trip_id = int(row[0])
      stop_id = int(row[3])
      hour = int(row[2][0:-6])
      minute = row[2][-5:-3]
      ampm = 'PM' if (hour > 11 and hour < 24) else 'AM'
      hr = hour - 12 if (hour > 12) else hour
      departure = "%s:%s %s" % (hr, minute, ampm)
      direction = 'north' if (stop_id % 2 == 1) else 'south'
      schedule = 'weekday' if (trip_id < 400) else 'weekend'
      if (trip_id not in _trips[schedule][direction]):
        _trips[schedule][direction][trip_id] = [None] * len(stations[direction])
      _trips[schedule][direction][trip_id][stations[direction].index(stop_id)] = departure
  return _trips

def write_schedule_file(direction, schedule, trips, stations):
  days = 'M-F' if (schedule == 'north') else 'S-Su'
  with open('res/CalTrain@%s %s.txt' % (direction.capitalize(), days), 'w') as f:
    header = ['Train No.']
    for stop_id in stations[direction]:
      header.append(stations['labels'][stop_id])
    f.write('\t'.join(header))
    f.write('\n')
    for trip_id in trips[schedule][direction]:
      f.write('\t'.join(map(xstr,[str(trip_id)] + trips[schedule][direction][trip_id])))
      f.write('\n')


if __name__ == "__main__":
    main()
