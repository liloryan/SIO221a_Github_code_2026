from scipy.signal import detrend
import xarray as xr 
import numpy as np 
from scipy import signal

def compute_spectra(data_array,sample_interval, dt_min = 10, detrend_data = True, hanning_window = False):
     
    '''  This function takes a data array that has been segmented already (shape: points_per_segment x number_of_segments),
         the time between each point in minutes, and the length of the segment in days. It also takes two booleans that
         determine whether or not to detrend the data (True by default) and whether to apply a Hanning window before the FFT.
         Every step works along axis 0 (time), so all segments are done at once.
         
         Input: dataarray, dt_min (time step in minutes), length_of_array_in_days (length of chunking of data), detrend_data(boolean,True = yes, automatic), 
                hanning_window (boolean,False = no automatic)
         
         Output: spectra, positive frequencies
    '''
    length_of_array_in_days = sample_interval #sample interval for our data chunk is 60 days
    dt = dt_min/ (60*24) #given in minutes -- > days
    N = int(length_of_array_in_days * 24 * 60 / dt_min) #number of points
    
    if detrend_data == True:  # use boolean to decide if we need to detrend the data
        print('detrending data')
        data = detrend(data_array, axis=0) #detrend using scipy function
        
    else: 
        print('no detrending of data')
        data = data_array
    
    frequencies = np.fft.fftshift(np.fft.fftfreq(N, d=dt)) #calculate frequencies
    print(f'fundamental freqency {np.min(np.abs(frequencies[frequencies != 0]))}') #sanity checks when computing
    print(f'nyquist freqency {np.max(np.abs(frequencies))}') #sanity checks when computing
    
    if hanning_window == False:  #check if there is a hanning window applied if not proceed withowed window
        print('computing FFT without Hanning Window')
        coefficient_amplitudes = np.fft.fftshift(np.fft.fft(data, axis=0), axes=0)/N
        
    else: 
        print('computing FFT with Hanning Window')
        window = signal.windows.hann(N)
        ## recall that we need to scale the data for windowing, multiplting the coeffs by sqrt(8/3) recovers the energy to satisfy parsevals therorem 
        coefficient_amplitudes = np.sqrt(8/3) * np.fft.fftshift(np.fft.fft(data * window[:, None], axis=0), axes=0)/N
        
    ## NOW APPLY PARSEVALS THEOREM AND GET THE ONLY THE RELEVANT REAL DATA
    df = 1 / length_of_array_in_days    # 1/60 cpd
    spectra = 2 * (np.abs(coefficient_amplitudes[frequencies > 0]) ** 2) / (df)
    pos_frequencies = frequencies[frequencies > 0]

        
    return spectra, pos_frequencies