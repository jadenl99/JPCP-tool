"""
author: Girish Hari
Lab: tsai-research

Functions that implement some of the same functionality found in Matlab's bwmorph.

`endpoints` - lines up perfectly with matlab's output (in my limited testing)
`branches` - this results in more clustered pixels than matlab's version but it pretty close
"""

import numpy as np
import scipy.ndimage as ndi


def _neighbors_cnt(image: np.ndarray) -> np.ndarray:
    """
    Counts the neighbor pixels for each pixel of an image:
            x = [
                [0, 1, 0],
                [1, 1, 1],
                [0, 1, 0]
            ]
            _neighbors(x)
            [
                [0, 3, 0],
                [3, 4, 3],
                [0, 3, 0]
            ]
    :type image: numpy.ndarray
    :param image: A two-or-three dimensional image
    :return: neighbor pixels for each pixel of an image
    """
    image = image.astype(np.uint8)
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    neighbor_cnt = ndi.convolve(image, kernel, mode="constant", cval=0)
    neighbor_cnt[~image.astype(bool)] = 0
    return neighbor_cnt


def get_branches_mask(image: np.ndarray) -> np.ndarray:
    """
    Returns the nodes in between edges

    Parameters
    ----------
    image : binary (M, N) ndarray

    Returns
    -------
    out : ndarray of bools
    """
    return _neighbors_cnt(image) > 2


def get_endpoints_mask(image: np.ndarray) -> np.ndarray:
    """
    Returns the endpoints in an image

    Parameters
    ----------
    image : binary (M, N) ndarray

    Returns
    -------
    out : ndarray of bools
    """
    return _neighbors_cnt(image) == 1
