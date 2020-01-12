#!/bin/bash

# This script will be part of a polling service. It will look for every
# SLP secondis inside DIR and check if any file of extension EXT exists.

# Set the directory and extension to look for
DIR_SRC=$1
DIR_RES=$2
DIR_LOG=$3
EXT=$4
SLP=$5

# Go to directory
cd $DIR_SRC

# Poll for changes
while true; do
	files=$(find . -name "*.$EXT")
	if [ ! -z "$files" ]
	then
		current_date_time="`date "+%Y-%m-%d %H:%M:%S"`";
		echo -e "[$current_date_time] Files detected:\n========\n$files\n========" >> $DIR_LOG
		for file in $files; do
			# Get only basename
			filename=$(basename $file)
			/usr/local/bin/build.sh $filename $DIR_SRC $DIR_RES
			err=$?
			if [ $err -ne 0 ]; then
				echo -e "[ERROR] : build.sh failed on target $filename\n" >> $DIR_LOG
			fi
		done
	fi
	sleep $SLP
done
