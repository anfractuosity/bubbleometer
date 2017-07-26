#!/usr/bin/python3
 
from random import randint
import sys
import struct 
import numpy as np
import time
import glob
import _thread
import random

from time import sleep
from collections import deque

import scipy.io.wavfile as wavfile
import collections
from multiprocessing import Process, Queue
import scipy.stats as stats
from bubbleometer import *

# Audio chunk size
CHUNK=512

# Number of CPU cores to use
CORES=2

q = Queue()
plist = []

def process(filename,epoch,q):
    
    y = []
    x = []
    i=1
    bad = []
    wav = wavfile.read(filename)[1]
    filt = filter_wav(wav)
    r = 0

    for d in range(0,len(filt),CHUNK):#window(y,CHUNK):
    
        data = filt[d:d+CHUNK]

        if len(data) != CHUNK:
            break

        mags = integrate(data) 
        
        y.append(mags)
        x.append((epoch-(60*60))+((CHUNK/48e3)*r))
        r+=1
        
    q.put((x,y,epoch))


data = {}

lines = timestampdata()

c = 1

# Spawn processes to process each wav file
for l in lines:

    p = Process(target=process, args=(l[0],l[1],q,))
    plist.append(p)
    p.start()

    print("starting")
    if len(plist) == CORES or c == len(lines):
        for p in plist:
            job = q.get()
            data[job[2]] = ( job[0] , job[1] )
        for p in plist:
            p.join()
        plist = []
        q = Queue()

    c += 1

y = []
x = []

# Sort data from the multiple processes
od = collections.OrderedDict(sorted(data.items()))
for k, v in od.items():
    for val in range(0,len(v[0])):
        x.append(v[0][val])
        y.append(v[1][val])

y = remove_break(y)
newx,newy = getbubblesperminute(x,y)
graphit(newx,newy)
