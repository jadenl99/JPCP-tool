from pymongo import MongoClient

class DBWriter:
    def __init__(self, interstate: str, MM_start: int,
                 MM_end: int, year: int, px_height: int):
        # set up connection to database
        self.CONNECTION_STRING = 'mongodb://localhost:27017'
        self.client = MongoClient(self.CONNECTION_STRING)
        self.db = self.client['jpcp_deterioration']    
        self.subjoint_collection = self.db['raw_subjoint_data']
        self.segment_collection = self.db['segments']
        
        self.px_height = px_height  
        self.year = year
        self.MM_start = MM_start
        self.MM_end = MM_end
        self.interstate = interstate

        self.year_id = self.update_segment_entry()

        # in case there are any entries from previous runs
        self.subjoint_collection.delete_many({'seg_year_id': self.year_id})


    def write_faulting_entry(self, 
                             index: int, 
                             endpoints: tuple[float], 
                             faulting_info: str):
        """Writes an entry to the faulting_values collection in the database.

        Args:
            index (int): index of the current XML file
            endpoints (tuple): (x1, y1, x2, y2), the endpoints of the subjoint
            in millimeters
            faulting_info (str): the faulting information of the subjoint
        """
        y1 = endpoints[1] + self.px_height * index
        y2 = endpoints[3] + self.px_height * index
        x1 = endpoints[0]
        x2 = endpoints[2]
        entry = {
            'seg_year_id': self.year_id,
            'faulting_info': faulting_info,
            'y_min': min(y1, y2),
            'y_max': max(y1, y2),
            'x_min': min(x1, x2),
            'x_max': max(x1, x2)
        }
        self.subjoint_collection.insert_one(entry)


    def update_segment_entry(self):
        """Writes an entry to the segments collection in the database. If it
        already exists, it updates the year if needed (else it does 
        nothing). Returns the id of the year of the specific segment for 
        asssociation matching.

        Returns:
            int: the id of the year of the specific segment for association 
            matching
        """

        query = {
            'interstate': self.interstate,
            'MM_start': self.MM_start,
            'MM_end': self.MM_end
        }
        seg_year_id = (f'{self.interstate}_MM{self.MM_start}_' + 
                       f'MM{self.MM_end}_{self.year}')
        
        template = {
            'interstate': self.interstate,
            'MM_start': self.MM_start,
            'MM_end': self.MM_end,
            'years': {str(self.year): seg_year_id}
        }

        seg_entry = self.segment_collection.find_one(query)
        # segment does not exist, create it
        if not seg_entry:
            self.segment_collection.insert_one(template)
        # segment exists, add year if needed
        elif str(self.year) not in seg_entry['years']:
            self.segment_collection.update_one(
                seg_entry,
                {'$set': {f'years.{self.year}': seg_year_id}}
            )
        
        return seg_year_id
