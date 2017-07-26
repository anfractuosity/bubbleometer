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
from scipy import signal
import matplotlib.pyplot as plt
from bubbleometer import *

data = []
bubbles = []
CHUNK=1024*2

flatten = lambda l: [item for sublist in l for item in sublist]
f, (ax1, ax2) = plt.subplots(2, sharex=True, sharey=False)
l, = ax1.plot([], [], 'bo')
l2, = ax2.plot([], [], 'r-')
p = pyaudio.PyAudio()

wf = wave.open(sys.argv[1], 'rb')
print("chans ",wf.getnchannels())

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

olddatax = []
olddatay = []
rows = 0

def update(newdata):
    rows = newdata[2]
    olddatax.append(newdata[1])
    olddatay.append(newdata[0])

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
    for v in olddatay:

        if len(v) > 24 and max(v) > 50:
            newy.append(1)
        else: 
            newy.append(0)
        newx.append(c)
        c=c+1
    ax2.set_ylim(0,1)
    l2.set_xdata(newx)
    l2.set_ydata(remove(newy))
    return l,l2,

def data_gen():
    count = 0
    data = wf.readframes(CHUNK)

    while data != '':
        
        s = np.frombuffer(data,dtype="<i2")
        stream.write(data)
        data = wf.readframes(CHUNK)
        mags , magsl = fft_process(s,count)   
        count +=1

        yield [ mags , magsl, count ]

ani = anim.FuncAnimation(f, update, data_gen,interval=0,blit=True)
plt.show()

while True:
    sleep(1)
