#!/bin/bash

# log start time
date > start

# record in hourly chunks
SEC=`expr 60 \* 60`
echo $SEC

# start recording
sox -d bubbles_.wav channels 1 rate 48k trim 0 $SEC : newfile : restart
