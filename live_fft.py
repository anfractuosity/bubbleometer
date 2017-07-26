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

data = []
bubbles = []
CHUNK=1024*2

from scipy import signal


import matplotlib.pyplot as plt


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
            for i2 in range(zz,zeroidx):
                ny[i2] = 0
            
            i = zeroidx

    return ny

def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result[int(result.size/2):]

def update(newdata):
    global rows
    olddatax.append(newdata[0])
    olddatay.append(newdata[1])
    #ax.set_ylim(0,max(olddata))
    #ax.set_xlim(0, int(len(olddata)*1.2))
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
    global rows
    count = 0
    data = wf.readframes(CHUNK)

    allchunks = []

    allallmags = deque(maxlen=10)

    while data != '':
        
        s = np.frombuffer(data,dtype="<i2")

        """ 
        for v in s:
            allchunks.append(v)
        

        sig = allchunks
        autocorr = signal.fftconvolve(sig, sig[::-1], mode='full')

        fig, (ax_orig, ax_mag) = plt.subplots(2, 1)
        ax_orig.plot(sig)
        ax_orig.set_title('White noise')
        ax_mag.plot(np.arange(-len(sig)+1,len(sig)), autocorr)
        ax_mag.set_title('Autocorrelation')
        fig.tight_layout()
        fig.show()
        """

        """c = autocorr(allchunks)

        fig2, ax2 = plt.subplots()
        l2, = ax2.plot(range(len(c)),c, 'r-')
        fig2.show()
        """
         
        stream.write(data)
        data = wf.readframes(CHUNK)
        rows += 1
        fft = np.fft.fft(s)

        fft = np.abs(fft[0:int(CHUNK/2)])

        mags = []  
        magsl = []   

        allmags = []
                                                               
        c = 0                                                                        
        for v in fft:                                                                                                      
            if v > 20000:
                mags.append(count)
                magsl.append(c)                                
                #mags.append(mag)                                                     
            c += 1                  
        count +=1

        """
        allallmags.append(allmags)

        o = None
        for al in allallmags:
            for al2 in allallmags:   
                if al != al2:          
                    c = np.corrcoef(al,al2)[0][1]
                    print(c)
        """

        #print("----------")
        """
        print(np.sort(mags)[::-1][0])                          
                     
        if (np.sort(mags)[::-1][0]) > 4000:  
            print("bubbles")                                        
            yield mags    
        else:
            print("  ")
        """

        yield [ mags , magsl ]

       

ani = anim.FuncAnimation(f, update, data_gen,interval=0,blit=True)
plt.show()


while True:
    sleep(1)
quit()
"""
def data_listener(x,y):

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    fig1 = plt.figure()

    data = np.random.rand(2, 25)
    ln, = plt.plot([], [], 'r-')
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.xlabel('x')
    plt.title('test')

    def update(l):
        y = [ 1 ]
        x = range(len(y))
        print("update", len(y))
        #ax.clear()
        #ax.plot(x, y)
        ln.set_data(x, y)

        return ln,

    a = anim.FuncAnimation(fig, update,fargs=(l), repeat=False, blit=True)                                                      
    plt.show()

    while True:
        nop = 1
        sleep(1)
        print("sleep")
_thread.start_new_thread( data_listener, ("Thread-1", 2, ) )
"""




if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

# instantiate PyAudio (1)
p = pyaudio.PyAudio()
good = []


"""
# Training
for f in glob.glob("train/bubbles*.wav"):
    wf = wave.open(f,'rb')
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

    allwav = []

    data = wf.readframes(CHUNK)
    while len(data) > 0:
        s = np.frombuffer(data,dtype="<i2") 
        allwav.append(s)
        data = wf.readframes(CHUNK)
        
    allwav = flatten(allwav)
    print(allwav)
    quit()

    stream.stop_stream()
    stream.close()
"""

# instantiate PyAudio (1)


def callback_simple(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    s = np.frombuffer(data,dtype="<i2")                                          
    fft = np.fft.fft(s)                                                          
    mags = []                                                                    
    c = 0                                                                        
    for v in fft:                                                                
        if c > 70 and c < 100:                                                   
            mag = np.sqrt((v.real**2)+(v.imag**2))                               
            mags.append(mag)                                                     
        c += 1                                                                   
    if (np.sort(mags)[::-1][0]) > 10000:                                          
        print("bubble")    
        bubbles.append(time.time()*1000)  
                          
    else:                                                                        
        print("  ")        


    return (data, pyaudio.paContinue)

def callback_corr(in_data, frame_count, time_info, status):

    data = wf.readframes(frame_count)
    s = np.frombuffer(data,dtype="<i2")                                          
    fft = np.fft.fft(s)                                                          

    mags = [np.sqrt((v.real**2)+(v.imag**2)) for v in fft ]
    print(mags)
                                                           
    return (data, pyaudio.paContinue)


# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback_simple)

# start the stream (4)
stream.start_stream()

# wait for stream to finish (5)
while stream.is_active():
    time.sleep(0.1)

# stop stream (6)
stream.stop_stream()
stream.close()
wf.close()
# close PyAudio (7)
p.terminate()
print(bubbles)
