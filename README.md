# bubbleometer

I developed a very simplistic algorithm to detect bubbles via audio from an airlock during fermentation. The airlock is simply filled with water, which makes bubbles and therefore bubble sounds, when CO2 passes through. 

See https://www.anfractuosity.com/projects/bubbleometer/ for more information.

# Requirements

* Python3
* Matplotlib
* Numpy
* Scipy
* Pyaudio - for live graphing demos

# Example

## On the PC doing the recordings run:
./record.sh
./timestamp_recordings.sh

## Once you have the recordings:

Place .wav files in folder called wav/ in the same directory as these python scripts.
Copy the file generated from timestamp_recordings.sh into the wav/ directory.

Try bubbleometer_fft.py or bubbleometer_envelope.py to generate graphs.

