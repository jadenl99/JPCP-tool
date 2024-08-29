from pymongo import MongoClient
import os
CONNECTION_STRING = 'mongodb://localhost:27017'
client = MongoClient(CONNECTION_STRING)
db = client['jpcp_deterioration']
slab_collection = db['slabs']


slab_collection.update_many({
    'seg_year_id': 'I16EB_MM12_MM22_2018',
    'slab_index': {'$gte': 2482}
    }, {
    "$inc" : {'slab_index' : 11}
    })

# use 2014 lengths for 2013 slabs
for i in range(2481, 2493):
    slab = slab_collection.find_one({
        'seg_year_id': 'I16EB_MM12_MM22_2017',
        'slab_index': i
    })
    slab_collection.update_one({
        'seg_year_id': 'I16EB_MM12_MM22_2018',
        'slab_index': i
        }, {    
        "$set" : {
            'length': slab['length'],
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
            'special_state': None,
            'comments': 'Adjustment for lane drift'}
    }, upsert=True)

def sort_by_number(filename):
    return int(filename.split('.')[0])  

dir = "C://Users//jaden//Documents//GitHub//JPCP-tool//I16EB//2018//Slabs//output_range//" # Change this to the directory of the 2018 range images
dir_list = os.listdir(dir)
dir_list.sort(key=sort_by_number, reverse=True)
for filename in dir_list:
    number = int(filename.split('.')[0])
    if number >= 2482:
        os.rename(dir + filename, dir + str(number + 11) + '.jpg')

dir = "C://Users//jaden//Documents//GitHub//JPCP-tool//I16EB//2018//Slabs//output_intensity//" # Change this to the directory of the 2018 intensity images
for filename in dir_list:
    number = int(filename.split('.')[0])
    if number >= 2482:
        os.rename(dir + filename, dir + str(number + 11) + '.jpg')    
    
print("2018EB adjusted")