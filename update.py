#!/usr/bin/env python

import csv
import re
import os
import subprocess

xstr = lambda s: s or ''

source = 'http://www.caltrain.com/Assets/GTFS/caltrain/CT-GTFS.zip'
nb_stations = []; nb_weekday = {}; nb_weekend = {}
sb_stations = []; sb_weekday = {}; sb_weekend = {}
nb_weekday_order = []; nb_weekend_order = []
sb_weekday_order = []; sb_weekend_order = []
extraneous = ['Diridon', 'Caltrain', 'Station']

# Fetch Caltrain data
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

# Generate app data files
labels = {}
with open('CT-GTFS/stops.txt', 'rb') as stopsFile:
  stopsReader = csv.reader(stopsFile)
  stopHeaders = next(stopsReader, None)
  for row in stopsReader:
    stop_id = int(row[1])
    for words in extraneous:
      row[2] = row[2].replace(words, '')
    labels[stop_id] = re.sub('\s+', ' ', row[2]).strip()
    if (stop_id % 2 == 1):
      nb_stations.insert(0, stop_id)
    else:
      sb_stations.append(stop_id)

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
    if (hour > 12):
      departure = "%s:%s PM" % (hour - 12, minute)
    else:
      departure = "%s:%s AM" % (hour, minute)
    if (stop_id % 2 == 1):
      if (trip_id < 400):
        if (trip_id not in nb_weekday):
          nb_weekday[trip_id] = [None] * len(nb_stations)
          nb_weekday_order.append(trip_id)
        nb_weekday[trip_id][nb_stations.index(stop_id)] = departure
      else:
        if (trip_id not in nb_weekend):
          nb_weekend[trip_id] = [None] * len(nb_stations)
          nb_weekend_order.append(trip_id)
        nb_weekend[trip_id][nb_stations.index(stop_id)] = departure
    else:
      if (trip_id < 400):
        if (trip_id not in sb_weekday):
          sb_weekday[trip_id] = [None] * len(sb_stations)
          sb_weekday_order.append(trip_id)
        sb_weekday[trip_id][sb_stations.index(stop_id)] = departure
      else:
        if (trip_id not in sb_weekend):
          sb_weekend[trip_id] = [None] * len(sb_stations)
          sb_weekend_order.append(trip_id)
        sb_weekend[trip_id][sb_stations.index(stop_id)] = departure

with open('res/CalTrain@North M-F.txt', 'w') as f:
  header = ['Train No.']
  for stop_id in nb_stations:
    header.append(labels[stop_id])
  f.write('\t'.join(header))
  f.write('\n')
  for trip_id in nb_weekday_order:
    f.write('\t'.join(map(xstr,[str(trip_id)] + nb_weekday[trip_id])))
    f.write('\n')

with open('res/CalTrain@North S-Su.txt', 'w') as f:
  header = ['Train No.']
  for stop_id in nb_stations:
    header.append(labels[stop_id])
  f.write('\t'.join(header))
  f.write('\n')
  for trip_id in nb_weekend_order:
    f.write('\t'.join(map(xstr,[str(trip_id)] + nb_weekend[trip_id])))
    f.write('\n')

with open('res/CalTrain@South M-F.txt', 'w') as f:
  header = ['Train No.']
  for stop_id in sb_stations:
    header.append(labels[stop_id])
  f.write('\t'.join(header))
  f.write('\n')
  for trip_id in sb_weekday_order:
    f.write('\t'.join(map(xstr,[str(trip_id)] + sb_weekday[trip_id])))
    f.write('\n')

with open('res/CalTrain@South S-Su.txt', 'w') as f:
  header = ['Train No.']
  for stop_id in sb_stations:
    header.append(labels[stop_id])
  f.write('\t'.join(header))
  f.write('\n')
  for trip_id in sb_weekend_order:
    if (trip_id not in sb_weekend):
      continue
    f.write('\t'.join(map(xstr,[str(trip_id)] + sb_weekend[trip_id])))
    f.write('\n')
