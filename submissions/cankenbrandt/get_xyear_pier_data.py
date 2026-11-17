"""Read the Scripps pier record of any year.

Copied from phython_code/Get2020PierData.py and edited by CVA 
to remove hardcoded year and make functions more useable 

Implements PierData dataclass for handling Scripps pier data.

MHA SIO221a, 2026-08-24.
CVA 2026-10-06
"""

import os
from dataclasses import dataclass, field

import numpy as np
from netCDF4 import Dataset



#SENTINEL = os.path.join('data', f'scripps_pier-{xyear}.nc')

#Currently never called because the data is fetched from the URL instead of local files.
#leaving it in in case I change my mind
def _find_pier_file(xyear = 2020):
    """Locate data/scripps_pier-{xyear}.nc without hard-coding anyone's home
    directory.  This module knows where IT lives, so the data must be its
    sibling: python_code/ and data/ are both inside the class repo."""
    data_path = os.path.join('data', f'scripps_pier-{xyear}.nc') #create filepath
    here = os.path.dirname(os.path.abspath(__file__))   # .../python_code
    repo = os.path.dirname(here)                        # .../SIO221a_Github_code

    for cand in (os.path.join(repo, data_path),
                 os.path.join(os.environ.get('SIO221A_ROOT', ''), data_path)):
        if os.path.isfile(cand):
            return cand

    raise FileNotFoundError(
        f'Could not find {data_path}.  Expected it inside your clone of '
        'SIO221a_Github_code, next to python_code.')


@dataclass
class PierData:
    """A slice of the {xyear} pier record.  The MATLAB version returns a struct
    with these same fields."""
    dnum: np.ndarray          # times, as numpy datetime64[s]
    temperature: np.ndarray   # degrees C
    pressure: np.ndarray      # decibars
    readme: str = field(
        default=f'xyear Pier data, SIO221a, function get_xyear_pier_data.py')

    def __len__(self):
        return len(self.dnum)


def get_pier_data(xyear = 2020, date_start=None, date_end=None, file=None):
    """Return temperature, pressure and time from the {xyear} Scripps pier record.

    Parameters
    ----------
    xyear : int, optional
        The year for which to retrieve pier data.
        Defaults to 2020
    date_start, date_end : numpy datetime64 or str, optional
        Bracket the period you want, e.g. '2020-06-04'.  Omit both to get the
        whole record.
        BEWARE: Doesn't check that date_start is before date_end or it's in {xyear}'s range.
    file : str, optional
        Path to the netCDF file.  Omit it and we find data/scripps_pier-{xyear}.nc
        inside the class repo OR from the URL if not available locally.
        CURRENTLY ONLY URL IS SUPPORTED.

    Returns
    -------
    pier : PierData

    Examples
    --------
    >>> pier = get_pier_data(xyear=2020, date_start='2020-06-04', date_end='2020-06-07')
    >>> len(pier)
    1076
    """

    #to explain this next one: I planned to use the pre-existing logic and store all the pier data files in the Data folder
    #but I didn't want to bother downloading and reorganizing the data.... so I just used the URL...
    #I should clean it up but I will leave the dead parts for now in case I want to change it back
    if file is None:
        #use this again if downloading the data locally:
        #file = _find_pier_file(xyear=xyear)

        #for grabbing the data from the URL
        file = f'http://sccoos.org/thredds/dodsC/autoss/scripps_pier-{xyear}.nc'

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
