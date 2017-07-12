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

data = []
bubbles = []
CHUNK=1024*2

bval = 200

# Try to remove false bubbles
def remove(ny):
    for i in range(0,len(ny)):
        zeroidx = -1
        if ny[i] == 1:
            count = 1
            for i2 in range(i+1,len(ny)):
                if ny[i2] == 1:
                    count += 1
                else: 
                    if ny[i2] == 0:
                        zeroidx = i2
                        break
            zz = i+1
            if count > 7:
                zz = i

            for i2 in range(zz,zeroidx):
                ny[i2] = 0
            
            i = zeroidx

    return ny

# Generate data for the graph
def data_gen(ff):
    wf2 = wavfile.read(ff)
    d = wf2[1]
   
    r = 0

    while True: 
        data = d[r:r+CHUNK]

        if len(data) != CHUNK:
            break
        
        fft = np.fft.fft(data)
        fft = np.abs(fft[0:int(len(fft)/2)])

        magsl = []   
        c = 0                                                                        
        
        for v in fft:                                                                                                      
            if v > 20000:
                magsl.append(c)   
            c += 1 
                 
        r += CHUNK

        yield magsl 

q = Queue()
plist = []

def process(wfile,ep,q):
    
    ny = []
    xx = []
    i=1

    for v in data_gen(wfile):
        if len(v) > 70:
            ny.append(1)
        else: 
            ny.append(0)
        xx.append((ep-(60*60))+((CHUNK/48e3)*i))
        i+=1
    
    q.put((xx,ny,ep))


data = {}

lines = []

with open('txt') as fin:
    for line in fin: 
        v = line.split(",")
        ep = int(v[0])
        wfile = v[1][1:-2]
        lines.append((wfile,ep))

c = 1

for l in lines:

    p = Process(target=process, args=(l[0],l[1],q,))
    plist.append(p)
    p.start()

    print("starting")
    if len(plist) == 8 or c == len(lines):
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

od = collections.OrderedDict(sorted(data.items()))

for k, v in od.items():
    print (k)
    for val in range(0,len(v[0])):
        x.append(v[0][val])
        y.append(v[1][val])

y = remove(y)

newy = []
newx = []

count = 0

tval = x[0]

for i in range(0,len(x)):

    if y[i] == 1:
        count += 1

    if x[i] > tval + (60):
        newy.append(count)
        newx.append(tval)
        tval = x[i]
        count = 0

fig2 = plt.figure()
ax4 = fig2.add_subplot(111)
secs = mdate.epoch2num(newx)

ax4.plot_date(secs,newy,'r-')
#ax4.plot_date(secs,scipy.ndimage.filters.gaussian_filter1d(newy,3.0),'b-')
yhat = signal.savgol_filter(newy, 51, 3) # window size 51, polynomial order 3
ax4.plot_date(secs,yhat,'b-')

date_fmt = '%d-%m-%y %H:%M:%S'
date_formatter = mdate.DateFormatter(date_fmt)
ax4.xaxis.set_major_formatter(date_formatter)
fig2.autofmt_xdate()
plt.show()

