import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
import os
from netCDF4 import Dataset
import pandas as pd
import xarray as xr
from scipy.signal import detrend
from scipy.stats import chi2 as chi2_dist

def detHan(data, samples, interval = 10/(60*24), detrended = True):
    """helper function to handle hanning windowing """
    if detrended == False:
        deT = detrend(data)
    else:
        deT = data
    M = samples
    p = len(data)//M 
    fn = 1/2/interval
    w = np.hanning(p) # matches MATLAB's hann, not its hanning
    scale = np.sqrt(8/3) # put back the energy the taper removed
    starts = np.arange(0, len(data) - p + 1, p//2)
    Sc = np.zeros((p//2 + 1, len(starts)))
    for k, s in enumerate(starts):
        sgi = detrend(deT[s:s+p])
        Xc = np.fft.fft(sgi*w*scale)
        tmp = np.abs(Xc[:p//2+1])**2 / p**2; tmp[1:-1] *= 2
        Sc[:, k] = tmp/(1/(interval*p))
    Sc = np.mean(Sc, axis=1)
    fbv = np.arange(0, fn + 1/(interval*p)/2, 1/(interval*p))

    #uncertainties
    nu = 2*M # 2 times M segments
    err_high = nu/chi2_dist.ppf(.05/2, nu)
    err_low = nu/chi2_dist.ppf(1 - .05/2, nu)
    indf = int(np.argmax(fbv > 12)) # remove low frequency noise


    coords = [fbv, Sc]
    uncert = [err_high, err_low, indf]
    return coords, uncert

def nonHan(data, interval = 10/(60*24)):
    """helper function to handle non-Hanning cases"""
    a = np.fft.fft(data)
    N = len(data)
    amp = np.abs(a[:(N+1)//2 + 1])**2 

    dt = interval
    T = dt*N
    df = 1/T
  
    f = np.arange(0, ((N + 1) // 2 + 1) * df, df) 

    amp = amp / N**2 
    amp[1:-1] = amp[1:-1]*2 
    amp = amp / df

    #uncert
    nu = 2 # 2 times M segments (only one segment)
    err_high = nu/chi2_dist.ppf(.05/2, nu)
    err_low = nu/chi2_dist.ppf(1 - .05/2, nu)

    indf = int(np.argmax(f > 12)) # remove low frequency noise
    coords = [f, amp]
    uncert = [err_high, err_low, indf]
    return coords, uncert

def segmenter(x, window=8640, step =4320): #got numbers by converting 30 and 60 days into number of data points
    arr = np.lib.stride_tricks.sliding_window_view(x, window_shape=window)[::step]
    return arr

def getDiff(data):
    "returns data interval in days"
    diffs= []
    for i in range(1,len(data)):
        diffs.append(data[i]-data[i-1])
    diffs = np.array(diffs)
    return diffs 

def spec(data, samp_interval, det= True, hanning = False):
    """interval should be given in days
    returns a list containing the coordinates of the frequency and the corresponding cycles per day and the uncertainty for the data
    """
    #get interval between points
    interval = getDiff(data)[0]
    #find how many samples are in the dataset
    #for 50% overlap 
    window = samp_interval/interval
    step = samp_interval/2
    samples = len(segmenter(data, window= window, step = step))
    if hanning == True:
        return detHan(data, samples, interval, det)
    else:
        if det == True:
            data = detrend(data)
        return nonHan(data, interval)