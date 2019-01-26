#!/usr/bin/env python

import csv
import re
import os
import subprocess

xstr = lambda s: s or ''

nb_stations = []; nb_weekday_trips = {}; nb_weekend_trips = {}
sb_stations = []; sb_weekday_trips = {}; sb_weekend_trips = {}
nb_weekday_order = []; nb_weekend_order = []
sb_weekday_order = []; sb_weekend_order = []
station_labels = {}

def main():
  fetch_schedule_data()
  parse_station_data()
  parse_schedule_data()
  write_schedule_file('North M-F',  nb_weekday_order, nb_weekday_trips, nb_stations)
  write_schedule_file('North S-Su', nb_weekend_order, nb_weekend_trips, nb_stations)
  write_schedule_file('South M-F',  sb_weekday_order, sb_weekday_trips, sb_stations)
  write_schedule_file('South S-Su', sb_weekend_order, sb_weekend_trips, sb_stations)

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
  extraneous = ['Diridon', 'Caltrain', 'Station']
  with open('CT-GTFS/stops.txt', 'rb') as stopsFile:
    stopsReader = csv.reader(stopsFile)
    stopHeaders = next(stopsReader, None)
    for row in stopsReader:
      stop_id = int(row[1])
      for words in extraneous:
        row[2] = row[2].replace(words, '')
      station_labels[stop_id] = re.sub('\s+', ' ', row[2]).strip()
      if (stop_id % 2 == 1):
        nb_stations.insert(0, stop_id)
      else:
        sb_stations.append(stop_id)

def parse_schedule_data():
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
          if (trip_id not in nb_weekday_trips):
            nb_weekday_trips[trip_id] = [None] * len(nb_stations)
            nb_weekday_order.append(trip_id)
          nb_weekday_trips[trip_id][nb_stations.index(stop_id)] = departure
        else:
          if (trip_id not in nb_weekend_trips):
            nb_weekend_trips[trip_id] = [None] * len(nb_stations)
            nb_weekend_order.append(trip_id)
          nb_weekend_trips[trip_id][nb_stations.index(stop_id)] = departure
      else:
        if (trip_id < 400):
          if (trip_id not in sb_weekday_trips):
            sb_weekday_trips[trip_id] = [None] * len(sb_stations)
            sb_weekday_order.append(trip_id)
          sb_weekday_trips[trip_id][sb_stations.index(stop_id)] = departure
        else:
          if (trip_id not in sb_weekend_trips):
            sb_weekend_trips[trip_id] = [None] * len(sb_stations)
            sb_weekend_order.append(trip_id)
          sb_weekend_trips[trip_id][sb_stations.index(stop_id)] = departure

def write_schedule_file(segment, order, trips, stations):
  with open('res/CalTrain@%s.txt' % segment, 'w') as f:
    header = ['Train No.']
    for stop_id in stations:
      header.append(station_labels[stop_id])
    f.write('\t'.join(header))
    f.write('\n')
    for trip_id in order:
      f.write('\t'.join(map(xstr,[str(trip_id)] + trips[trip_id])))
      f.write('\n')


if __name__ == "__main__":
    main()
