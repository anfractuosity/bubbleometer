#!/usr/bin/python3 

import pyaudio
import wave
import sys
import struct 
import numpy as np
import time
import glob
import _thread

import matplotlib.pyplot as plt
import matplotlib.animation as anim

from time import sleep
from collections import deque
from scipy import signal

data = []
bubbles = []
CHUNK=1024*4

flatten = lambda l: [item for sublist in l for item in sublist] 

fig, ax = plt.subplots()
l, = ax.plot([], [], 'bo')

# Start pyaudio and load wav
p = pyaudio.PyAudio()
wf = wave.open(sys.argv[1], 'rb')
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

olddatax = []
olddatay = []
rows = 0

## Plot data on the graph
def update(newdata):

    global rows
    olddatax.append(newdata[0])
    olddatay.append(newdata[1])
    xx = flatten(olddatax)
    yy = flatten(olddatay)

    ax.set_xlim(0, rows)
    
    my = 0
    if len(yy) == 0:
        my = 10
    else:
        my = max(yy)  

    ax.set_ylim(0, my)
    l.set_xdata(xx)
    l.set_ydata(yy)
    return l,


## Generate data for the graph
def data_gen():
    
    global rows
    data = wf.readframes(CHUNK)

    while data != '':
        
        s = np.frombuffer(data,dtype="<i2")
        ## play audio
        #stream.write(data)
        data = wf.readframes(CHUNK)
        
        fft = np.fft.fft(s)
        fft = fft[0:int(len(fft)/2)]

        mags = []  
        magsl = []   

        c = 0                                                                        
        
        for v in fft:                                                                                                      
            mag = np.sqrt((v.real**2)+(v.imag**2))  
            if mag > 20000:
                mags.append(rows)
                magsl.append(c)   
                                                                               
            c += 1                  
        rows += 1

        yield [ mags , magsl ]

## Use animation, so we get a live graph
ani = anim.FuncAnimation(fig, update, data_gen,interval=100,blit=True)
plt.show()

## Need to keep main thread alive
while True:
    sleep(1)
