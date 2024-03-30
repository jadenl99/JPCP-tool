from pymongo import MongoClient
from datetime import datetime
class DBWriter:
    def __init__(self, interstate: str, MM_start: int,
                 MM_end: int, year: int, mm_height: int):
        # set up connection to database
        self.CONNECTION_STRING = 'mongodb://localhost:27017'
        self.client = MongoClient(self.CONNECTION_STRING)
        self.db = self.client['jpcp_deterioration']    
        self.subjoint_collection = self.db['raw_subjoint_data']
        self.segment_collection = self.db['segments']
        self.img_collection = self.db['image_data']
        self.mm_height = mm_height  
        self.year = year
        self.MM_start = MM_start
        self.MM_end = MM_end
        self.interstate = interstate

        self.year_id = self.update_segment_entry()

        # in case there are any entries from previous runs
        self.subjoint_collection.delete_many({'seg_year_id': self.year_id})
        self.img_collection.delete_many({'seg_year_id': self.year_id})


    def write_faulting_entry(self, 
                             index: int, 
                             endpoints: tuple[float], 
                             faulting_info: list[tuple[float, float]]):
        """Writes an entry to the faulting_values collection in the database.

        Args:
            index (int): index of the current XML file
            endpoints (tuple): (x1, y1, x2, y2), the endpoints of the subjoint
            in millimeters
            faulting_info (str): the faulting information of the subjoint
        """
        y1 = endpoints[1] + self.mm_height * index
        y2 = endpoints[3] + self.mm_height * index
        x1 = endpoints[0]
        x2 = endpoints[2]
        max_x = max(x1, x2)
        min_x = min(x1, x2)
        filtered_faulting_info = [item
                                  for item 
                                  in faulting_info 
                                  if min_x <= item['x_val'] <= max_x]
        entry = {
            'seg_year_id': self.year_id,
            'faulting_info': filtered_faulting_info,
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
        seg_id = (f'{self.interstate}_MM{self.MM_start}_' + 
                  f'MM{self.MM_end}')
        seg_year_id = (f'{self.interstate}_MM{self.MM_start}_' + 
                       f'MM{self.MM_end}_{self.year}')
        
        template = {
            '_id': seg_id, # 'interstate_MMstart_MMend
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
    

    def write_image_entry(self, index: str, date: datetime):
        """Writes an entry to the image_data collection in the database.

        Args:
            index (int): index of the current XML file
        """
        entry = {
            'seg_year_id': self.year_id,
            'img_id': int(index),
            'date': date
        }
        self.img_collection.insert_one(entry)