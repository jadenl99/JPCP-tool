from pymongo import MongoClient
from crop_slab.joint import HorizontalJoint
import warnings
from utils.px_mm_converter import PXMMConverter
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
        
        faulting_val = self.calc_faulting(bottom_joint)
        if faulting_val:
            faulting_val = round(faulting_val, 2)


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
            'faulting_val': faulting_val,
            'primary_state': None,
            'secondary_state': None,
            'special_state': None
        }

        self.slab_collection.insert_one(entry)


    def calc_faulting(self, bottom_joint: HorizontalJoint):
        """Calculates the faulting value of the slab. Averages all faulting
        values within the wheelpath of the slab. Negative values are treated
        as 0. Representation below not to scale.

        |-----------|---WP---|------|------|---WP---|-----------|
        |edge buffer|   1m   |0.375m|0.375m|   1m   |edge buffer|   
       
        Args:
            bottom_joint (HorizontalJoint): the bottom joint of the slab

        Returns:
            float: the faulting value of the slab
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
            return None

        left_wp = (x_min_mm + edge_buffer, x_min_mm + edge_buffer + 1000)
        right_wp = (x_max_mm - edge_buffer - 1000, x_max_mm - edge_buffer)
        y_bottom_px = bottom_joint.get_max_y()
        y_top_px = bottom_joint.get_min_y()
        bottom_img_id = bottom_joint.get_bottom_img_id(self.scaler.num_images, self.scaler.px_height)
        top_img_id = bottom_joint.get_top_img_id(self.scaler.num_images, self.scaler.px_height)
        # print(y_bottom_px, y_top_px, bottom_img_id, top_img_id)
        y_min_mm = self.scaler.convert_px_to_mm_relative(0, y_bottom_px % 1250, bottom_img_id)[1]
        y_max_mm = self.scaler.convert_px_to_mm_relative(0, y_top_px % 1250, top_img_id)[1]
        # find all subjoints that are within the y-range of the bottom joint
        # of the slab
        raw_subjoints = self.raw_subjoint_collection.find(
            {
                '$or': 
                [
                    {
                        'seg_year_id': self.seg_year_id,
                        'y_min': {'$gte': y_min_mm - 100, '$lte': y_max_mm + 100}
                    },
                    {
                        'seg_year_id': self.seg_year_id,
                        'y_max': {'$gte': y_min_mm - 100, '$lte': y_max_mm + 100}
                    }
                ]
            }
        )


        total, entries = 0, 0
        for raw_subjoint in raw_subjoints:
            sx_min = raw_subjoint['x_min']
            sx_max = raw_subjoint['x_max']
            fault_vals = raw_subjoint['faulting_info']
            if not fault_vals:
                continue
            # width of each faulting value
            single_width = (sx_max - sx_min) / len(fault_vals)
          
            # check left wheelpath
            l_left = max(sx_min, left_wp[0])
            l_right = min(sx_max, left_wp[1])
            left_overlap = l_right - l_left
            if left_overlap > 0:
                l = int((l_left - sx_min) / single_width)
                r = int((l_right - sx_min) / single_width)
                res = fault_vals[l:r+1]
                res = [abs(x) for x in res] 
                total += sum(res)
                entries += len(res)
            
            # check right wheelpath
            r_left = max(sx_min, right_wp[0])
            r_right = min(sx_max, right_wp[1])
            right_overlap = r_right - r_left
            if right_overlap > 0:
                l = int((r_left - sx_min) / single_width)
                r = int((r_right - sx_min) / single_width)
                res = fault_vals[l:r+1]
                res = [abs(x) for x in res]
                total += sum(res)
                entries += len(res)

        if entries == 0:
            return None
        return float(total) / entries
    




            










