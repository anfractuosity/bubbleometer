#!/usr/bin/python3 
import pyaudio
import wave
import sys
import struct 
import numpy as np
import time
import glob
import matplotlib.pyplot as plt
import _thread
import matplotlib.pyplot as plt
import matplotlib.animation as anim
from time import sleep
from collections import deque
import scipy.io.wavfile as wavfile
import math

data = []
bubbles = []
CHUNK=512

from scipy import signal

from scipy.signal import butter, lfilter
from scipy.signal import filtfilt

import matplotlib.pyplot as plt
from bubbleometer import *

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

flatten = lambda l: [item for sublist in l for item in sublist]


f, (ax1, ax2) = plt.subplots(2, sharex=True, sharey=False)

l, = ax1.plot([], [], 'bo')
l2, = ax2.plot([], [], 'r-')

olddatax = []
olddatay = []

olddatax2 = []
olddatay2 = []
rows = 0

fs = 48000.0
lowcut = 800.0
highcut = 3000.0

from scipy.signal import butter, lfilter

wav = wavfile.read(sys.argv[1])[1]
bp = butter_bandpass_filter(wav, lowcut, highcut, fs, order=6)
b, a = butter(1,100.0/(0.5*48e3), 'low')
y = filtfilt(b, a, abs(bp))

def update(newdata):
    global rows

    olddatax.append(newdata[2])
    olddatay.append(newdata[3])

    olddatax2.append(newdata[0])
    olddatay2.append(newdata[1])

    xx = flatten(olddatax)
    yy = flatten(olddatay)

    ax1.set_xlim(0, rows)
    
    my = 0
    if len(yy) == 0:
        my = 10
    else:
        my = max(yy)  

    ax1.set_ylim(0, 1024)
    l.set_xdata(xx)
    l.set_ydata(yy)

    newy = []
    newx = []

    c = 0
    for v in olddatay2:
        newy.append(v)
        newx.append(c)
        c=c+1
  
    ax2.set_ylim(0,1)
    l2.set_xdata(newx)
    l2.set_ydata(remove_break(newy))
    return l,l2,


def data_gen():
    global rows
    data = y[0:CHUNK]
    bpd = bp[0:CHUNK]
    r = 0
    count = 0
    while len(data) == CHUNK:
        s = data
        fft = np.fft.fft(bpd)
        fft = np.abs(fft[0:1024])

        mags = []  
        magsl = []  
        c = 0
        for v in fft:                                                                                                      
            if v > 20000:
                mags.append(count)
                magsl.append(c)                                
                #mags.append(mag)                                                     
            c += 1          
        integ = np.trapz(s)
        if integ > 50000:
            mag = 1
        else:
            mag = 0

        val = count
        count +=1
        rows = count
        r += CHUNK
        data = y[r:r+CHUNK]
        bpd = bp[r:r+CHUNK]
        
        stream.write(wav[r:r+CHUNK]) 
                                  
        yield [ val , mag, mags,magsl ]

ani = anim.FuncAnimation(f, update, data_gen,interval=0,blit=True)
plt.show()


while True:
    sleep(1)

