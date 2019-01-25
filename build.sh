#!/bin/bash

# http://www.freeware-symbian.com/s80-7-0-device-1769/caltrain-schedule-timetable-for-javaphone-download-29145.html

SRC=CalTrain
OUT=CalTrainSchedule

BASE=http://www.caltrain.com/Assets/GTFS/caltrain
DATA=CT-GTFS

rm -rf dist $DATA
mkdir -p dist $DATA

cd downloads
rm $DATA.zip
curl -O $BASE/$DATA.zip
cd ../$DATA
unzip ../downloads/$DATA.zip

cd ..
cp downloads/$SRC.jar dist/$OUT.jar
cd res # Add appropriate icon
jar uf ../dist/$OUT.jar icon40x40.png 
cd ..

while read line; do
  if [[ "$line" =~ "MIDlet-Jar-URL" ]]; then
    echo MIDlet-Jar-URL: $OUT.jar
  else
    echo $line
  fi
done < downloads/$SRC.jad > dist/$OUT.jad
echo "MIDlet-Icon: icon40x40.png" >> dist/$OUT.jad
