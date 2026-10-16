import numpy as np
from dataclasses import dataclass, field
import os
from netCDF4 import Dataset

@dataclass
class PierData:
    """A slice of the 2021 pier record. """
    dnum: np.ndarray          # times, as numpy datetime64[s]
    temperature: np.ndarray   # degrees C
    pressure: np.ndarray      # decibars
    readme: str = field(
        default='2021 Pier data, SIO221a, function get_2021_pier_data.py')

    def __len__(self):
        return len(self.dnum)

    
def get_pier_data(file, date_start=None, date_end=None):
    """Return temperature, pressure and time from the 2020 Scripps pier record.

    Parameters
    ----------
    date_start, date_end : numpy datetime64 or str, optional
        Bracket the period you want, e.g. '2020-06-04'.  Omit both to get the
        whole record.
    file : str, optional
        Path to the netCDF file.  Omit it and we find data/scripps_pier-2020.nc
        inside the class repo.

    Returns
    -------
    pier : PierData
    """

    nc = Dataset(file)
    try:
        time = np.asarray(nc.variables['time'][:])
        temperature = np.asarray(nc.variables['temperature'][:])
        pressure = np.asarray(nc.variables['pressure'][:])
    finally:
        nc.close()

    # netCDF time is seconds since 1970-01-01, which is exactly datetime64[s].
    dnum = time.astype('datetime64[s]')

    if date_start is None:
        i1 = np.ones(dnum.shape, dtype=bool)
    else:
        i1 = ((dnum > np.datetime64(date_start)) &
              (dnum < np.datetime64(date_end)))

    return PierData(dnum=dnum[i1],
                    temperature=temperature[i1],
                    pressure=pressure[i1])


def getManyPier(numyears, start, date_start=None, date_end=None):
    """
    converts from pier object to dictionary in order to append more easily

    takes in number of years to add together, starting year

    returns: PierData object 
    
    """
    pier_data = {"dnum":np.array([], dtype='datetime64[s]'), "temperature":np.array([]), "pressure":np.array([])} #make an initial dictionary to append all the data to
    for i in range(start,start+numyears):
        pier = get_pier_data(file= "../pier_data/scripps_pier-"+str(i)+".nc")
        pier_data["dnum"] = np.concatenate((pier_data["dnum"], pier.dnum)) #preserve the order, append new values to the end
        pier_data["temperature"] = np.concatenate((pier_data["temperature"], pier.temperature))
        pier_data["pressure"] = np.concatenate((pier_data["pressure"], pier.pressure))
    pier = PierData(dnum= pier_data["dnum"], temperature=pier_data["temperature"], pressure=pier_data["pressure"])
    return pier