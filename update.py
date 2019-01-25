#!/usr/bin/env python

import csv

datafiles = ['CalTrain@North M-F.txt', 'CalTrain@North S-Su.txt',
             'CalTrain@South M-F.txt', 'CalTrain@South S-Su.txt']
nb_stations = []; nb_weekday = {}; nb_weekend = {}  
sb_stations = []; sb_weekday = {}; sb_weekend = {}

labels = {}
with open('CT-GTFS/stops.txt', 'rb') as stopsFile:
  stopsReader = csv.reader(stopsFile)
  stopHeaders = next(stopsReader, None)
  for row in stopsReader:
    stop_id = int(row[1])
    labels[stop_id] = row[2].replace(' Caltrain', '').replace(' Station', '')
    if (stop_id % 2 == 1):
      nb_stations.append(stop_id)
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
    departure = row[2][0:-3]
    if (stop_id % 2 == 1):
      if (trip_id < 400):
        if (trip_id not in nb_weekday):
          nb_weekday[trip_id] = [None] * len(nb_stations)
        nb_weekday[trip_id][nb_stations.index(stop_id)] = departure
      else:
        if (trip_id not in nb_weekend):
          nb_weekend[trip_id] = [None] * len(nb_stations)
        nb_weekend[trip_id][nb_stations.index(stop_id)] = departure
    else:
      if (trip_id < 400):
        if (trip_id not in sb_weekday):
          sb_weekday[trip_id] = [None] * len(sb_stations)
        sb_weekday[trip_id][sb_stations.index(stop_id)] = departure
      else:
        if (trip_id not in sb_weekend):
          sb_weekend[trip_id] = [None] * len(sb_stations)
        sb_weekend[trip_id][sb_stations.index(stop_id)] = departure

# generate four files
