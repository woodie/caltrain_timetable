#!/bin/bash

JME=/Applications/Java_ME_SDK_3.0.app/Contents/Resources

SRC=CalTrain
OUT=CalTrainSchedule

rm -rf dist
mkdir -p dist

cp downloads/$SRC.jar dist/$OUT.jar
cd res
jar uf ../dist/$OUT.jar icon40x40.png CalTrain*txt
cd ..

while read line; do
  if [[ "$line" =~ "MIDlet-Jar-URL" ]]; then
    echo MIDlet-Jar-URL: $OUT.jar
  elif [[ "$line" =~ "MIDlet-Jar-Size" ]]; then
    echo MIDlet-Jar-Size: $(stat -f %z dist/$OUT.jar)
  elif [[ "$line" =~ "HELP_TEXT" ]]; then
    echo HELP_TEXT: Caltrain timetable may not be current.
  else
    echo $line
  fi
done < downloads/$SRC.jad > dist/$OUT.jad
echo "MIDlet-Icon: icon40x40.png" >> dist/$OUT.jad

$JME/bin/emulator -Xdevice:DefaultCldcPhone1 -Xdebug \
    -Xrunjdwp:transport=dt_socket,suspend=n,server=y,address=51307 \
    -Xdescriptor:dist/$OUT.jad -Xdomain:maximum

