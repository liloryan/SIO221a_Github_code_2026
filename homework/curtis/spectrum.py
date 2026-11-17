# This script defines a function to compute spectral density of an evenly spaced time series
# Author: Jon Curtis

import numpy as np
from scipy.signal import detrend as sp_detrend


def spectrum(x, dt, detrend=True, hanning=True):
    """
    Spectral density of an evenly spaced time series (no NaNs).

    x: data
    dt: sample interval
    detrend: remove mean and linear trend first
    hanning: apply a Hanning window (rescaled to preserve variance)

    Returns f (0 to Nyquist) and S, normalized so sum(S) * df = variance.
    """
    # check for NaNs
    x = np.asarray(x, dtype=float)
    if np.any(np.isnan(x)):
        raise ValueError('x contains NaNs; fill gaps before computing the spectrum')
    N = len(x)

    # remove mean and linear trend
    if detrend:
        x = sp_detrend(x)

    # taper the ends to zero, and keep the window's mean square to undo its variance loss
    if hanning:
        w = np.hanning(N)
        x = x * w
        w_norm = np.mean(w**2)
    else:
        w_norm = 1.0

    # FFT of real data: only frequencies 0 ... Nyquist are needed
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(N, d=dt)

    # scale |X|^2 into spectral density
    S = np.abs(X)**2 * dt / N / w_norm

    # fold the negative frequencies onto the positive ones (except f = 0, and Nyquist when N is even)
    if N % 2 == 0:
        S[1:-1] *= 2
    else:
        S[1:] *= 2

    return f, S
