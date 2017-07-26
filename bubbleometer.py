import numpy as np
from itertools import tee
from scipy.signal import butter, lfilter
from matplotlib.pylab import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import datetime as dt
import scipy.signal as signal

flatten = lambda l: [item for sublist in l for item in sublist]


def timestampdata():
    lines = []

    # Load file with timestamp data
    with open('wav/txt') as fin:
        for line in fin: 
            v = line.split(",")
            ep = int(v[0])
            wfile = v[1][1:-2]
            lines.append(("wav/"+wfile,ep))

    return lines

def getbubblesperminute(x,y):

    newy = []
    newx = []
    count = 0
    tval = x[0]

    # Extract bubbles per minute data
    for i in range(0,len(x)):

        if y[i] == 1:
            count += 1

        if x[i] > tval + (60):
            newy.append(count)
            newx.append(tval)
            tval = x[i]
            count = 0

    return newx, newy

# Generate graphs of bubbles / min against time
def graphit(newx,newy):

    # Enlarge font
    font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}
    matplotlib.rc('font', **font)
    
    # Standard graph
    fig = plt.figure()
    ax = fig.add_subplot(111)
    secs = mdate.epoch2num(newx)
    ax.plot_date(secs,newy,'r-')

    date_fmt = '%d-%m-%y %H:%M:%S'
    date_formatter = mdate.DateFormatter(date_fmt)
    ax.xaxis.set_major_formatter(date_formatter)
    fig.autofmt_xdate()

    # Filtered graph
    fig2 = plt.figure()
    ax2 = fig2.add_subplot(111)
    yhat = signal.savgol_filter(newy, 11, 3) # window size 31, polynomial order 3

    ax2.plot_date(secs,yhat,'b-')
    ax2.xaxis.set_major_formatter(date_formatter)
    fig2.autofmt_xdate()

    plt.show()

# Try to remove false bubbles, remove continous 1s and pick first
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
            if count > 7:
                zz = i

            for i2 in range(zz,zeroidx):
                ny[i2] = 0
            
            i = zeroidx
    return ny

# Try to remove false bubbles using simple 'break' detection
def remove_break(data):

    zcount = 0
    idx = -1
    i = 0

    for v in data:
        if v == 0 :
            zcount += 1

            if i == len(data)-1:

                for zz in range(idx,idx+zcount):
                    data[zz] = 2    

            if idx == -1:
                idx = i
        else:

            if zcount > 10:
               for zz in range(idx,idx+zcount):
                    data[zz] = 2                

            zcount = 0
            idx = -1
        i+=1

    for i in range(0,len(data)):
        if data[i] == 2:
            data[i] = 0
        else:
            data[i] = 1
    nout = data

    new2 = np.zeros(len(nout))
    count = 0
    idx = -1
    i = 0

    for v in nout:
        if v == 1:
            if idx == -1:
                idx = i
            count += 1
        else:
            if not idx == -1:
                new2[int((idx + (float(count)/2.0)))] = 1
            count = 0
            idx = -1
        i += 1
        #if i % 1000 == 0:
        #    print((float(i)/len(nout))*100.0)

    return new2

# Try to remove false bubbles using gaussian kernel
def remove_old(data):
    new = convn(data)
    nout = []
    density = stats.gaussian_kde(new) # x: list of price
    density.set_bandwidth(bw_method=0.000001)

    datah = {}
    rmq = Queue()
    rmlist = []
    arrs = np.array_split(np.array(range(0,len(data))),8)

    idv = 0
    for v in arrs:
        print("spawning")
        p = Process(target=rm, args=(density,rmq,v,idv))
        rmlist.append(p)
        p.start()
        idv += 1

    for p in rmlist:
        job = rmq.get()
        datah[job[0]] = job[1]
    for p in rmlist:
        p.join()

    # Sort data from the multiple processes
    nnout = []
    od = collections.OrderedDict(sorted(datah.items()))
    for k, v in od.items():
        print(k)
        nnout.append(v)

    nout = flatten(nnout)

    count = 0
    idx = -1
    i = 0

    new2 = np.zeros(len(nout))

    for v in nout:

        if v == 1:

            if idx == -1:
                idx = i

            count += 1
        else:
            if not idx == -1:
                new2[int((idx + (float(count)/2.0)))] = 1

            count = 0
            idx = -1

        i += 1

    return new2

def fft_process(data,count):
    fft = np.fft.fft(data)
    fft = np.abs(fft[0:int(len(fft)/2)])

    mags = []  
    magsl = [] 
    c = 0                                                                        
        
    for v in fft:                                                                                                      
        if v > 30000:
            mags.append(c)  
            magsl.append(count)  
        c += 1 

    return mags , magsl


def parzen(x,data):
    sig = 5.0
    a = 1.0/(float(len(data)*((2*np.pi)**0.5)*sig))
    b = 0.0
    for v in data:
        b+=math.exp(-((x-v)**2/(2*sig**2)))
    return a * b

def window(iterable, size):
    iters = tee(iterable, size)
    for i in range(1, size):
        for each in iters[i:]:
            next(each, None)
    return zip(*iters)

def convn(data):
    d = []

    for i in range(len(data)):
        if data[i] == 1:
            d.append(i)
        
    return d

def rm(density,rmq,v,idv):
    nout = []
    for i in v:
        if density(i) > 0.00001:
            nout.append(1)
        else:
            nout.append(0)
    rmq.put((idv,nout))

# From https://stackoverflow.com/questions/12093594/how-to-implement-band-pass-butterworth-filter-with-scipy-signal-butter
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y
