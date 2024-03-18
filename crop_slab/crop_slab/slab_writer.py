from pymongo import MongoClient

class SlabWriter:
    def __init__(self, db_name: str, year: int):
        # set up connection to database
        CONNECTION_STRING = 'mongodb://localhost:27017'
        self.client = MongoClient(CONNECTION_STRING)

        
        self.db = self.client[db_name]
        if str(year) in self.db.list_collection_names():
            self.db.drop_collection(str(year))
        
        self.collection_name = self.db[str(year)]

    
    def write_slab_entry(self, slab_index, length, width, start_im, end_im, 
                         y_offset, y_min, y_max):
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
        """

        entry = {
            'slab_index': slab_index,
            'length': length,
            'width': width,
            'start_im': start_im,
            'end_im': end_im,
            'y_offset': y_offset,
            'y_min': y_min,
            'y_max': y_max,
            'primary_state': None,
            'secondary_state': None
        }

        self.collection_name.insert_one(entry)











