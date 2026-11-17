import xarray as xr  #import xarray library
import numpy as np #import numpy to conver the data time array

def load_in_pier_data(date_to_load,path_to_data = '/Users/kat/Desktop/GradSchool/SIOC221/HW/HW1/HW1_data/'): 
    ''' This funcion loads data in from a specified path on the local machine. 
        It takes inputs: year date(float/int), path(str)
        returns data_for_specified_year, time_array corresponding to data
    '''
    data_year = xr.open_dataset(f'{path_to_data}scripps_pier-{date_to_load}.nc') #load in the data 
    time_array = np.sort(np.asarray(data_year.time).astype('datetime64[s]')) #sort the time array so it is in time order
    print(f'got pier data for {date_to_load}: data, time array')
    return data_year,time_array

d2015_data, d2015_time = load_in_pier_data(2015)