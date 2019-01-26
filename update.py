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
  write_schedule_file('North M-F',  'nb', trips['weekday'], stations)
  write_schedule_file('South M-F',  'sb', trips['weekday'], stations)
  write_schedule_file('North S-Su', 'nb', trips['weekend'], stations)
  write_schedule_file('South S-Su', 'sb', trips['weekend'], stations)

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
  stations = {'nb':[], 'sb':[], 'labels':{}}
  extraneous = ['Diridon', 'Caltrain', 'Station']
  with open('CT-GTFS/stops.txt', 'rb') as stopsFile:
    stopsReader = csv.reader(stopsFile)
    stopHeaders = next(stopsReader, None)
    for row in stopsReader:
      stop_id = int(row[1])
      for words in extraneous:
        row[2] = row[2].replace(words, '')
      stations['labels'][stop_id] = re.sub('\s+', ' ', row[2]).strip()
      if (stop_id % 2 == 1):
        stations['nb'].insert(0, stop_id)
      else:
        stations['sb'].append(stop_id)
  return stations

def parse_schedule_data(stations):
  weekday = {'nb':OrderedDict(), 'sb':OrderedDict()}
  weekend = {'nb':OrderedDict(), 'sb':OrderedDict()}
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
      if (stop_id % 2 == 1):
        if (trip_id < 400):
          if (trip_id not in weekday['nb']):
            weekday['nb'][trip_id] = [None] * len(stations['nb'])
          weekday['nb'][trip_id][stations['nb'].index(stop_id)] = departure
        else:
          if (trip_id not in weekend['nb']):
            weekend['nb'][trip_id] = [None] * len(stations['nb'])
          weekend['nb'][trip_id][stations['nb'].index(stop_id)] = departure
      else:
        if (trip_id < 400):
          if (trip_id not in weekday['sb']):
            weekday['sb'][trip_id] = [None] * len(stations['sb'])
          weekday['sb'][trip_id][stations['sb'].index(stop_id)] = departure
        else:
          if (trip_id not in weekend['sb']):
            weekend['sb'][trip_id] = [None] * len(stations['sb'])
          weekend['sb'][trip_id][stations['sb'].index(stop_id)] = departure
  return {'weekday':weekday, 'weekend':weekend}

def write_schedule_file(segment, direction, trips, stations):
  with open('res/CalTrain@%s.txt' % segment, 'w') as f:
    header = ['Train No.']
    for stop_id in stations[direction]:
      header.append(stations['labels'][stop_id])
    f.write('\t'.join(header))
    f.write('\n')
    for trip_id in trips[direction]:
      f.write('\t'.join(map(xstr,[str(trip_id)] + trips[direction][trip_id])))
      f.write('\n')


if __name__ == "__main__":
    main()
