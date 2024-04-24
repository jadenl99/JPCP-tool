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
    if np.all(np.isnan(arr)):
        return None
    filtered_arr = mask_outliers(arr)
    if np.all(np.isnan(filtered_arr)):
        return None
    filtered_arr = np.abs(filtered_arr)
    filtered_arr = nn_interpolate(filtered_arr)

    mean = np.mean(filtered_arr)

    if np.isnan(mean):
        return None
    return mean


def median_faulting(arr: np.array):
    """Calculates the median of the MAGNITUDE of the faulting values 
    in the array, handling BOTH the -10000 values and outliers. These values are 
    then turned into NaN values and nearest neighbors interpolation is used on
    those NaN values, and the calculation is made.
   

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
    if np.all(np.isnan(arr)):
        return None
    filtered_arr = mask_outliers(arr)
    if np.all(np.isnan(filtered_arr)):
        return None
    filtered_arr = np.abs(filtered_arr)
    filtered_arr = nn_interpolate(filtered_arr)

    median = np.median(filtered_arr)

    if np.isnan(median):
        return None
    return median


def percentile95_faulting(arr: np.array): 
    """Calculates the 95th percentile of the MAGNITUDE of the faulting values 
    in the array, handling BOTH the -10000 values and outliers. These values are 
    then turned into NaN values and nearest neighbors interpolation is used on
    those NaN values, then the calculation is made.
   

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
    
    filtered_arr = mask_outliers(arr)
    if np.all(np.isnan(arr)):
        return None
    filtered_arr = np.abs(filtered_arr)
    filtered_arr = nn_interpolate(filtered_arr)

    percentile = np.percentile(filtered_arr, 95)

    if np.isnan(percentile):
        return None
    return percentile


def stdev_faulting(arr: np.array):
    """Calculates the standard deviation of the MAGNITUDE of the faulting values 
    in the array, handling BOTH the -10000 values and outliers. These values are 
    then turned into NaN values and nearest neighbors interpolation is used on
    those NaN values, then the calculation is made.

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
    if np.all(np.isnan(arr)):
        return None
    filtered_arr = mask_outliers(arr)
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
        ValueError: If the array cannot be converted to a float array
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
    arr_copy[mask] = np.nan
    if np.all(mask):
        return arr_copy
    
    q1 = np.nanpercentile(arr_copy, 25)
    q3 = np.nanpercentile(arr_copy, 75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    mask = np.logical_or(arr <= lower_bound, arr >= upper_bound, np.isnan(arr))
    arr_copy[mask] = np.nan
    return arr_copy


def calc_all_stats(arr: np.array):
    """Calculates all the statistics of the faulting values in the array.

    Args:
        arr (np.array): NumPy array of all the faulting values

    Returns:
        dict: Dictionary containing all the statistics
    
    Raises:
        ValueError: If the array cannot be converted to a float
    """
    try:
        arr = arr.astype(float)
    except ValueError:
        raise ValueError("Array cannot be converted to float")
    filtered_arr = mask_outliers(arr)
    if np.all(np.isnan(filtered_arr)):
        return{'mean': None, 'median': None, 'percentile95': None, 
            'stdev': None, 'percent_positive': None}
    filtered_arr = nn_interpolate(filtered_arr)
    percent_positive_val = percent_positive(filtered_arr)
    abs_arr = np.abs(filtered_arr)
    
    mean = np.mean(abs_arr)
    median = np.median(abs_arr)
    percentile95 = np.percentile(filtered_arr, 95)
    stdev = np.std(abs_arr)
    
    return {'mean': mean, 'median': median, 'percentile95': percentile95, 
            'stdev': stdev, 'percent_positive': percent_positive_val}


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

    filtered_arr = mask_outliers(arr)
    filtered_arr = nn_interpolate(filtered_arr)
    if np.all(np.isnan(filtered_arr)):
        return None
    return np.sum(filtered_arr > 0) / float(len(filtered_arr))


def find_subjoints_in_range(fault_vals: list[dict[float, float]], 
                            x_min: float, 
                            x_max: float):
        """Finds all subjoint data within the x-ranges

        Args:
            fault_vals (list[dict[float, float]]): list of faulting values with
            each dictionary containing the x-value and the faulting value
            x_min (float): min y-value, expressed in absolute mm
            x_max (float): max y-value, expressed in absolute mm

        Returns:
            np.array: array of subjoint data within the x-ranges

        Raises:
            ValueError: if x_min is greater than x_max
            ValueError: if faulting values are not in the correct format
        """
        if x_min > x_max:
            raise ValueError('x_min cannot be greater than x_max')
        entries = [entry['data'] for entry in fault_vals 
                   if x_min <= entry['x_val'] <= x_max]
        try:
            return np.array(entries, dtype=float)
        except:
            raise ValueError('Faulting values are not in the correct format.')
        
    
def find_subjoints_in_range_filtered(fault_vals: list[dict[float, float]], 
                                     x_min: float, 
                                     x_max: float):
        """Finds all subjoint data within the x-ranges and filters out the 
        outliers and replaces them with using nearest neighbors interpolation.


        Args:
            fault_vals (list[dict[float, float]]): list of faulting values with
            each dictionary containing the x-value and the faulting value
            x_min (float): min y-value, expressed in absolute mm
            x_max (float): max y-value, expressed in absolute mm

        Returns:
            list[dict[float, float]]: list of faulting values and their
            corresponding x-values.

        Raises:
            ValueError: if x_min is greater than x_max
            ValueError: if faulting values are not in the correct format
        """
        if x_min > x_max:
            raise ValueError('x_min cannot be greater than x_max')
        entries = [entry['data'] for entry in fault_vals 
                   if x_min <= entry['x_val'] <= x_max]
        x_vals = [entry['x_val'] for entry in fault_vals
                  if x_min <= entry['x_val'] <= x_max]
        try:
            entries = np.array(entries, dtype=float)
        except:
            raise ValueError('Faulting values are not in the correct format.')
        
        filtered_entries = mask_outliers(entries)
        filtered_entries = list(nn_interpolate(filtered_entries))
        return [{'x_val': x_vals[i], 'data': filtered_entries[i]} for 
                i in range(len(filtered_entries))]
    



