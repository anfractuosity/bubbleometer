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
from scipy.signal import hilbert
from scipy.signal import filtfilt

import sounddevice as sd
sd.default.samplerate = 48000
from multiprocessing import Process, Queue
#from scipy.stats import kde
import scipy.stats as stats
# Audio chunk size
CHUNK=512

# Number of CPU cores to use
CORES=2

from itertools import tee
from scipy.signal import butter, lfilter

def parzen(x,data):
    sig = 5.0
    a = 1.0/(float(len(data)*((2*np.pi)**0.5)*sig))
    b = 0.0
    for v in data:
        b+=math.exp(-((x-v)**2/(2*sig**2)))
    return a * b

def window(iterable, size):
    iters = tee(iterable, size)
    for i in range(1, size):
        for each in iters[i:]:
            next(each, None)
    return zip(*iters)

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def convn(data):
    d = []

    for i in range(len(data)):
        if data[i] == 1:
            d.append(i)
        
    return d

#data = [ 1, 0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0 ]

def rm(density,rmq,v,idv):
    nout = []
    for i in v:
        if density(i) > 0.00001:
            nout.append(1)
        else:
            nout.append(0)
    rmq.put((idv,nout))

flatten = lambda l: [item for sublist in l for item in sublist]

# Try to remove false bubbles


def remove(data):
   
    
    zcount = 0
    idx = -1
    i = 0
    for v in data:
        if v == 0 :
            zcount += 1

            if i == len(data)-1:

                for zz in range(idx,idx+zcount):
                    data[zz] = 2    

            if idx == -1:
                idx = i
        else:

            if zcount > 10:
               for zz in range(idx,idx+zcount):
                    data[zz] = 2                

            zcount = 0
            idx = -1
        i+=1

    for i in range(0,len(data)):
        if data[i] == 2:
            data[i] = 0
        else:
            data[i] = 1
    nout = data

    new2 = np.zeros(len(nout))
    count = 0
    idx = -1
    i = 0


    print("here")

    for v in nout:

        if v == 1:

            if idx == -1:
                idx = i

            count += 1
        else:
            if not idx == -1:
                new2[int((idx + (float(count)/2.0)))] = 1

            count = 0
            idx = -1

        i += 1
        if i % 1000 == 0:
            print((float(i)/len(nout))*100.0)
    return new2


def remove_old(data):
    new = convn(data)


    #print(new[0:1000])
    #quit()
    nout = []
    density = stats.gaussian_kde(new) # x: list of price
    density.set_bandwidth(bw_method=0.000001)

    datah = {}
    rmq = Queue()
    rmlist = []
    arrs = np.array_split(np.array(range(0,len(data))),8)

    idv = 0
    for v in arrs:
        print("spawning")
        p = Process(target=rm, args=(density,rmq,v,idv))
        rmlist.append(p)
        p.start()
        idv += 1

    for p in rmlist:
        job = rmq.get()
        datah[job[0]] = job[1]
    for p in rmlist:
        p.join()

    # Sort data from the multiple processes

    nnout = []
    od = collections.OrderedDict(sorted(datah.items()))
    for k, v in od.items():
        print(k)
        nnout.append(v)

    nout = flatten(nnout)

    count = 0
    idx = -1
    i = 0

    new2 = np.zeros(len(nout))

    for v in nout:

        if v == 1:

            if idx == -1:
                idx = i

            count += 1
        else:
            if not idx == -1:
                new2[int((idx + (float(count)/2.0)))] = 1

            count = 0
            idx = -1

        i += 1

    return new2



# Generate data for the graph
#def data_gen(filename):
 
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

        """if r/CHUNK >= 39382 and r/CHUNK <= 42195:
            if mags == 1:
                print("NOTE")
            else:
                print("0")
            bad = wav[r:r+CHUNK]
            #mags = 0 
        else:
            bad = None
        """

        y.append(mags)
        x.append((epoch-(60*60))+((CHUNK/48e3)*r))
        r+=1
        
        #if r % 1000:
        #    print(r/len(y))
    """
    bd2 = []
    for b in bad:
        for v in b:
            bd2.append(v)
    
    wavfile.write("bad.wav",48000,np.array(bd2))
    """

    q.put((x,y,epoch))


data = {}

lines = []

# Load file with timestamp data
with open('txt') as fin:
    for line in fin: 
        v = line.split(",")
        ep = int(v[0])
        wfile = v[1][1:-2]
        lines.append((wfile,ep))

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

"""
print("here")

import pickle
with open('data.pickle', 'wb') as f:
    pickle.dump(y, f)  
    quit()
"""

y = remove(y)

newy = []
newx = []

count = 0

tval = x[0]

"""
fig = plt.figure()
ax = fig.add_subplot(111)
secs = mdate.epoch2num(newx)
ax.plot(range(len(y))[39382:42195],y[39382:42195],'r-')

#np.sum([40921:42196])
plt.show()
"""



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

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}

matplotlib.rc('font', **font)

fig = plt.figure()
ax = fig.add_subplot(111)
secs = mdate.epoch2num(newx)
ax.plot_date(secs,newy,'r-')

date_fmt = '%d-%m-%y %H:%M:%S'
date_formatter = mdate.DateFormatter(date_fmt)
ax.xaxis.set_major_formatter(date_formatter)
fig.autofmt_xdate()

fig2 = plt.figure()
ax2 = fig2.add_subplot(111)
yhat = signal.savgol_filter(newy, 11, 3) # window size 31, polynomial order 3

ax2.plot_date(secs,yhat,'b-')
ax2.xaxis.set_major_formatter(date_formatter)
fig2.autofmt_xdate()

plt.show()

