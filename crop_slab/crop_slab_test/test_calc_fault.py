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
    

    def test_std_faulting(self):
        """The standard deviation of the MAGNITUDE of the faulting values is 
        calculated by interpolating ONLY the invalid entries (-10000 values). 
        """
        arr = np.array([1, 2, -3, 4, 5, 6, 7, 8, 9, 10, -10000, 100])
        expected = np.std([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 100])
        result = fc.stdev_faulting(arr)
        self.assertAlmostEqual(result, expected, places=6)


    def test_percent_positive(self):
        """The percentage of positive values is calculated, with -10000 values
        interpolated using nearest neighbors.
        """
        arr = np.array([1, -2, -3, 4, 5, 6, 7, 8, 9, 10, -10000, 100])
        expected = 10 / 12.0
        result = fc.percent_positive(arr)
        self.assertAlmostEqual(result, expected, places=6)
