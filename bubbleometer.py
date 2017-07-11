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

data = []
bubbles = []
CHUNK=1024*4
flatten = lambda l: [item for sublist in l for item in sublist]

fig, ax = plt.subplots()
l, = ax.plot([], [], 'bo')
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


def data_gen():
    global rows
    count = 0
    data = wf.readframes(CHUNK)

    allchunks = []

    allallmags = deque(maxlen=10)

    while data != '':
        
        s = np.frombuffer(data,dtype="<i2")

        # play audio
        #stream.write(data)

        data = wf.readframes(CHUNK)
        rows += 1
        fft = np.fft.fft(s)

        fft = fft[0:int(len(fft)/2)]

        mags = []  
        magsl = []   

        allmags = []
                                                               
        c = 0                                                                        
        for v in fft:                                                                                                      
            mag = np.sqrt((v.real**2)+(v.imag**2))  
            allmags.append(mag) 

            if mag > 20000:
                mags.append(count)
                magsl.append(c)                                                                                  
            c += 1                  
        count +=1

        yield [ mags , magsl ]

ani = anim.FuncAnimation(fig, update, data_gen,interval=100,blit=True)
plt.show()


while True:
    sleep(1)
