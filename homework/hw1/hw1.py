
#%%
import os
from dataclasses import dataclass, field

import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt

SENTINEL = os.path.join('data', 'scripps_pier-2021.nc')

#%%
def _find_pier_file():
    """Locate data/scripps_pier-2021.nc without hard-coding anyone's home
    directory.  This module knows where IT lives, so the data must be its
    sibling: python_code/ and data/ are both inside the class repo."""
    here = os.path.dirname(os.path.abspath(__file__))   # .../python_code
    repo = os.path.dirname(here)                        # .../SIO221a_Github_code
    repo = os.path.dirname(repo)  #hack to get up to the correct directory
    for cand in (os.path.join(repo, SENTINEL),
                 os.path.join(os.environ.get('SIO221A_ROOT', ''), SENTINEL)):
        if os.path.isfile(cand):
            return cand
    print(cand)
    raise FileNotFoundError(
        f'Could not find {SENTINEL}.  Expected it inside your clone of '
        'SIO221a_Github_code, next to python_code.')


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


def get_2021_pier_data(date_start=None, date_end=None, file=None):
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

    Examples
    --------
    >>> pier = get_2020_pier_data('2020-06-04', '2020-06-07')
    >>> len(pier)
    1076
    """
    if file is None:
        file = _find_pier_file()

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

def plot_pier_data(pier):
    plt.figure(figsize = (10,5))
    plt.plot(pier.dnum, pier.temperature)
    plt.xlabel("Date", fontsize = 14)
    plt.minorticks_on()
    plt.ylabel("Temperature (°C)", fontsize = 14)
    plt.xticks(rotation=45)
    plt.show()
# %%
pier = get_2021_pier_data(file = "scripps_pier-2021.nc")
plot_pier_data(pier)

np.mean(pier.temperature)
np.std(pier.temperature)
# %%
