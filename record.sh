#!/bin/bash

SEC=`expr 60 \* 24`
echo $SEC

sox -d bubbles_.wav channels 1 rate 48k trim 0 $SEC : newfile : restart
