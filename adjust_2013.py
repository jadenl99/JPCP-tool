import pymongo
from pymongo import MongoClient
import os
CONNECTION_STRING = 'mongodb://localhost:27017'
client = MongoClient(CONNECTION_STRING)
db = client['jpcp_deterioration']
slab_collection = db['slabs']

slab_collection.update_many({
    'seg_year_id': 'I16WB_MM22_MM12_2013',
    'slab_index': {'$gte': 1536}
    }, {
    "$inc" : {'slab_index' : 4}
    })

slab_collection.update_one({
    'seg_year_id': 'I16WB_MM22_MM12_2013',
    'slab_index': 1535
    }, {
    "$set" : {'length' : 7100}
})

slab_collection.insert_one({
            'seg_year_id': 'I16WB_MM22_MM12_2013',
            'slab_index': 1536,
            'length': 5096,
            'width': 0,
            'start_im': None,
            'end_im': None,
            'y_offset': 0,
            'y_min': 0,
            'y_max': 0,
            'num_faulting_vals': None,
            'num_invalid': None,
            'num_outliers': None,
            'faulting_vals': None,
            'filtered_faulting_vals': None,
            'mean_faulting': None,
            'stdev_faulting': None,
            'median_faulting': None,
            'p95_faulting': None,
            'positive_faulting': None,
            'z1_median': None,
            'z2_median': None,
            'z3_median': None,
            'z4_median': None,
            'z5_median': None,
            'primary_state': None,
            'secondary_state': None,
            'special_state': None
        })
    
slab_collection.insert_one({
            'seg_year_id': 'I16WB_MM22_MM12_2013',
            'slab_index': 1537,
            'length': 4868,
            'width': 0,
            'start_im': None,
            'end_im': None,
            'y_offset': 0,
            'y_min': 0,
            'y_max': 0,
            'x_min': 0,
            'x_max': 0,
            'x_faulting_vals': None,
            'x_reg_vals': None,
            'faulting_vals': None,
            'filtered_faulting_vals': None,
            'mean_faulting': None,
            'stdev_faulting': None,
            'median_faulting': None,
            'p95_faulting': None,
            'positive_faulting': None,
            'z1_median': None,
            'z2_median': None,
            'z3_median': None,
            'z4_median': None,
            'z5_median': None,
            'primary_state': None,
            'total_crack_length': None,
            'avg_crack_width': None,
            'secondary_state': None,
            'special_state': None
        })
    
slab_collection.insert_one({
            'seg_year_id': 'I16WB_MM22_MM12_2013',
            'slab_index': 1538,
            'length': 6640,
            'width': 0,
            'start_im': None,
            'end_im': None,
            'y_offset': 0,
            'y_min': 0,
            'y_max': 0,
            'x_min': 0,
            'x_max': 0,
            'x_faulting_vals': None,
            'x_reg_vals': None,
            'faulting_vals': None,
            'filtered_faulting_vals': None,
            'mean_faulting': None,
            'stdev_faulting': None,
            'median_faulting': None,
            'p95_faulting': None,
            'positive_faulting': None,
            'z1_median': None,
            'z2_median': None,
            'z3_median': None,
            'z4_median': None,
            'z5_median': None,
            'total_crack_length': None,
            'avg_crack_width': None,
            'primary_state': None,
            'secondary_state': None,
            'special_state': None
        })

slab_collection.insert_one({
            'seg_year_id': 'I16WB_MM22_MM12_2013',
            'slab_index': 1538,
            'length': 7044,
            'width': 0,
            'start_im': None,
            'end_im': None,
            'y_offset': 0,
            'y_min': 0,
            'y_max': 0,
            'x_min': 0,
            'x_max': 0,
            'x_faulting_vals': None,
            'x_reg_vals': None,
            'faulting_vals': None,
            'filtered_faulting_vals': None,
            'mean_faulting': None,
            'stdev_faulting': None,
            'median_faulting': None,
            'p95_faulting': None,
            'positive_faulting': None,
            'z1_median': None,
            'z2_median': None,
            'z3_median': None,
            'z4_median': None,
            'z5_median': None,
            'total_crack_length': None,
            'avg_crack_width': None,
            'primary_state': None,
            'secondary_state': None,
            'special_state': None
        })



def sort_by_number(filename):
    return int(filename.split('.')[0])  




dir = "C://Users//jaden//Documents//GitHub//JPCP-tool//data//2013//Slabs//output_range//" # Change this to the directory of the range images
dir_list = os.listdir(dir)
dir_list.sort(key=sort_by_number, reverse=True)
for filename in dir_list:
    number = int(filename.split('.')[0])
    if number >= 1536:
        os.rename(dir + filename, dir + str(number + 4) + '.jpg')

dir = "C://Users//jaden//Documents//GitHub//JPCP-tool//data//2013//Slabs//output_intensity//" # Change this to the directory of the 2013 intensity images
for filename in dir_list:
    number = int(filename.split('.')[0])
    if number >= 1536:
        os.rename(dir + filename, dir + str(number + 4) + '.jpg')           


dir = "C://Users//jaden//Documents//GitHub//JPCP-tool//data//2013//Slabs//output_segmentation//" # Change this to the directory of the 2013 intensity images
for filename in dir_list:
    number = int(filename.split('.')[0])
    if number >= 1536:
        os.rename(dir + filename, dir + str(number + 4) + '.jpg')            


print("Successfully updated the database.")
