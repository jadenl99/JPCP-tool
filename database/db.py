from pymongo import MongoClient, UpdateOne
import pymongo
import os
from dotenv import load_dotenv

class SlabInventory():
    def __init__(self):
        load_dotenv()
        CONNECTION_STRING = os.getenv('SLAB_DB_CONN')

        try:
            self.client = MongoClient(CONNECTION_STRING)
        except:
            print('Error connecting to database')
            exit(1)
        self.db = self.client['jpcp_deterioration']
        self.registration_collection = self.db['registration']
        self.raw_subjoint_collection = self.db['raw_subjoint_data']
        self.slab_collection = self.db['slabs']
        self.requests = []


    def all_registration_data(self, filter = {}):
        """Gets all the slab registaration metadata, such as interstate, 
        direction, mileposts, and years registered for the slab id

        Args: filter (dict, optional): filter to apply to the query. 
        Default is an empty dictionary.

        Returns:
            pymongo.cursor.Cursor: A cursor object that can be used to iterate
            over each registration done
        """
        return self.registration_collection.find(filter)


    def execute_requests(self):
        """Executes all the requests in the requests list and clears all the
        requests after.
        """
        if self.requests:
            self.slab_collection.bulk_write(self.requests)
            self.requests = []  
    

    def add_slab_update_request(self, year, slab_index, update_data, seg_str):
        """Adds an update request to the requests list to update a certain 
        slab

        Args:
            year (int): year of the slab to update
            slab_index (int): slab index of the slab to update
            update_data (dict): data to update the slab with
            seg_str (str): segment string in the format "Ixx_MMxx_MMxx"
        """
        seg_yr_id = f"{seg_str}_{year}"
        self.requests.append(
            UpdateOne(
                {"slab_index": slab_index, "seg_year_id": seg_yr_id},
                {"$set": update_data}
                )
            )


    def upsert_slab_entry(self, year, slab_index, update_data, seg_str):
        """Updates or inserts a slab entry in the database

        Args:
            year (int): year of the slab
            slab_index (int): slab index of the slab
            update_data (dict): data to update the slab with
            seg_str (str): segment string in the format "Ixx_MMxx_MMxx"
        """
        seg_yr_id = f"{seg_str}_{year}"
        self.slab_collection.update_one(
            {"slab_index": slab_index, "seg_year_id": seg_yr_id},
            {"$set": update_data},
            upsert=True
        ) 
        
    
    def fetch_slab(self, year, slab_index, seg_str):
        """Fetches a slab from the database based on the year and slab index

        Args:
            year (int): year of the slab to fetch
            slab_index (int): slab index of the slab to fetch
            seg_str (str): segment string   
        Returns:
            dict: slab data of the slab fetched
        """
        seg_yr_id = f"{seg_str}_{year}"
        return self.slab_collection.find_one(
            {"slab_index": slab_index, "seg_year_id": seg_yr_id}
            )


    def fetch_seg_ids(self):
        """Fetches all the segment ids in the database

        Returns:
            list[str]: list of all the segment ids in the database
        """
        segments = self.db['segments'].find({})

        lst = []
        for seg in segments:
            lst.append(f"{seg['interstate']}_MM{seg['MM_start']}_MM{seg['MM_end']}")
        
        return lst


    def fetch_segment_data(self, interstate, start_mm, end_mm):
        """Fetches the segment data for the given interstate, start milepost,
        and end milepost

        Args:
            interstate (str): interstate of the segment
            start_mm (int): start milepost of the segment
            end_mm (int): end milepost of the segment

        Returns:
            dict: segment data for the given interstate, start milepost, and end
            milepost
        """
        return self.db['segments'].find_one(
            {"interstate": interstate, "MM_start": start_mm, "MM_end": end_mm}
            )   
    


    def get_year_slab_data(self, seg_str: str, year: int, start_slab: int=0):
        """Gets all slabs from the segment from a specified year

        Args:
            seg_str (str): segment string
            year (int): The year to get the slabs from
            start_slab (int, optional): The starting slab index. Defaults to 0.

        Raises:
            ValueError: If no slabs are found for the specified year

        Returns:
            Cursor: a cursor object containing all slabs
        """
        seg_year_id = f'{seg_str}_{year}'

        result = self.slab_collection.find(
            {'seg_year_id': seg_year_id,
            'slab_index': {'$gte': int(start_slab)}}
        ).sort('slab_index', pymongo.ASCENDING) 
        if not result:
            raise ValueError(f'No data found for the specified year {year}')

        return result
    

    def update_registration_data(self, registration_data: list[dict], 
                                 seg_str: str, base_year: int, 
                                 years: list[int]):
        """Updates the registration data in the registration collection

        Args:
            registration_data (list[dict]): The registration data to update
            seg_str (str): The segment id to update the registration data for
            base_year (int): The base year to update the registration data for
            years (list[int]): The years to update the registration data for
        """
        self.registration_collection.update_one(
            {'segment_id': seg_str,
             'base_year': base_year,
             'years': years},
            {'$set': {'registration_data': registration_data}}
        )
    

    def create_registration_entry(self, seg_str: str, base_year: int, 
                                  years: list[int]):
        """Deletes old entry and creates a new entry in the registration

        Args:
            seg_str (str): the segment string 
            base_year (int): the base year
            years (list[int]): list of years to be registered
        """
        self.registration_collection.delete_one({
            'segment_id': seg_str,
            'base_year': base_year,
            'years': years
        })
        entry = {
            'segment_id': seg_str,
            'base_year': base_year,
            'years': years,
            'registration_data': []
        }
        self.registration_collection.insert_one(entry)
    

    def add_crack_stats(self, slab_index, crack_length, avg_crack_width, 
                        seg_str, year):
        """Adds crack stats to the slab entry

        Args:
            slab_index (int): index of the slab
            crack_length (float): length of the crack
            avg_crack_width (float): average width of the crack
            seg_str (str): segment string
            year (int): year of the slab
        """
        seg_year_id = f'{seg_str}_{year}'
        self.slab_collection.update_one(
            {'seg_year_id': seg_year_id, 'slab_index': slab_index},
            {'$set': {'total_crack_length': crack_length, 'avg_crack_width': avg_crack_width}}
        )


    def delete_segment_year_slabs(self, seg_str: str, year: int):
        """Deletes all slabs in a segment for a given year

        Args:
            seg_str (str): The segment string
            year (int): The year to delete the slabs for
        """
        seg_year_id = f'{seg_str}_{year}'
        self.slab_collection.delete_many({'seg_year_id': seg_year_id})


    def find_subjoints_in_range(self, y_min: float, y_max: float, seg_str: str,
                                year: int):
        """Finds all subjoint data within the y-ranges

        Args:
            y_min (float): min y-value, expressed in mm, in terms of the whole
            segment
            y_max (float): max y-value, expressed in mm, in terms of the whole
            segment
            seg_str (str): the segment string
            year (int): the year of the data

        Returns:
            pymongo.cursor.Cursor: cursor object containing all subjoint data
            within the y-ranges
        """
        seg_year_id = f'{seg_str}_{year}'
        raw_subjoints = self.raw_subjoint_collection.find(
            {
                '$or': 
                [
                    {
                        'seg_year_id': seg_year_id,
                        'y_min': {'$gte': y_min - 100, '$lte': y_max + 100}
                    },
                    {
                        'seg_year_id': seg_year_id,
                        'y_max': {'$gte': y_min - 100, '$lte': y_max + 100}
                    }
                ]
            }
        ).sort("x_min", pymongo.ASCENDING)
        return raw_subjoints
    

    def write_slab_entry(self, seg_str: str, year: int, slab_index: int, 
                         length: float, width: float, start_im: int, 
                         end_im: int, y_offset: float, y_min: float, 
                         y_max: float, x_min: float, x_max: float, 
                         x_faulting_vals: list[float], x_reg_vals: list[float], 
                         faulting_vals: list[float], 
                         filtered_faulting_vals: list[float], 
                         mean_faulting: float, stdev_faulting: float,
                         median_faulting: float, p95_faulting: float,
                         positive_faulting: float, z1_median: float,
                         z2_median: float, z3_median: float, z4_median: float,
                         z5_median: float):
        """Performs an insert or update operation on the slab collection

        """
        query = {
            'seg_year_id': f'{seg_str}_{year}',
            'slab_index': slab_index
        }
        entry = {
            #'seg_year_id': f'{seg_str}_{year}',
            # 'slab_index': slab_index,
            'length': length,
            'width': width,
            'start_im': start_im,
            'end_im': end_im,
            'y_offset': y_offset,
            'y_min': y_min,
            'y_max': y_max,
            'x_min': x_min,
            'x_max': x_max,
            'x_faulting_vals': x_faulting_vals,
            'x_reg_vals': x_reg_vals,
            'faulting_vals': faulting_vals,
            'filtered_faulting_vals': filtered_faulting_vals,
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
            'total_crack_length': None,
            'avg_crack_width': None,
            'primary_state': None,
            'secondary_state': None,
            'special_state': None
        }
        self.slab_collection.update_one(query, {'$set': entry}, upsert=True)
        #self.slab_collection.insert_one(entry)


