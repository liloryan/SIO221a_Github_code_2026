import numpy as np
from scipy.signal import detrend as scipy_detrend
from scipy.stats import chi2

def wind_spectrum(data, dt, demean=True, detrend=True, hanning=True,
                  max_gap=6):
    """
    This function calculates an averaged power spectral density using 60 day segments that overlap by 50%.
    
    A limitation of this function is that it cannot detect missing timestamps that are not represented as 'NaN'.

    The function accepts a single dataset or a list of datasets, allowing for the analysis of one or multiple years of wind observations.

    Each dataset is divided into 60 day segments with 50% overlap.
    Short gaps containing NaNs are linearly interpolated, while segments containing longer gaps are excluded.

    The function is able to remove means and/or linear trends, and apply a Hanning window before calculating the Fast Fourier Transform (FFT) if desired.

    Parameters
    ----------
    data : array or list of arrays
        (data is where you put your wind measurements from one or multiple datasets).

    dt : float
        (dt is your sampling interval in days).
        For 10 minute observations, dt = 10/(60*24).

    demean : bool, optional
        (demean will remove the mean from each segment).
        The default is "True", so the function will automatically do this unless specified not to.

    detrend : bool, optional
        (detrend will remove a linear trend from each segment).
        The default is "True", so the function will automatically do this unless specified not to. Detrending also removes the mean.

    hanning : bool, optional
        (hanning wil apply a Hanning window before calculating the Fast Fourier Transform (FFT)).
        The default is "True", so the function will automatically do this unless specified not to.

    max_gap : int, optional
        (max_gap is the maximum integar number of consecutive missing observations to interpolate.
        The default max gap is 6.

    Returns
    -----------
    The function will return a dictionary with the spectral analysis results.
        The dictionary contains the following:
        frequency : frequencies in cycles per day (cpd)
        spectrum : averaged power spectral density
        n_segments : number of valid segments
        degrees_of_freedom : approximate effective degrees of freedom
        err_low : lower 95% confidence interval factor
        err_high : upper 95% confidence interval factor
        ci_lower : lower 95% confidence limits
        ci_upper : upper 95% confidence limits

    Notes
    -----------
    Each dataset is segmented separately to avoid crossing gaps between files.
    Observations within each dataset are assumed to be regularly spaced by dt.

    The confidence intervals use an approximate chi squared method and an overlap correction for the Hanning window.
    """

    #Put the input into a list, which can be one or multiple datasets
    if isinstance(data, list):
        datasets = data
    else:
        datasets = [data]

    #Convert datasets to one dimensional NumPy arrays
    datasets = [np.asarray(d, dtype=float).flatten().copy()
                for d in datasets]

    #Calculate the number of observations in 60 days
    pseg = int(round(60 / dt))

    #Set 50% overlap between consecutive segments
    step = pseg // 2

    #Calculate FFT frequencies and frequency resolution
    f = np.fft.rfftfreq(pseg, d=dt)
    df = 1 / (pseg * dt)

    #Create a window and correct for its effect on spectral power if necessary
    if hanning:
        w = np.hanning(pseg)
        w = w / np.sqrt(np.mean(w**2))
    else:
        w = np.ones(pseg)

    #Store the spectrum calculated from each valid segment
    spectra = []

    #Process each dataset separately
    for d in datasets:

        #Find indices containing valid observations
        valid = np.where(np.isfinite(d))[0]

        #Skip datasets with fewer than two valid observations
        if len(valid) < 2:
            continue

        #Examine gaps between consecutive valid observations
        for a, b in zip(valid[:-1], valid[1:]):

            #Number of missing observations between valid values
            gap = b - a - 1

            #Linearly interpolate gaps no longer than max_gap
            if 0 < gap <= max_gap:
                d[a+1:b] = np.interp(
                    np.arange(a+1, b),
                    [a, b],
                    [d[a], d[b]]
                )

        #Divide the dataset into 60 day overlapping segments
        for s in range(0, len(d) - pseg + 1, step):

            #Extract a copy of the current segment
            segment = d[s:s+pseg].copy()

            #Exclude segments containing unresolved missing values
            if not np.isfinite(segment).all():
                continue

            #Remove a linear trend, which also removes the mean
            if detrend:
                segment = scipy_detrend(segment)

            #If not detrending, optionally remove the mean
            elif demean:
                segment = segment - np.mean(segment)

            #Apply the desired window and calculate the FFT
            X = np.fft.rfft(segment * w)

            #Calculate the power of each Fourier coefficient
            tmp = np.abs(X)**2 / pseg**2

            #Double positive frequency power to account for negative frequencies, excluding zero and Nyquist
            tmp[1:-1] *= 2

            #Convert spectral power into power spectral density
            tmp = tmp / df

            #Store this segment's spectrum
            spectra.append(tmp)

    #Count valid segments
    M = len(spectra)

    #Stop if there are no valid segments to average
    if M == 0:
        raise ValueError("No valid segments found.")

    #Average the spectra across all valid segments
    Sc = np.mean(spectra, axis=0)

    #Estimate effective degrees of freedom
    if hanning:
        nu = 2 * M * 0.9
    else:
        nu = 2 * M

    #Calculate approximate 95% confidence interval factors
    err_low = nu / chi2.ppf(0.975, nu)
    err_high = nu / chi2.ppf(0.025, nu)

    #Apply confidence interval factors to the averaged spectrum
    ci_lower = Sc * err_low
    ci_upper = Sc * err_high

    #Display the number of segments included in the average
    print(f"Total valid segments: {M}")

    #Return a dictionary that has the spectral analysis results
    return {
        'frequency': f,
        'spectrum': Sc,
        'n_segments': M,
        'degrees_of_freedom': nu,
        'err_low': err_low,
        'err_high': err_high,
        'ci_lower': ci_lower,
        'ci_upper': ci_upper
    }
