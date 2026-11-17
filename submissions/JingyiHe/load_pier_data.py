"""
load_pier_data.py
function for reading the SCCOOS Scripps Pier automated
shore-station records (temperature and pressure) for one or more years.

Usage:
    from load_pier_data import load_pier_data
    d = load_pier_data([2020, 2021])
    d['time']         # numpy datetime64[s] array
    d['temperature']  # degC, numpy float array (bad values -> NaN)
    d['pressure']     # dbar (as stored in the file), numpy float array

Data source:
Each year is read directly from the SCCOOS THREDDS (OPeNDAP) server:
    http://sccoos.org/thredds/dodsC/autoss/scripps_pier-<year>.nc
After the first download, each year is saved as a small .npz cache file outside the repo,
so later runs load quickly. Pass cache_dir=None to always re-download.
"""

import os
import numpy as np
from netCDF4 import Dataset

# OPeNDAP address of the yearly files; {} is replaced by the year
BASE_URL = 'http://sccoos.org/thredds/dodsC/autoss/scripps_pier-{}.nc'

# Physically plausible ranges used for simple quality control.
# Values outside these ranges are treated as bad and set to NaN.
VALID_RANGE = {
    'temperature': (5.0, 35.0),   # degC, ocean temperature at the pier
    'pressure':    (0.0, 20.0),   # dbar, sensor depth is a few metres
}


def _find_variable(nc, name):
    """Return the name of the variable in the file that matches `name`.

    Looks for an exact match first, then for any variable whose name
    contains 'name'.
    Raises KeyError if nothing matches.
    """
    if name in nc.variables:
        return name
    for v in nc.variables:
        if name in v.lower():
            return v
    raise KeyError(f'no variable like "{name}" in file; '
                   f'available: {list(nc.variables)}')


# Default folder for the downloaded copies
DEFAULT_CACHE = os.path.join(os.path.expanduser('~'), 'sio221a_pier_cache')


def _read_one_year(year, variables, cache_dir):
    """Read time and the requested variables for a single year.
    Uses the cached copy if it exists and contains all requested variables, otherwise downloads the year from the SCCOOS server and saves a cache.
    Returns a dict of numpy arrays, or None if the file cannot be opened.
    """
    # Try the cache from an earlier download
    cache = os.path.join(cache_dir, f'scripps_pier-{year}.npz') if cache_dir else ''
    if cache and os.path.isfile(cache):
        c = np.load(cache)
        if all(k in c for k in ('time',) + tuple(variables)):
            return {k: c[k] for k in ('time',) + tuple(variables)}

    # Otherwise download from the THREDDS server
    source = BASE_URL.format(year)
    try:
        nc = Dataset(source)
    except OSError as err:
        print(f'{year}: could not open {source} ({err})')
        return None

    out = {}
    # Time is stored as seconds since 1970-01-01 -> convert to datetime64
    tunits = nc.variables['time'].units
    if not tunits.startswith('seconds since 1970-01-01'):
        print(f'  WARNING {year}: unexpected time units "{tunits}"')
    out['time'] = np.asarray(nc.variables['time'][:]).astype('datetime64[s]')

    # Read each requested variable; masked values become NaN
    for name in variables:
        vname = _find_variable(nc, name)
        out[name] = np.ma.filled(nc.variables[vname][:].astype(float), np.nan)
    nc.close()

    # Save a cache so the next run does not need to download again
    if cache:
        os.makedirs(cache_dir, exist_ok=True)
        np.savez(cache, **out)
    return out


def load_pier_data(years, variables=('temperature', 'pressure'),
                   cache_dir=DEFAULT_CACHE, verbose=True):
    """Load and stitch Scripps Pier records for the given years.

    Parameters:
    years : int or iterable of int
        Year(s) to load, e.g. 2021 or range(2005, 2022).
    variables : tuple of str
        Variables to read besides time (default temperature and pressure).
    cache_dir : str or None
        Folder for the downloaded copies (default ~/sio221a_pier_cache).
        Use None to always download from the server.
    verbose : bool
        If True, print a one-line summary per year.

    Returns dict with keys 'time' (datetime64[s]) and one key per variable
    (float arrays, NaN for bad/missing values), all sorted in time with
    repeated time stamps removed.
    """
    if np.isscalar(years):
        years = [years]

    pieces = []
    for year in years:
        d = _read_one_year(year, variables, cache_dir)
        if d is None:
            continue
        if verbose:
            dt = np.median(np.diff(d['time'])) / np.timedelta64(1, 'm')
            print(f'{year}: {len(d["time"]):7d} samples, {d["time"][0]} to '
                  f'{d["time"][-1]}, median dt = {dt:.1f} min')
        pieces.append(d)

    if not pieces:
        raise RuntimeError('no data could be loaded')

    # Join all years into one long record
    out = {k: np.concatenate([p[k] for p in pieces]) for k in pieces[0]}

    # Sort by time and drop repeated time stamps
    order = np.argsort(out['time'])
    out = {k: v[order] for k, v in out.items()}
    keep = np.concatenate([[True], np.diff(out['time']) > np.timedelta64(0, 's')])
    out = {k: v[keep] for k, v in out.items()}

    # Simple quality control: values outside a plausible range -> NaN
    for name in variables:
        if name in VALID_RANGE:
            lo, hi = VALID_RANGE[name]
            bad = (out[name] < lo) | (out[name] > hi)
            if verbose and bad.any():
                print(f'{name}: {bad.sum()} values outside [{lo}, {hi}] set to NaN')
            out[name][bad] = np.nan

    return out
