#!/usr/bin/python3 
from random import randint
import pyaudio
import wave
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
from scipy import signal
import scipy
import wave, struct
import scipy.io.wavfile as wavfile
import collections
import matplotlib.pyplot as plt
import matplotlib.dates as mdate

import numpy as np

import datetime as dt

from multiprocessing import Process, Queue

#import pytz


data = []
bubbles = []
CHUNK=1024*2

flatten = lambda l: [item for sublist in l for item in sublist] 

fig, ax = plt.subplots()

ax1 = subplot2grid((2, 2), (0, 0))
ax2 = subplot2grid((2, 2), (0, 1))
ax3 = subplot2grid((2, 2), (1, 0))


l1, = ax1.plot([], [], 'bo')

bval = 200
test = np.zeros(2048)
hist, bins = np.histogram(test,bins=bval)
#center = (bins[:-1] + bins[1:]) / 2

rects, = ax2.plot(bins[0:bval], hist, color='c')

# Start pyaudio and load wav
p = pyaudio.PyAudio()


l3, = ax3.plot([], [], 'r-')


olddatax = []
olddatay = []
rows = 0


def remove(ny):
    # remove false bubbles
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

## Plot data on the graph
def update(newdata):

    global rows
    olddatax.append(newdata[0])
    olddatay.append(newdata[1])
    xx = flatten(olddatax)
    yy = flatten(olddatay)

    ax1.set_xlim(0, rows)
    
    my = 0
    if len(yy) == 0:
        my = 10
    else:
        my = max(yy)  

    ax1.set_ylim(0, 2048/2)
    l1.set_xdata(xx)
    l1.set_ydata(yy)

    hist, bins = np.histogram(newdata[1],bins=bval)
    """
    for rect, yi in zip(rects, hist ):
        v = randint(0,2048)
        rect.set_height(v)

    """

    ax2.set_xlim(0, bval)
    ax2.set_ylim(0,5)
    rects.set_xdata(bins[0:bval])
    rects.set_ydata(hist)

    ax3.set_ylim(0, 2048/2)

    xx2 = np.arange(0,len(olddatax))

    
    ny = []
    for v in olddatay:
        if len(v) > 40:
            ny.append(1)
        else: 
            ny.append(0)

    ax3.set_xlim(0, len(olddatax))
    ax3.set_ylim(0, max(ny))

    l3.set_xdata(xx2)
    l3.set_ydata(ny)
    #l2.set_data(x, data[0])

    return l1,rects,l3,


## Generate data for the graph
def data_gen(ff):
    wf2 = wavfile.read(ff)
    global rows
    
    d = wf2[1]
   
    ln = len(wf2[1]) 
    r = 0
    #data = wf.readframes(CHUNK)

    while True: #data != '':
        
        #s = np.frombuffer(data,dtype="<i2")
        ## play audio
        #stream.write(data)
        #data = wf.readframes(CHUNK)

        data = d[r:r+CHUNK]

        if len(data) != CHUNK:
            break
        
        fft = np.fft.fft(data)
        fft = np.abs(fft[0:int(len(fft)/2)])

        mags = []  
        magsl = []   
        c = 0                                                                        
        
        for v in fft:                                                                                                      
            #mag = np.sqrt((v.real**2)+(v.imag**2))  
            if v > 20000:
                mags.append(rows)
                magsl.append(c)   
                                                                               
            c += 1                  
        rows += 1
        r += CHUNK

        #if r % CHUNK*1000 == 0:
        #    print(r,ln)

        yield [ mags , magsl ]

## Use animation, so we get a live graph
#ff = "bubbles_072.wav"
#ani = anim.FuncAnimation(fig, update, data_gen,interval=0,blit=True)
#plt.show()

#while True:
#    sleep(1)

q = Queue()
plist = []

def process(wfile,ep,q):
    
    ny = []
    xx = []

    i=1

    for v in data_gen(wfile):
        if len(v[1]) > 70:
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

ny = []
xx = []

od = collections.OrderedDict(sorted(data.items()))

for k, v in od.items():
    print (k)
    for val in range(0,len(v[0])):
        xx.append(v[0][val])
        ny.append(v[1][val])

ny = remove(ny)

newy = []
newx = []

count = 0

tval = xx[0]

for i in range(0,len(xx)):

    if ny[i] == 1:
        count += 1

    if xx[i] > tval + (60):
        newy.append(count)
        newx.append(tval)
        tval = xx[i]
        count = 0
        
    

    ##if i > 100:
    #    break

fig2 = plt.figure()
ax4 = fig2.add_subplot(111)
secs = mdate.epoch2num(newx)

ax4.plot_date(secs,newy,'r-')
#ax4.plot_date(secs,scipy.ndimage.filters.gaussian_filter1d(newy,3.0),'b-')
yhat = scipy.signal.savgol_filter(newy, 51, 3) # window size 51, polynomial order 3
ax4.plot_date(secs,yhat,'b-')





date_fmt = '%d-%m-%y %H:%M:%S'
date_formatter = mdate.DateFormatter(date_fmt)
ax4.xaxis.set_major_formatter(date_formatter)
fig2.autofmt_xdate()
plt.show()

## Need to keep main thread alive
while True:
    sleep(1)
