import unittest
import numpy as np
import crop_slab.fault_calc as fc
class FaultCalcTest(unittest.TestCase):
    def test_mask_outliers(self):
        """-10000 values must be filtered out.
        """
        arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, -10000, 10000])
        expected = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, np.nan, np.nan])
        result = fc.mask_outliers(arr)
        self.assertTrue(np.allclose(result, expected, atol=1e-6, equal_nan=True))

    
    def test_mask_outliers2(self):
        """The 400 value as well as the -10000 values must be filtered out
        """
        arr = np.array([2, 5, 4, 3, 3, 3, 4, 400, -10000, -10000, -10000, -10000])
        expected = np.array([2, 5, 4, 3, 3, 3, 4, np.nan, np.nan, np.nan, np.nan, np.nan])
        result = fc.mask_outliers(arr)
        self.assertTrue(np.allclose(result, expected, atol=1e-6, equal_nan=True))


    def test_mask_outliers3(self):
        """The 300 value as well as the -10000 values must be filtered out
        """
        arr = np.array([-300, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 300, -10000])
        expected = np.array([np.nan, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, np.nan, np.nan])
        result = fc.mask_outliers(arr)
        self.assertTrue(np.allclose(result, expected, atol=1e-6, equal_nan=True))
    

    def test_mask_outliers4(self):
        """NaN value handling
        """
        arr = np.array([np.nan, np.nan])
        expected = np.array([np.nan, np.nan])
        result = fc.mask_outliers(arr)
        self.assertTrue(np.allclose(result, expected, atol=1e-6, equal_nan=True))


    def test_near_interpolate1(self):
        """The NaN values are interpolated with the nearest neighbors.
        """
        arr = np.array([1, 2, 3, 4, np.nan, 6, 7, 8, 9, 10])
        expected = np.array([1, 2, 3, 4, 4, 6, 7, 8, 9, 10])
        print(expected)
        result = fc.nn_interpolate(arr)
        print(result)
        self.assertTrue(np.allclose(result, expected, atol=1e-6))


    def test_near_interpolate2(self):
        """The NaN values are interpolated with the nearest neighbors.
        """
        arr = np.array([1, 2, 3, 4, np.nan, np.nan, np.nan, 8, 9, 10])
        expected = np.array([1, 2, 3, 4, 4, 4, 8, 8, 9, 10])
        result = fc.nn_interpolate(arr)
        self.assertTrue(np.allclose(result, expected, atol=1e-6))


    def test_near_interpolate3(self):
        """All NaN values"""
        arr = np.array([np.nan, np.nan, np.nan, np.nan])
        expected = np.array([np.nan, np.nan, np.nan, np.nan])
        result = fc.nn_interpolate(arr)
        self.assertTrue(np.allclose(result, expected, atol=1e-6, equal_nan=True))

    
    def test_avg_faulting(self):
        """The average faulting value is calculated without outliers.
        """
        arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, -10000, 100])
        expected = (1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 30) / 12.0
        result = fc.avg_faulting(arr)
        self.assertAlmostEqual(result, expected, places=6)

    
    def test_avg_faulting2(self):
        """NaN values edge case
        """

        arr = np.array([np.nan, np.nan, np.nan, np.nan])
        result = fc.avg_faulting(arr)
        self.assertIsNone(result)
    

    def test_avg_faulting_negative(self):
        """Negative values edge case. Since we are calculating magnitude, output
        must be positive
        """

        arr = np.array([-1, -2, -3, -4, -5, -6, -7, -8, -9, -10])
        expected = 5.5
        result = fc.avg_faulting(arr)
        self.assertAlmostEqual(result, expected, places=6)
    
    def test_median_faulting(self):
        arr = np.array([1, -2, 3, -4, 5, 6, -10000, 7, 900, 9])
        expected = 5.5
        result = fc.median_faulting(arr)
        self.assertAlmostEqual(expected, result)


    def test_median_NaN(self):
        arr = np.array([np.nan, np.nan])
        result = fc.median_faulting(arr)
        self.assertIsNone(result)
        

    def test_std_faulting(self):
        """The standard deviation of the MAGNITUDE of the faulting values is 
        calculated by interpolating BOTH the invalid entries (-10000 values)
        and the outliers. 
        """
        arr = np.array([1, 2, -3, 4, 5, 6, 7, 8, 9, 10, -10000, 100])
        expected = np.std([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10])
        result = fc.stdev_faulting(arr)
        self.assertAlmostEqual(result, expected, places=6)

    
    def test_std_faulting_NaN(self):
        arr = np.array([np.nan, np.nan])
        result = fc.stdev_faulting(arr)
        self.assertIsNone(result)

    def test_95th_percentile_faulting(self):
        """The 95th percentile faulting value is calculated, with -10000 values
        interpolated using nearest neighbors.
        """
        arr = np.arange(0, 100)
        expected = 94.05
        result = fc.percentile95_faulting(arr)
        self.assertAlmostEqual(result, expected, places=6)
    

    def test_95th_NaN(self):
        """NaN values edge case
        """
        arr = np.array([np.nan, np.nan, np.nan, np.nan])
        result = fc.percentile95_faulting(arr)
        self.assertIsNone(result)


    def test_percent_positive(self):
        """The percentage of positive values is calculated, with -10000 values
        interpolated using nearest neighbors.
        """
        arr = np.array([1, -2, -3, 4, 5, 6, 7, 8, 9, 10, -10000, 100])
        expected = 10 / 12.0
        result = fc.percent_positive(arr)
        self.assertAlmostEqual(result, expected, places=6)

    
    def test_percent_positive2(self):
        """NaN values edge case
        """
        arr = np.array([np.nan, np.nan, np.nan, np.nan])
        result = fc.percent_positive(arr)
        self.assertIsNone(result)

    
    def test_find_subjoints_in_range(self):
        """The values in the array that fall within the specified range are 
        extracted.
        """
        fault_vals = [{'data': 1, 'x_val': 1}, {'data': 2, 'x_val': 2}, 
                      {'data': 3, 'x_val': 3}, {'data': 4, 'x_val': 4}, 
                      {'data': 5, 'x_val': 5}, {'data': 6, 'x_val': 6}, 
                      {'data': 7, 'x_val': 7}, {'data': 8, 'x_val': 8}, 
                      {'data': 9, 'x_val': 9}, {'data': 10, 'x_val': 10}]
        res = fc.find_subjoints_in_range(fault_vals, 2, 4)
        expected = np.array([2, 3, 4], dtype=float)
        self.assertTrue(np.allclose(res, expected, atol=1e-6))
    

    def test_find_subjoints_in_range_2(self):
        """Empty list edgecase
        """
        fault_vals = []
        res = fc.find_subjoints_in_range(fault_vals, 2, 4)
        expected = np.array([], dtype=float)    
        self.assertTrue(np.allclose(res, expected, atol=1e-6))    

    
    def test_find_subjoints_in_range_3(self):
        """Out of bounds edgecase
        """
        fault_vals = [{'data': 1, 'x_val': 1}]
        res = fc.find_subjoints_in_range(fault_vals, 2, 4)
        expected = np.array([], dtype=float)
        self.assertTrue(np.allclose(res, expected, atol=1e-6))  

    
    def test_all_stats(self):
        """Confirming all the statistics are calculated correctly
        """
        arr = np.array([1, -2, -3, 4, 5, 6, 7, 8, 9, 10, -10000, 100])
        data = fc.calc_all_stats(arr)
        mean = fc.avg_faulting(arr)
        median = fc.median_faulting(arr)    
        percentile95 = fc.percentile95_faulting(arr)
        stdev = fc.stdev_faulting(arr)
        percent_positive_val = fc.percent_positive(arr)


        self.assertAlmostEqual(data['mean'], mean)  
        self.assertAlmostEqual(data['median'], median)
        self.assertAlmostEqual(data['percentile95'], percentile95)
        self.assertAlmostEqual(data['stdev'], stdev)
        self.assertAlmostEqual(data['percent_positive'], percent_positive_val)

    def test_all_stats2(self):
        """NaN values edge case
        """
        arr = np.array([np.nan, np.nan, np.nan, np.nan])
        data = fc.calc_all_stats(arr)
        self.assertIsNone(data['mean'])
        self.assertIsNone(data['median'])
        self.assertIsNone(data['percentile95'])
        self.assertIsNone(data['stdev'])
        self.assertIsNone(data['percent_positive'])


    


    

