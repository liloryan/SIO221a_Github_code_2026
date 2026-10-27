#%%
import numpy as np
from dataclasses import dataclass, field
import scipy
#%%
"""
*Group 1: write a function called OrthogDemo_[your inits or group name].
	*function takes two inputs, n and m.
	*function outputs a structure "out" with the following fields: 
		*time: a time vector, 0:0.01:(2 pi) 
		*wave1: cos(m*time)
		*wave2: cos(n*time)
		*product = wave1 * wave2
		*integral = \int_0^2*pi wave1 * wave2 dt
	*push this to Github under codingexercises / class6
"""

@dataclass
class out:
    """A slice of the 2021 pier record. """
    time: np.ndarray          # times, as numpy datetime64[s]
    wave1: np.ndarray   # degrees C
    wave2: np.ndarray      # decibars
    integral: float

    def __len__(self):
        return len(self.time)

def OrthogDemo_LR(n,m):
    time = range(0, 2*np.pi, 0.01)
    wave1 = np.cos(m*time)
    wave2 = np.cos(n*time)
    