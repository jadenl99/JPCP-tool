from pymongo import MongoClient, UpdateOne

class SlabInventory():
    def __init__(self):
        CONNECTION_STRING = 'mongodb://localhost:27017'
        self.client = MongoClient(CONNECTION_STRING)
        self.db = self.client['jpcp_deterioration']
        self.registration_collection = self.db['registration']
        self.slab_collection = self.db['slabs']
        self.requests = []
        self.segment_id = None
        self.seg_str = None


    def all_registration_metadata(self, filter = {}):
        """Gets all the slab registaration metadata, such as interstate, 
        direction, mileposts, and years registered for the slab id

        Args: filter (dict, optional): filter to apply to the query. 
        Default is an empty dictionary.

        Returns:
            pymongo.cursor.Cursor: A cursor object that can be used to iterate
            over each registration done
        """
        return self.registration_collection.find(
            filter, {"_id": 1, "segment_id": 1, "years" : 1, "base_year": 1}
            )


    def set_segment(self, seg):
        """Sets the segment_id to the given segment id and updates all the 
        necessary fields

        Args:
            seg (int): segment id to set the segment_id to
        """
        self.segment_id = seg
        self.seg_str = self.registration_collection.find_one(
            {"_id": self.segment_id}
        )['segment_id']

    
    def fetch_reg_data(self):
        """Fetches the registration data for the current segment_id.

        Returns:
            dict: registration data for the current segment_id
        """
        reg_data = self.registration_collection.find_one(
            {"_id": self.segment_id},
            {"_id": 0, "registration_data": 1}
            )
        
        return reg_data['registration_data']


    def execute_requests(self):
        """Executes all the requests in the requests list and clears all the
        requests after.
        """
        if self.requests:
            self.slab_collection.bulk_write(self.requests)
            self.requests = []  
    

    def add_slab_update_request(self, year, slab_index, update_data):
        """Adds an update request to the requests list to update a certain 
        slab

        Args:
            year (int): year of the slab to update
            slab_index (int): slab index of the slab to update
            update_data (dict): data to update the slab with
        """
        seg_yr_id = f"{self.seg_str}_{year}"
        self.requests.append(
            UpdateOne(
                {"slab_index": slab_index, "seg_year_id": seg_yr_id},
                {"$set": update_data}
                )
            ) 
        
    
    def fetch_slab(self, year, slab_index):
        """Fetches a slab from the database based on the year and slab index

        Args:
            year (int): year of the slab to fetch
            slab_index (int): slab index of the slab to fetch

        Returns:
            dict: slab data of the slab fetched
        """
        seg_yr_id = f"{self.seg_str}_{year}"
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
    
