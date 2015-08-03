#!/bin/sh
#FILES=/path/to/*
FILES=*.wav
for f in $FILES
do
  echo "Processing $f file..."
  # take action on each file. $f store current file name
  mplayer "$f"
#  aplay "$f" 
#  cat $f
done

