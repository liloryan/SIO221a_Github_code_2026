# my_spectrum.py
# Spectrum function for HW5.
import numpy as np
from scipy.stats import chi2

# Compute the power spectral density of a time series.
# The data are split into segments with 50% overlap, the spectra of all segments are averaged.
#
# Inputs:
# data: 1D array, evenly spaced, no NaNs
# dt: sample interval
#
# Optional inputs:
# seg_len: points per segment (default: whole record)
# demean: True = remove the mean of each segment (default True)
# detrend: True = remove a straight line from each segment (default True)
# hann: True = apply a Hanning window to each segment (default True)
#
# Outputs:
# freq: frequencies
# spec: spectral density
# n_seg: number of segments averaged
# dof: degrees of freedom

def my_spectrum(data, dt, seg_len=None, demean=True, detrend=True, hann=True):

    N = len(data)

    # if no segment length is given, use the whole record as one segment
    if seg_len == None:
        seg_len = N

    # frequencies
    df = 1 / (seg_len * dt) # frequency spacing
    n_freq = seg_len // 2 + 1 # from 0 up to Nyquist
    freq = np.arange(n_freq) * df

    # the window
    if hann == True:
        window = np.hanning(seg_len)
    else:
        window = np.ones(seg_len)

    t = np.arange(seg_len)
    step = seg_len // 2 # overlap

    # loop over segments, add up their spectra
    spec_sum = np.zeros(n_freq)
    n_seg = 0
    start = 0

    while start + seg_len <= N:
        seg = data[start : start + seg_len]
        # remove a straight line
        if detrend == True:
            p = np.polyfit(t, seg, 1) # p[0] = slope, p[1] = intercept
            line = p[0] * t + p[1]
            seg = seg - line
        elif demean == True:
            seg = seg - np.mean(seg)
        # multiply by the window
        seg = seg * window
        # fourier transform
        X = np.fft.rfft(seg)
        S = np.abs(X) ** 2 / seg_len * dt
        # one-sided
        S[1:-1] = S[1:-1] * 2
        # the window makes the data smaller
        S = S / np.mean(window ** 2)
        spec_sum = spec_sum + S # add to the total
        n_seg = n_seg + 1
        start = start + step # move to the next segment

    # do average
    spec = spec_sum / n_seg
    dof = 2 * n_seg

    return freq, spec, n_seg, dof

def conf_factors(dof):
    # 95% confidence interval factors (also used in HW3), 0.025 on both sides
    lo = dof / chi2.ppf(0.975, dof)
    hi = dof / chi2.ppf(0.025, dof)
    return lo, hi
