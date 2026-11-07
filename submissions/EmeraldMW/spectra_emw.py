import numpy as np
import pandas as pd
import xarray as xr
from scipy.signal import detrend


def segment_spectra(data, deltat, detrend_data=True, hanning=True):
    """
    This is a function built for an array of data. It performs 60 day segments on the data and then performs spectral analysis on the segments.
    Returns a power spectrum for all given variables as well as a frequency to be used for the x axis.
    data - data that is wanted to be segmented and analyzed
    deltat - time interval between sample points in days
    Detrend_data - detrends the data    Hanning - applies a hanning window
    It presumes that any gaps have already been interpolated. (mostly as preparing for interpolation can be very dependent on where the data is sourced from)
    Additionally it expects that there is a detectable datetime dimension as the format for time differs from data source to data source. It should be labeled 'time', 'date', or 'datetime'
    """

    #Have to detect where the datetime is located as datetime was not stated as an input I can ask for. I am presuming the 60 day segments is still wanted as nothing else was stated as being wanted
    #I feel very clever for coming up with this
    if isinstance(data, (pd.DataFrame, pd.Series)): #Check if pandas
        if isinstance(data.index, pd.DatetimeIndex): #Check if index is datetime
            time = data.index.name #Grab index name
            timeindex = True #Time is in the index
        elif isinstance(data, pd.DataFrame): #Make sure dataframe
            for col in data.columns: #check each column
                if col.lower() in ['time','date', 'datetime']: #The use of .lower() was the best way I could find to remove case sensitivity
                    if pd.api.types.is_datetime64_any_dtype(data[col]): #FOUND FUNCTION TO DETECT DATETIME
                        time = col #Grab Column name
                        timeindex = False #Time is not an index
    elif isinstance(data, (xr.Dataset, xr.DataArray)): #If it's something made with xarray instead
        for coord in data.coords:
          if 'time' in coord.lower() or 'date' in coord.lower() or 'datetime' in coord.lower(): #look for time in the coords
              if pd.api.types.is_datetime64_any_dtype(data[coord]): #hopefully this still works here too
                  time = coord #Grab coordinate name
    else:
        print('Data needs datetime information or is neither dataframe, dataarray, nor dataset.')
        return None
    #HOW DID THIS ACTUALLY WORK 

    #Segment time!
    segment = []
    segments = []
    start = pd.Timestamp(data[time].min().values)
    end = pd.Timestamp(data[time].max().values)
    segstart = start #this is the moving start used for each segment

    while segstart + pd.Timedelta(days=60) <= end: #Create loop that will end when segments reach endtime
        segend = segstart + pd.Timedelta(days=60) #define the end of our segment by the start of it +60 days
        if isinstance(data, (pd.DataFrame, pd.Series)): #This next part is different between Pandas and xarray
            if timeindex: #If time was in the index
                seg = data.loc[str(segstart) : str(segend)] #Use a locator
            else: #If time was in a column
                seg = data[(data[time] >= segstart) & (data[time] <= segend)] #Find using a mask
        elif isinstance(data, (xr.Dataset, xr.DataArray)): #If xarray
            seg = data.sel(**{time: slice(str(segstart), str(segend))}) #select a slice between segstart and segend. #This might break or not function with datetime detection but AAAAAAAAAA
        segstart = segstart + pd.Timedelta(days=30) #Add thirty days so that there's 50% overlap with previous segment
        segments.append(seg)
    
    #Detect if dataframe or dataarray and find variables accordingly. Kind of unecessary since I already do it but whatever reusing code
    if isinstance(segments[0], pd.DataFrame): #If Pandas
        variables = list(segments[0].columns) 
    elif isinstance(segments[0], xr.DataArray): #If DataArray
        variables = list(segments[0].name)
    elif isinstance(segments[0], xr.Dataset): #If Dataset
        variables = list(segments[0].data_vars)
    else:
        print('Data is neither dataframe, dataarray, nor dataset.')
        return None
        
    fft={} #Make the fft list. Unfortunately has to be a dictionary due to multiple variables
    for var in variables:
        fft[var] = [] #Make each variable a list. Again, annoying but user can convert to pandas or whatever they want if they wish
        N = len(segments[0][var].values) #Need number of data points per segment from first segment
        freq = np.fft.fftfreq(N,deltat) #This is the segment frequency used for x-axis. I don't like that it's in loop but it was the only way I could think to get the length needed
        for seg in segments:
            data = seg[var].values
            
            if len(data) != N: #Rather than rewrite N and frequency every time, just detect that it's consistent for each variable. As a bonus, this is probably just preferable behavior
                print('Data has inconsistent segment length')
                return None
            
            if detrend_data: #Problem specifies "Detrend and Demean" as if at the same time so opting to only demean if detrend is true
                data = detrend(data) #had to put detrend_data earlier or else it breaks the function
            if hanning: #Hanning window. Very simple
                hanwin = np.hanning(N)
                data = data*hanwin

            sfft = np.fft.fft(data) #Take fft of segment
            amp = np.abs(sfft[freq>0])**2 #This produces the energy spectra which seems to be preferred
            fft[var].append(amp) #Append to our fft array
        fft[var] = np.mean(fft[var], axis = 0) #Mean the columns to get an average between all the segments for each variable
    freq = freq[freq>0] #Mask it to be positive spectra only
    return fft, freq