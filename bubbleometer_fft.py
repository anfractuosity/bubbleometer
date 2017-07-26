#!/usr/bin/python3
 
from random import randint
import sys
import struct 
import numpy as np
import time
import glob
import _thread
import random

from matplotlib.pylab import *
import matplotlib.pyplot as plt
import matplotlib.animation as anim

from time import sleep
from collections import deque

import scipy.signal as signal
import scipy.io.wavfile as wavfile
import collections
import matplotlib.dates as mdate
import datetime as dt

from multiprocessing import Process, Queue
from bubbleometer import *

# Audio chunk size
CHUNK=1024*2

# Number of CPU cores to use
CORES=8

# Generate data for the graph
def data_gen(filename):

    wav = wavfile.read(filename)[1]
    r = 0

    while True:
 
        data = wav[r:r+CHUNK]

        if len(data) != CHUNK:
            break
        
        mags,magsl  = fft_process(data,0)             
        r += CHUNK

        yield mags

q = Queue()
plist = []

def process(filename,epoch,q):
    
    y = []
    x = []
    i=1

    for v in data_gen(filename):

        if len(v) > 24 and max(v) > 50:
            y.append(1)
        else: 
            y.append(0)

        x.append((epoch-(60*60))+((CHUNK/48e3)*i))
        i+=1
    
    q.put((x,y,epoch))


data = {}

lines = []

# Load file with timestamp data
with open('wav/txt') as fin:
    for line in fin: 
        v = line.split(",")
        ep = int(v[0])
        wfile = v[1][1:-2]
        lines.append(("wav/"+wfile,ep))

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

y = remove(y)

newy = []
newx = []

count = 0

tval = x[0]

# Extract bubbles per minute data
for i in range(0,len(x)):

    if y[i] == 1:
        count += 1

    if x[i] > tval + (60):
        newy.append(count)
        newx.append(tval)
        tval = x[i]
        count = 0

graphit(newx,newy)
