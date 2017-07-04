#!/usr/bin/python3 

import pyaudio
import wave
import sys
import struct 
import numpy as np
import time

CHUNK = 1024*5

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')
print("chans ",wf.getnchannels())
# instantiate PyAudio (1)
p = pyaudio.PyAudio()

"""
# open stream (2)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# read data
data = wf.readframes(CHUNK)
"""


bubbles = []


def callback(in_data, frame_count, time_info, status):
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




# open stream using callback (3)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)

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
""""
quit()






# play stream (3)
while len(data) > 0:

    s = np.frombuffer(data,dtype="<i2")
    fft = np.fft.fft(s)
   
    mags = []
    c = 0
    for v in fft:
        if c > 70 and c < 100:
            mag = np.sqrt((v.real**2)+(v.imag**2))
            mags.append(mag)
        c += 1
    
    if (np.sort(mags)[::-1][0]) > 9000:
        print("bubble")
    else:
        print("  ")
    stream.write(data)
    data = wf.readframes(CHUNK)

# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()

"""

