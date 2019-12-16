#!/bin/bash

# This script will be part of a polling service. It will look for every
# SLP secondis inside DIR and check if any file of extension EXT exists.

# Set the directory and extension to look for
DIR=$1
EXT=$2
SLP=$3
LOGS="tmp/pollmsg"

# Go to directory
cd $DIR

# Poll for changes
while true; do
	files=$(find . -name "*.$EXT")
	if [ ! -z "$files" ]
	then
		current_date_time="`date "+%Y-%m-%d %H:%M:%S"`";
		echo -e "[$current_date_time]Files detected:\n========\n$files\n========"
	fi
	sleep $SLP
done
