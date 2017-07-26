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
import matplotlib.pyplot as plt
from bubbleometer import *

data = []
bubbles = []
CHUNK=512

wf = wave.open(sys.argv[1], 'rb')
p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)
f, (ax1) = plt.subplots(1, sharex=True, sharey=False)
l1, = ax1.plot([], [], 'r-')

olddatax = []
olddatay = []
wav = wavfile.read(sys.argv[1])[1]
y,bp = filter_wav(wav)

def update(newdata):
    
    olddatax.append(newdata[1])
    olddatay.append(newdata[0])
    ax1.set_ylim(0,1)
    ax1.set_xlim(0,newdata[1])
    
    l1.set_xdata(olddatax)
    l1.set_ydata(remove(olddatay))
    
    return l1,


def data_gen():
    r = 0
    row = 0
    data = y[0:CHUNK]
    while len(data) == CHUNK:
        mag = integrate(data)
        r += CHUNK
        row += 1
        data = y[r:r+CHUNK]
        stream.write(wav[r:r+CHUNK]) 
        yield [ mag, row ]

ani = anim.FuncAnimation(f, update, data_gen,interval=0,blit=True)
plt.show()


while True:
    sleep(1)

