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

data = []
bubbles = []
CHUNK=1024

flatten = lambda l: [item for sublist in l for item in sublist]

#fig, ax = plt.subplots()
#line, = plt.plot([], [], 'r-')
#ax.set_ylim(0, 1)

#fig = plt.figure()
fig, ax = plt.subplots()

#plt.ylim(0, 1)
#plt.xlim(0, 1)
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

def update(newdata):
    olddatax.append(newdata[0])
    olddatay.append(newdata[1])
    #ax.set_ylim(0,max(olddata))
    #ax.set_xlim(0, int(len(olddata)*1.2))
    xx = flatten(olddatax)
    yy = flatten(olddatay)

    ax.set_xlim(0, int(len(xx)*1.2))
    
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
    count = 0
    data = wf.readframes(CHUNK)
    while data != '':
        
        s = np.frombuffer(data,dtype="<i2") 
        stream.write(data)
        data = wf.readframes(CHUNK)
        
        fft = np.fft.fft(s)

        fft = fft[0:int(len(fft)/2)]

        mags = []  
        magsl = []   
                                                               
        c = 0                                                                        
        for v in fft:                                                                                                      
            mag = np.sqrt((v.real**2)+(v.imag**2))   

            if mag > 40000:
                mags.append(count)
                magsl.append(c)                                
                #mags.append(mag)                                                     
            c += 1                  
        count +=1
        """
        print(np.sort(mags)[::-1][0])                          
                     
        if (np.sort(mags)[::-1][0]) > 4000:  
            print("bubbles")                                        
            yield mags    
        else:
            print("  ")
        """

        yield [ mags , magsl ]

       

ani = anim.FuncAnimation(fig, update, data_gen,interval=100,blit=True)
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
