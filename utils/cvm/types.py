from typing import TypeAlias

import numpy as np

Np1dArray: TypeAlias = np.ndarray[np.number]
Np2dArray: TypeAlias = np.ndarray[np.number, np.dtype[np.number]]
Np3dArray: TypeAlias = np.ndarray[np.number, np.ndarray[np.number, np.dtype[np.number]]]
