#!/bin/bash

# This script will be used by the poll service when archive will be found. Extract
# content, run make command and post results in given directory.

FILE=$1
DIR_SRC=$2
DIR_RES=$3

err=0
# Message for missing Makefile
MSG="error: Makefile is missing"

# Get user hash from archive name
hash=$(echo $FILE | cut -d '.' -f 1)

# Create result file
RES_FILE=$DIR_RES/$hash.result

# Create dir and extract archive
cd $DIR_SRC
mkdir $hash
unzip $FILE -d $hash
cd $hash

# Return error if Makefile is missing
if [ ! -f "Makefile" ]; then
	echo $MSG > $RES_FILE
	err=1
fi

# Run make for compiling and redirect output/err to log file
make >> $RES_FILE 2>&1

# Clean and delete directory
cd ..
echo "rm -rf $hash"
rm -rf $hash $FILE
exit $err
