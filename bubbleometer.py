import numpy as np

# Try to remove false bubbles
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

def fft_process(data,count):
    fft = np.fft.fft(data)
    fft = np.abs(fft[0:int(len(fft)/2)])

    mags = []  
    magsl = [] 
    c = 0                                                                        
        
    for v in fft:                                                                                                      
        if v > 40000:
            mags.append(count)  
            magsl.append(c)  
        c += 1 

    return mags , magsl
