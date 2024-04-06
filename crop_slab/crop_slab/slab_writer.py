from pymongo import MongoClient
from crop_slab.joint import HorizontalJoint
import warnings
import numpy as np
from utils.px_mm_converter import PXMMConverter
import crop_slab.fault_calc as fc
class SlabWriter:
    def __init__(self, interstate: str, MM_start: int,
                 MM_end: int, year: int, scaler: PXMMConverter):
        # set up connection to database
        CONNECTION_STRING = 'mongodb://localhost:27017'
        self.client = MongoClient(CONNECTION_STRING)
        self.db = self.client['jpcp_deterioration']
        self.slab_collection = self.db['slabs']
        self.raw_subjoint_collection = self.db['raw_subjoint_data']
        self.year = year
        self.MM_start = MM_start
        self.MM_end = MM_end
        self.interstate = interstate
        self.seg_year_id = self.find_segment_year_id()
        self.scaler = scaler
        # drop old entries from that year to make room for update if needed
        self.slab_collection.delete_many({'seg_year_id': self.seg_year_id}) 


    def find_segment_year_id(self):
        """Finds the segment year id in the database

        Returns:
            str: the segment year id
        """
        segment = self.db['segments'].find_one(
            {'interstate': self.interstate, 
             'MM_start': self.MM_start, 
             'MM_end': self.MM_end}
        )

        try:
            return segment['years'][str(self.year)]
        except:
            raise ValueError('Raw segment data for the year is not loaded in. \
                             Please run the XML to CVAT parser first to \
                             retrieve faulting values for the year.')


    
    def write_slab_entry(self, slab_index, length, width, start_im, end_im, 
                         y_offset, y_min, y_max, bottom_joint):
        """Writes a slab entry to the database

        Args:
            slab_index (int): index of the slab 
            length (float): length of slab from midpoint to midpoint
            width (float): width of the slab
            start_im (int): index of the first image for the slab
            end_im (int): index of the last image for the slab
            y_offset (float): y-offset of slab, based off location of midpoint
            of bottom joint
            y_min (float): min y-value of the slab
            y_max (float): max y-value of the slab
            bottom_joint (HorizontalJoint): the bottom joint of the slab
        """
        
        wheelpath_vals = self.get_faulting_data(bottom_joint)
        mean_faulting = fc.avg_faulting(wheelpath_vals)
        stdev_faulting = fc.stdev_faulting(wheelpath_vals)
        median_faulting = fc.median_faulting(wheelpath_vals)
        p95_faulting = fc.percentile95_faulting(wheelpath_vals)
        positive_faulting = fc.percent_positive(wheelpath_vals)

        if mean_faulting:
            mean_faulting = round(mean_faulting, 2)
        if stdev_faulting:
            stdev_faulting = round(stdev_faulting, 2)
        if median_faulting:
            median_faulting = round(median_faulting, 2)
        if p95_faulting:
            p95_faulting = round(p95_faulting, 2)
        if positive_faulting:
            positive_faulting = round(positive_faulting, 2)


        entry = {
            'seg_year_id': self.seg_year_id,
            'slab_index': slab_index,
            'length': length,
            'width': width,
            'start_im': start_im,
            'end_im': end_im,
            'y_offset': y_offset,
            'y_min': y_min,
            'y_max': y_max,
            'mean_faulting': mean_faulting,
            'stdev_faulting': stdev_faulting,
            'median_faulting': median_faulting,
            'p95_faulting': p95_faulting,
            'positive_faulting': positive_faulting,
            'primary_state': None,
            'secondary_state': None,
            'special_state': None
        }

        self.slab_collection.insert_one(entry)


    def find_subjoints_in_range(self, y_min: float, y_max: float):
        """Finds all subjoint data within the y-ranges

        Args:
            y_min (float): min y-value, expressed in absolute mm
            y_max (float): max y-value, expressed in absolute mm

        Returns:
            pymongo.cursor.Cursor: cursor object containing all subjoint data
            within the y-ranges
        """
        raw_subjoints = self.raw_subjoint_collection.find(
            {
                '$or': 
                [
                    {
                        'seg_year_id': self.seg_year_id,
                        'y_min': {'$gte': y_min - 100, '$lte': y_max + 100}
                    },
                    {
                        'seg_year_id': self.seg_year_id,
                        'y_max': {'$gte': y_min - 100, '$lte': y_max + 100}
                    }
                ]
            }
        )
        return raw_subjoints
    
    
    def get_faulting_data(self, bottom_joint: HorizontalJoint):
        """Gets all the faulting data for the slab of interest, identified
        with the bottom joint of the slab.

        
        Args:
            bottom_joint (HorizontalJoint): the bottom joint of the slab

        Returns:
            np.array: array of faulting values for the bottom joint
        """
        x_min_px = bottom_joint.get_min_x()
        x_max_px = bottom_joint.get_max_x()
        x_min_mm = self.scaler.convert_px_to_mm_relative(x_min_px, 0, 0)[0]
        x_max_mm = self.scaler.convert_px_to_mm_relative(x_max_px, 0, 0)[0]
        width_mm = x_max_mm - x_min_mm
        edge_buffer = (width_mm - 2750) / 2
        if edge_buffer < 0:
            warnings.warn(f'Slab width is less than 2.75m, so faulting value \
                          for slab cannot be calculated. Ensure joints are \
                          annotated correctly.', Warning)

        left_wp = (x_min_mm + edge_buffer, x_min_mm + edge_buffer + 1000)
        right_wp = (x_max_mm - edge_buffer - 1000, x_max_mm - edge_buffer)
        y_bottom_px = bottom_joint.get_max_y()
        y_top_px = bottom_joint.get_min_y()
        bottom_img_id = bottom_joint.get_bottom_img_id(self.scaler.num_images, self.scaler.px_height)
        top_img_id = bottom_joint.get_top_img_id(self.scaler.num_images, self.scaler.px_height)
        y_min_mm = self.scaler.convert_px_to_mm_relative(0, y_bottom_px % 1250, bottom_img_id)[1]
        y_max_mm = self.scaler.convert_px_to_mm_relative(0, y_top_px % 1250, top_img_id)[1]

        raw_subjoints = self.find_subjoints_in_range(y_min_mm, y_max_mm) 
        
        wheelpath_entries = np.array([])
        for raw_subjoint in raw_subjoints:         
            fault_vals = raw_subjoint['faulting_info']
            if not fault_vals:
                continue
            # check left wheelpath
            l_values = np.array([item['data'] 
                        for item in fault_vals 
                        if left_wp[0] <= item['x_val'] <= left_wp[1]])
        
            # check right wheelpath
            r_values = np.array([item['data'] 
                        for item in fault_vals 
                        if right_wp[0] <= item['x_val'] <= right_wp[1]])
            wheelpath_entries = np.concatenate((wheelpath_entries, l_values, r_values))

        return wheelpath_entries
        
    

    def calc_faulting_sum(self, arr: np.ndarray):
        """Calculates the sum of the faulting values in the array, handling the
        -10000 values by interpolating the median of the non-negative values.

        Args:
            arr (np.ndarray): array of faulting values

        Returns:
            float: sum of the faulting values
        """
        arr = arr.astype(float)
        arr = np.absolute(arr)
        mask = (arr > 9998)
        if np.all(mask):
            return 0
        arr[mask] = np.nan
        median = np.nanmedian(arr)
        arr[mask] = median

        return np.sum(arr)
            
    




            










