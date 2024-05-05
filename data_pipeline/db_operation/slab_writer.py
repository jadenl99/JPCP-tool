from pymongo import MongoClient
import pymongo
from crop_slab.joint import HorizontalJoint
import warnings
import numpy as np
from utils.px_mm_converter import PXMMConverter
import crop_slab.fault_calc as fc
import math
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
        # left buffer
        z1 = (x_min_mm, x_min_mm + edge_buffer)
        # left wheelpath
        z2 = (x_min_mm + edge_buffer, x_min_mm + edge_buffer + 1000)
        # center
        z3 = (x_min_mm + edge_buffer + 1000, x_max_mm - edge_buffer - 1000)
        # right wheelpath
        z4 = (x_max_mm - edge_buffer - 1000, x_max_mm - edge_buffer)
        # right buffer
        z5 = (x_max_mm - edge_buffer, x_max_mm)

        faulting_data = self.get_faulting_data(bottom_joint)    
        faulting_vals = fc.find_subjoints_in_range(faulting_data, 
                                                   x_min_mm, 
                                                   x_max_mm)
        stats = fc.calc_all_stats(faulting_vals)
        mean_faulting = stats['mean']
        stdev_faulting = stats['stdev']
        median_faulting = stats['median']
        p95_faulting = stats['percentile95']
        positive_faulting = stats['percent_positive']
        if mean_faulting:
            mean_faulting = round(mean_faulting, 4)
        if stdev_faulting:
            stdev_faulting = round(stdev_faulting, 4)
        if median_faulting:
            median_faulting = round(median_faulting, 4)
        if p95_faulting:
            p95_faulting = round(p95_faulting, 4)
        if positive_faulting:
            positive_faulting = round(positive_faulting, 4)
        
        filtered_faulting_data = fc.find_subjoints_in_range_filtered(
            faulting_data, x_min_mm, x_max_mm
            )
        # z1_vals = fc.find_subjoints_in_range(filtered_faulting_data, z1[0], z1[1])
        # z2_vals = fc.find_subjoints_in_range(filtered_faulting_data, z2[0], z2[1])
        # z3_vals = fc.find_subjoints_in_range(filtered_faulting_data, z3[0], z3[1])
        # z4_vals = fc.find_subjoints_in_range(filtered_faulting_data, z4[0], z4[1])
        # z5_vals = fc.find_subjoints_in_range(filtered_faulting_data, z5[0], z5[1])
        z1_vals = 0
        z2_vals = 0
        z3_vals = 0
        z4_vals = 0
        z5_vals = 0
        
        z1_vals = np.abs(z1_vals)
        z2_vals = np.abs(z2_vals)
        z3_vals = np.abs(z3_vals)
        z4_vals = np.abs(z4_vals)
        z5_vals = np.abs(z5_vals)

        z1_median = np.median(z1_vals)
        z2_median = np.median(z2_vals)
        z3_median = np.median(z3_vals)
        z4_median = np.median(z4_vals)
        z5_median = np.median(z5_vals)

        if z1_median:
            z1_median = round(z1_median, 4)
        if z2_median:
            z2_median = round(z2_median, 4)
        if z3_median:
            z3_median = round(z3_median, 4)
        if z4_median:
            z4_median = round(z4_median, 4)
        if z5_median:
            z5_median = round(z5_median, 4)

        num_faulting_entries = len(faulting_vals)
        filtered_faulting_vals = fc.mask_outliers(faulting_vals)
        num_outliers = int(np.sum(np.isnan(filtered_faulting_vals)))
        invalid_faulting_vals = fc.mask_invalid(faulting_vals)
        num_invalid = int(np.sum(np.isnan(invalid_faulting_vals)))
        filtered_faulting_vals = fc.nn_interpolate(filtered_faulting_vals)
        
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
            'num_faulting_vals': num_faulting_entries,
            'num_invalid': num_invalid,
            'num_outliers': num_outliers,
            'faulting_vals': faulting_vals.tolist(),
            'filtered_faulting_vals': filtered_faulting_vals.tolist(),
            'mean_faulting': mean_faulting,
            'stdev_faulting': stdev_faulting,
            'median_faulting': median_faulting,
            'p95_faulting': p95_faulting,
            'positive_faulting': positive_faulting,
            'z1_median': z1_median,
            'z2_median': z2_median,
            'z3_median': z3_median,
            'z4_median': z4_median,
            'z5_median': z5_median,
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
        ).sort("x_min", pymongo.ASCENDING)
        return raw_subjoints
    
    def get_faulting_data(self, bottom_joint: HorizontalJoint):
        """Gets all the faulting data for the slab of interest, identified
        with the bottom joint of the slab.

        
        Args:
            bottom_joint (HorizontalJoint): the bottom joint of the slab

        Returns:
            np.array: list of faulting values for the bottom joint
        """
        y_bottom_px = bottom_joint.get_max_y()
        y_top_px = bottom_joint.get_min_y()
        bottom_img_id = bottom_joint.get_bottom_img_id(self.scaler.num_images, self.scaler.px_height)
        top_img_id = bottom_joint.get_top_img_id(self.scaler.num_images, self.scaler.px_height)
        y_min_mm = self.scaler.convert_px_to_mm_relative(0, y_bottom_px % 1250, bottom_img_id)[1]
        y_max_mm = self.scaler.convert_px_to_mm_relative(0, y_top_px % 1250, top_img_id)[1]

        raw_subjoints = self.find_subjoints_in_range(y_min_mm, y_max_mm) 

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
        
    
    
            
    




            










