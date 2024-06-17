import numpy as np
from scipy.interpolate import interp1d


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


def find_subjoints_in_range_dict(fault_vals: list[dict[float, float]], 
                        x_min: float, 
                        x_max: float):
    """Finds all subjoint data within the x-ranges

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
    
    
    return [{'x_val': x_vals[i], 'data': entries[i]} for 
            i in range(len(entries))]
    

def get_faulting_data(y_min_mm, y_max_mm, seg_str, year, slab_inventory):
    """Gets all the faulting data for the slab of interest, identified
    with the bottom joint of the slab.

    
    Args:
        y_min_mm (float): minimum y-value in mm, expressed in terms of the 
        whole segment
        y_max_mm (float): maximum y-value in mm, expressed in terms of the 
        whole segment
        seg_str (str): the segment string
        year (int): the year of the data
        slab_inventory (SlabInventory): the slab inventory object for access to 
        database

    Returns:
        list: list of faulting values for the bottom joint
    """
    raw_subjoints = slab_inventory.find_subjoints_in_range(y_min_mm, y_max_mm,
                                                           seg_str, year) 

    faulting_entries = []
    x_cover = -1
    for raw_subjoint in raw_subjoints:         
        fault_vals = raw_subjoint['faulting_info']
        if not fault_vals:
            continue
        fault_vals = [entry for entry in fault_vals if entry['x_val'] > x_cover]
        if not fault_vals:
            continue
        x_cover = fault_vals[-1]['x_val']
        faulting_entries.extend(fault_vals)

    return faulting_entries


