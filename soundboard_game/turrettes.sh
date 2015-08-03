#!/bin/sh
#FILES=/path/to/*
FILES=*.wav
  value=`cat soundshot`   # soundshot is the file with a number to advance and $
  echo "$value"
  if [ "$value" -gt "0" ]
        then
      for f in $FILES
        do
	  # take action on each file. $f store current file name
	  if [ "$value" -eq "0" ]
	     then
	      echo "Playing $f file on code $value..."
	      mplayer "$f"
	      cp template soundshot
	      exit
	      #aplay "$f"; this line depreciated
	     else
	      value=$(($value-1));
	  fi
        done
  fi
cp template soundshot

