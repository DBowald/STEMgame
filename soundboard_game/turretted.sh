#!/bin/sh
#FILES=/path/to/*
FILES=*.wav
while [ : ] 
do 
  value=`cat soundshot`   # soundshot is the file with a number to advance and $
  #echo "$value"
if [ "$value" -gt "0" ]
    then if [ "$value" -lt "31" ]
	then 
    ./turrettes.sh
        fi
fi 
sleep 1
done 
