import pymongo
from pymongo import MongoClient
class RegistrationWriter:
    def __init__(self, beginMM: int, endMM: int, interstate: str,
                 base_year: int, years: list[int]): 
        CONNECTION_STRING = 'mongodb://localhost:27017'
        self.client = MongoClient(CONNECTION_STRING)
        self.db = self.client['jpcp_deterioration']
        self.registration_collection = self.db['registration']
        self.slab_collection = self.db['slabs']
        self.beginMM = beginMM
        self.endMM = endMM
        self.interstate = interstate.replace("-", "")
        self.segment_id = self.get_seg_id()
        self.base_year = base_year
        self.years = years

        
        self.create_registration_entry()
            

    def get_year_slab_data(self, year: int, start_slab: int=0):
        """Gets all slabs from the segment from a specified year

        Args:
            year (int): The year to get the slabs from
            start_slab (int, optional): The starting slab index. Defaults to 0.

        Raises:
            ValueError: If no slabs are found for the specified year

        Returns:
            Cursor: a cursor object containing all slabs
        """
        seg_year_id = f'{self.interstate}_MM{self.beginMM}_MM{self.endMM}_{year}'
        result = self.slab_collection.find(
            {'seg_year_id': seg_year_id,
            'slab_index': {'$gte': start_slab}}
        ).sort('slab_index', pymongo.ASCENDING) 
        if not result:
            raise ValueError(f'No data found for the specified year {year}')
        return result
    

    def get_seg_id(self):
        seg = self.db['segments'].find_one({'interstate': self.interstate,
                                            'MM_start': self.beginMM,
                                            'MM_end': self.endMM})
        if not seg:
            raise ValueError('Segment does not exist in the database')  
        return seg['_id']
    

    def create_registration_entry(self):
        """Deletes old entry and creates a new entry in the registration
        """
        self.registration_collection.delete_one({
            'segment_id': self.segment_id,
            'base_year': self.base_year,
            'years': self.years
        })
        entry = {
            'segment_id': self.segment_id,
            'base_year': self.base_year,
            'years': self.years,
            'registration_data': []
        }
        self.registration_collection.insert_one(entry)

    
    def update_registration_data(self, registration_data: list[dict]):
        """Updates the registration data in the registration collection

        Args:
            registration_data (list[dict]): The registration data to update
        """
        self.registration_collection.update_one(
            {'segment_id': self.segment_id,
             'base_year': self.base_year,
             'years': self.years},
            {'$set': {'registration_data': registration_data}}
        )

    def get_slab_data(self, year: int, slab_index: int, 
                      status_only: bool = False):
        """Gets the data for a specific slab

        Args:
            year (int): The year the slab is from
            slab_index (int): The index of the slab
            status_only (bool, optional): If True, only the status 
            (average faulting/slab states/length) of the slab is returned. 
            Defaults to False.

        Raises:
            ValueError: If no data is found for the specified slab
        Returns:
            dict: The slab data
        """
        seg_year_id = f'{self.interstate}_MM{self.beginMM}_MM{self.endMM}_{year}'
        if status_only:
            result = self.slab_collection.find_one(
                {'seg_year_id': seg_year_id, 
                 'slab_index': slab_index},
                {'_id': 0, 'mean_faulting': 1, 'primary_state': 1, 
                 'secondary_state': 1, 'special_state': 1, 'length': 1}
            )
        else: 
            result = self.slab_collection.find_one(
                {'seg_year_id': seg_year_id, 
                'slab_index': slab_index}
            )
        if not result:
            raise ValueError(f'No data found for the specified slab '
                             f'{slab_index} in the year {year}')
        return result
    

    def update_offsets(self, year: int, shift: float):
        """Updates the y_offset for all slabs in a year

        Args:
            year (int): The year to update the offsets for
            shift (float): The amount to shift the slabs by
        """
        seg_year_id = f'{self.interstate}_MM{self.beginMM}_MM{self.endMM}_{year}'
        self.slab_collection.update_many(
            {'seg_year_id': seg_year_id},
            {'$inc': {'y_offset': shift}}
        )



