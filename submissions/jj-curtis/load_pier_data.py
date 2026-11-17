# This script defines a function to load pier data over a set interval
# Author: Jon Curtis

import xarray as xr

def load_years(start_year, end_year):
    '''Load data from SIO pier from start_year to end_year'''
    start_year = int(start_year)
    end_year = int(end_year)

    # put each year into a single array 
    ds = []
    for i in range(start_year, end_year + 1):
        link = f'http://sccoos.org/thredds/dodsC/autoss/scripps_pier-{i}.nc'
        ds.append(xr.open_dataset(link).convert_calendar('standard'))
        print(f'opened {i}')

    # return single xarray
    return xr.concat(ds, dim="time")