import numpy as np
from scipy.interpolate import interp1d
def avg_faulting(arr: np.array):
    """Calculates the average faulting value in array (magnitude), handling the 
    -10000 values as well as outliers using the IQR method. These values are 
    then turned into NaN values and nearest neighbors interpolation is used, 
    then average is calculated
   

    Args:
        arr (np.array): NumPy array of all the faulting values
    
    Returns:
        float: The average faulting value

    Raises:
        ValueError: If the array cannot be converted to a float
    """
    try:
        arr = arr.astype(float)
    except ValueError:
        raise ValueError("Array cannot be converted to float")
    
    filtered_arr = mask_outliers(arr)
    if np.all(np.isnan(filtered_arr)):
        return filtered_arr
    filtered_arr = np.abs(filtered_arr)
    filtered_arr = nn_interpolate(filtered_arr)

    mean = np.mean(filtered_arr)

    if np.isnan(mean):
        return None
    return mean


def median_faulting(arr: np.array):
    """Calculates the median faulting value in array (magnitude), handling the 
    -10000 values ONLY. Nearest neighbors interpolation is used to handle the
    invalid entries, then the median is computed.
   

    Args:
        arr (np.array): NumPy array of all the faulting values
    
    Returns:
        float: The average faulting value

    Raises:
        ValueError: If the array cannot be converted to a float
    """
    try:
        arr = arr.astype(float)
    except ValueError:
        raise ValueError("Array cannot be converted to float")
    
    filtered_arr = mask_invalid(arr)
    if np.all(np.isnan(filtered_arr)):
        return filtered_arr
    filtered_arr = np.abs(filtered_arr)
    filtered_arr = nn_interpolate(filtered_arr)

    median = np.median(filtered_arr)

    if np.isnan(median):
        return None
    return median


def percentile95_faulting(arr: np.array): 
    """Calculates the 95th percentile faulting value in array (magnitude), 
    handling the -10000 values ONLY. Nearest neighbors interpolation is used to 
    handle the invalid entries, then the 95th percentile is computed.
   

    Args:
        arr (np.array): NumPy array of all the faulting values
    
    Returns:
        float: The 95th percentile faulting value

    Raises:
        ValueError: If the array cannot be converted to a float
    """
    try:
        arr = arr.astype(float)
    except ValueError:
        raise ValueError("Array cannot be converted to float")
    
    filtered_arr = mask_invalid(arr)
    if np.all(np.isnan(filtered_arr)):
        return None
    filtered_arr = np.abs(filtered_arr)
    filtered_arr = nn_interpolate(filtered_arr)

    percentile = np.percentile(filtered_arr, 95)

    if np.isnan(percentile):
        return None
    return percentile


def stdev_faulting(arr: np.array):
    """Calculates the standard deviation of the MAGNITUDE of the faulting values 
    in the array, handling ONLY the -10000 values using nearest neighbors. 
    interpolation. These values are then turned into NaN values and nearest 
    neighbors interpolation is used.

    Args:
        arr (np.array): NumPy array of all the faulting values

    Returns:
        float: The standard deviation of the faulting values
    
    Raises:
        ValueError: If the array cannot be converted to a float
    """
    try:
        arr = arr.astype(float)
    except ValueError:
        raise ValueError("Array cannot be converted to float")
    
    filtered_arr = mask_invalid(arr)
    if np.all(np.isnan(filtered_arr)):
        return None
    filtered_arr = np.abs(filtered_arr)
    filtered_arr = nn_interpolate(filtered_arr)
    std = np.std(filtered_arr)

    if np.isnan(std):
        return None
    return std
    

def nn_interpolate(arr: np.array):
    """Interpolates the NaN values in the array using the nearest neighbors
    method.

    Args:
        arr (np.array): NumPy array of all the faulting values

    Returns:
        np.array: Array with the NaN values interpolated
    
    Raises:
        ValueError: If the array cannot be converted to a float
    """
    arr_copy = arr.copy()
    try:
        arr_copy = arr_copy.astype(float)
    except ValueError:
        raise ValueError("Array cannot be converted to float")
    
    if np.all(np.isnan(arr_copy)):
        return arr_copy
    t = np.arange(len(arr_copy))
    valid_indices = ~np.isnan(arr_copy)
    t_val = t[valid_indices]
    T_val = arr_copy[valid_indices]
    nn = interp1d(t_val, T_val, kind='nearest', fill_value='extrapolate')
    interp_val = nn(t)
    return interp_val

   
def mask_invalid(arr: np.array):
    """Masks out the invalid -10000 values ONLY in the array.

    Args:
        arr (np.array): NumPy array of all the faulting values

    Returns:
        np.array: Masked array of the faulting values
    
    Raises:
        ValueError: If the array cannot be converted to a float
    """
    arr_copy = arr.copy()
    try:
        arr_copy = arr_copy.astype(float)
    except ValueError:
        raise ValueError("Array cannot be converted to float")
    mask = np.logical_or(arr > 9998, arr < -9998)
    arr_copy[mask] = np.nan
    return arr_copy


def mask_outliers(arr: np.array):
    """Masks out the outliers in the array using the IQR method. First masks
    out the -10000 values and then calculates the IQR to mask out the outliers.

    Args:
        arr (np.array): NumPy array of all the faulting values

    Returns:
        np.array: Masked array of the faulting values
    
    Raises:
        ValueError: If the array cannot be converted to a float
    """
    arr_copy = arr.copy()   
    try:
        arr_copy = arr_copy.astype(float)
    except ValueError:
        raise ValueError("Array cannot be converted to float")
    mask = np.logical_or(arr > 9998, arr < -9998)
    arr[mask] = np.nan
    if np.all(mask):
        return arr_copy
    
    q1 = np.nanpercentile(arr, 25)
    q3 = np.nanpercentile(arr, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    mask = np.logical_or(arr <= lower_bound, arr >= upper_bound, np.isnan(arr))
    arr[mask] = np.nan
    return arr


def percent_positive(arr: np.ndarray):
    """Calculates the percentage of positive values in the array.

    Args:
        arr (np.ndarray): array of faulting values

    Returns:
        float: percentage of positive values
    
    Raises:
        ValueError: If the array cannot be converted to a float
    """
    arr_copy = arr.copy()

    try:
        arr_copy = arr_copy.astype(float)
    except ValueError:
        raise ValueError("Array cannot be converted to float")
    

    filtered_arr = mask_invalid(arr)
    filtered_arr = nn_interpolate(filtered_arr)
    if np.all(np.isnan(filtered_arr)):
        return None
    return np.sum(filtered_arr > 0) / float(len(filtered_arr))

    

