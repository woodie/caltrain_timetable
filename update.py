#!/usr/bin/env python

import csv
import os
import subprocess
from collections import OrderedDict 

xstr = lambda s: s or ''

def main():
  fetch_schedule_data()
  trips = parse_trip_data()
  stations = parse_station_data()
  times = parse_schedule_data(trips, stations)
  write_schedule_file('north', 'weekday', times, stations)
  write_schedule_file('south', 'weekday', times, stations)
  write_schedule_file('north', 'weekend', times, stations)
  write_schedule_file('south', 'weekend', times, stations)

def fetch_schedule_data():
  #source = 'http://www.caltrain.com/Assets/GTFS/caltrain/CT-GTFS.zip'
  source = 'http://www.caltrain.com/Assets/GTFS/caltrain/TimeTable/April2019_GTFS.zip'
  basedir = os.getcwd()
  subprocess.call(['mkdir', '-p', 'downloads'])
  os.chdir('downloads')
  subprocess.call(['rm', 'CT-GTFS.zip'])
  subprocess.call(['curl', '-o', 'CT-GTFS.zip', source])
  os.chdir(basedir)
  subprocess.call(['mkdir', '-p', 'CT-GTFS'])
  os.chdir('CT-GTFS')
  subprocess.call(['unzip', '-o', '../downloads/CT-GTFS.zip'])
  os.chdir(basedir)

def parse_trip_data():
  _trips = {}
  with open('CT-GTFS/trips.txt', 'rb') as tripsFile:
    tripsReader = csv.reader(tripsFile)
    header = next(tripsReader, None)
    trip_id_x = header.index('trip_id')
    trip_name_x = header.index('trip_short_name')
    for row in tripsReader:
      trip_id = row[trip_id_x]
      trip_name = row[trip_name_x]
      _trips[trip_id] = trip_name
  return _trips

def parse_station_data():
  _stations = {'north':[], 'south':[], 'labels':{}}
  extra = ['Diridon', 'Caltrain', 'Station']
  with open('CT-GTFS/stops.txt', 'rb') as stopsFile:
    stopsReader = csv.reader(stopsFile)
    header = next(stopsReader, None)
    stop_id_x = header.index('stop_id')
    stop_name_x = header.index('stop_name')
    for row in stopsReader:
      stop_id = int(row[stop_id_x])
      if (stop_id > 70400):
        continue # skip fake stations
      stop_name = ' '.join(i for i in row[stop_name_x].split() if i not in extra)
      _stations['labels'][stop_id] = stop_name
      if (stop_id % 2 == 1):
        _stations['north'].insert(0, stop_id)
      else:
        _stations['south'].append(stop_id)
  return _stations

def parse_schedule_data(trips, stations):
  _times = {'weekday':{'north':OrderedDict(), 'south':OrderedDict()},
            'weekend':{'north':OrderedDict(), 'south':OrderedDict()}}
  with open('CT-GTFS/stop_times.txt', 'rb') as timesFile:
    timesReader = csv.reader(timesFile)
    header = next(timesReader, None)
    trip_id_x = header.index('trip_id')
    stop_id_x = header.index('stop_id')
    departure_x = header.index('departure_time')
    sortedLines = sorted(timesReader, key=lambda row: int(row[departure_x].replace(':','')))
    for row in sortedLines:
      trip_num = trips[row[trip_id_x]]
      if (len(trip_num) > 4):
        continue # skip special times HERE
      trip_id = int(trip_num)
      stop_id = int(row[stop_id_x])
      hour = int(row[departure_x][0:-6])
      minute = row[departure_x][-5:-3]
      ampm = 'PM' if (hour > 11 and hour < 24) else 'AM'
      hr = hour - 12 if (hour > 12) else hour
      departure = "%s:%s %s" % (hr, minute, ampm)
      direction = 'north' if (stop_id % 2 == 1) else 'south'
      schedule = 'weekday' if (trip_id < 400) else 'weekend'
      if (trip_id not in _times[schedule][direction]):
        _times[schedule][direction][trip_id] = [None] * len(stations[direction])
      _times[schedule][direction][trip_id][stations[direction].index(stop_id)] = departure
  return _times

def write_schedule_file(direction, schedule, times, stations):
  days = 'M-F' if (schedule == 'weekday') else 'S-Su'
  with open('res/CalTrain@%s %s.txt' % (direction.capitalize(), days), 'w') as f:
    header = ['Train No.']
    for stop_id in stations[direction]:
      header.append(stations['labels'][stop_id])
    f.write('\t'.join(header))
    f.write('\n')
    for trip_id in times[schedule][direction]:
      f.write('\t'.join(map(xstr,[str(trip_id)] + times[schedule][direction][trip_id])))
      f.write('\n')


if __name__ == "__main__":
    main()
