#!/usr/bin/python3 

import pyaudio
import wave
import sys
import struct 
import numpy as np

CHUNK = 1024

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')
print("chans ",wf.getnchannels())
# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# open stream (2)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# read data
data = wf.readframes(CHUNK)

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

