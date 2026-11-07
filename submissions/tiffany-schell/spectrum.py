from scipy.signal import detrend
import numpy as np

def spectrum(data, dt, demean_data=True, detrend_data=True, hanning=True):
    '''
    A function that computes the spectrum from input data.
    
    data: Make sure to pass in a dataframe of pre-segmented data, where each
    column represents one segment
    
    dt: Sampling interval in day
    
    demean_data: Whether or not to demean the data (recommended to do so)
    
    detrend_data: Whether or not to detrend the data (recommended to do so)
    
    hanning: Whether or not to apply a Hanning window (recommended to do so)
    '''
    N = len(data) # number of observations per segment
    f = np.fft.rfftfreq(N, d=dt) # frequency bins

    ### Whether to demean, detrend, both or neither
    if detrend_data:
        seg = detrend(data, axis=0, type='linear') # demean and detrend
        if not demean_data: # only detrend
            seg += np.mean(data, axis=0) # restore original mean
    elif demean_data: # only demean
        seg = detrend(data, axis=0, type='constant')
    else: # don't demean or detrend
        seg = data

    ### Whether or not to apply a Hanning window
    if hanning:
        w = np.hanning(N).reshape(N,1) # Hanning window of length N
        scale = np.sqrt(8/3)
        X = np.fft.fft(seg*w*scale, axis=0) # apply window & scale, fft

    else: # boxcar
        X = np.fft.fft(seg, axis=0)

    ### Compute spectrum
    S = np.abs(X[:N//2+1])**2 / N**2 # compute power at nonnegative frequencies
    # next, double power except at zero and Nyquist frequencies
    if N % 2 == 0: # even N: last bin is Nyquist (don't double it)
        S[1:-1, :] *= 2
    else: # odd N: last bin is not Nyquist (double it)
        S[1:, :] *= 2
    S = S / (1 / (dt*N)) # convert power to spectral density
    S_mean = np.mean(S, axis=1) # axis=1 averages at each frequency

    return f, S_mean # spectral density at each frequency
