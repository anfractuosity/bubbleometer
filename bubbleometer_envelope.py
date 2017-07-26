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

from scipy.signal import hilbert
from scipy.signal import filtfilt

import sounddevice as sd
sd.default.samplerate = 48000
from multiprocessing import Process, Queue
#from scipy.stats import kde
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

    fs = 48000.0
    lowcut = 800.0
    highcut = 3000.0
    bp = butter_bandpass_filter(wav, lowcut, highcut, fs, order=6)
    b, a = butter(1,100.0/(0.5*48e3), 'low')
    filt = filtfilt(b, a, abs(bp))

    r = 0
    for d in range(0,len(filt),CHUNK):#window(y,CHUNK):
    
        data = filt[d:d+CHUNK]

        if len(data) != CHUNK:
            break

        mags = []   
        integ = np.trapz(data)
        
        if integ > 60000:
            mags = 1
        else:
            mags = 0

        y.append(mags)
        x.append((epoch-(60*60))+((CHUNK/48e3)*r))
        r+=1
        
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

y = remove_break(y)

newy = []
newx = []

count = 0

tval = x[0]

err = False
oldi = 0
# Extract bubbles per minute data
for i in range(0,len(x)):

    if y[i] == 1:
        count += 1

    if x[i] > tval + (60):
        newy.append(count)
        newx.append(tval)
        tval = x[i]
        count = 0
        oldi = i

graphit(newx,newy)
