from pymongo import MongoClient, UpdateOne
import pymongo
class SlabInventory():
    def __init__(self):
        CONNECTION_STRING = 'mongodb://localhost:27017'
        self.client = MongoClient(CONNECTION_STRING)
        self.db = self.client['jpcp_deterioration']
        self.registration_collection = self.db['registration']
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
            seg_str (str): segment string 
        """
        seg_yr_id = f"{seg_str}_{year}"
        self.requests.append(
            UpdateOne(
                {"slab_index": slab_index, "seg_year_id": seg_yr_id},
                {"$set": update_data}
                )
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
    

    # def update_offsets(self, seg_str: str, year: int, shift: float):
    #     """Updates the y_offset for all slabs in a year

    #     Args:
    #         seg_str (str): The segment string
    #         year (int): The year to update the offsets for
    #         shift (float): The amount to shift the slabs by
    #     """
    #     seg_year_id = f'{seg_str}_{year}'
    #     self.slab_collection.update_many(
    #         {'seg_year_id': seg_year_id},
    #         {'$inc': {'y_offset': shift}}
    #     )
