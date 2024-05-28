from PyQt5.QtCore import QObject, pyqtSignal
from enum import Enum

class ImageType(Enum):
    RANGE = 'output_range'
    INTENSITY = 'output_intensity'

class ToolModel(QObject):
    replaced_year_changed = pyqtSignal(int)
    replaced_type_changed = pyqtSignal(str)
    def __init__(self, year_panel_models, slab_inventory, directory,
                 all_reg_data):
        """Constructor for ToolModel, containing data for the annotation tool 
        main window

        Args:
            year_panel_models (dict[int, YearPanelModel]): dictionary mapping 
            of the registration years to their corresponding models
            slab_inventory (SlabInventory): database containing all the slab 
            information
            directory (str): directory of the slab data  
            all_reg_data (dict): registration data and metadata for the specific
            registration being annotated
        """
        super().__init__()
        self._year_panel_models = year_panel_models
        self._base_year = all_reg_data['base_year']
        self._seg_id = all_reg_data['_id']
        self._seg_str = all_reg_data['segment_id']
        self._reg_data = all_reg_data['registration_data']
        self._directory = directory
        self._slab_inventory = slab_inventory
        self._image_type = ImageType.RANGE
        self._first_BY_index = self._reg_data[0]['base_id']
        self._last_BY_index = self._reg_data[-1]['base_id'] 
        self._current_BY_index = self._first_BY_index
        self._replaced_year = self._reg_data[0]['replaced']
        self._replaced_type = self._reg_data[0]['replaced_type']
        


    @property
    def replaced_year(self):
        return self._replaced_year
    

    @replaced_year.setter
    def replaced_year(self, replaced_year):
        self._replaced_year = replaced_year
        self.replaced_year_changed.emit(replaced_year)


    
    @property
    def replaced_type(self):
        return self._replaced_type
    

    @replaced_type.setter
    def replaced_type(self, replaced_type):
        self._replaced_type = replaced_type
        self.replaced_type_changed.emit(replaced_type)


    @property
    def first_BY_index(self):
        return self._first_BY_index 
    

    @property
    def last_BY_index(self):
        return self._last_BY_index


    @property
    def year_panel_models(self):
        return self._year_panel_models  
    

    @property
    def reg_data(self):
        return self._reg_data


    @property
    def image_type(self):
        return self._image_type
    
    
    def set_image_type(self, image_type):
        """Sets image type based on string provided

        Args:
            image_type (str): image type to set
        """
        if image_type == 'output_intensity':
            self._image_type = ImageType.INTENSITY
        else:
            self._image_type = ImageType.RANGE


    @property
    def directory(self):
        return self._directory
    

    @property
    def seg_id(self):
        return self._seg_id
    

    @seg_id.setter
    def seg_id(self, seg_id):
        self._seg_id = seg_id


    @property
    def seg_str(self):
        return self._seg_str
    

    @seg_str.setter
    def seg_str(self, seg_str):
        self._seg_str = seg_str

        
    def execute_updates(self):
        """Executes all the requests in the requests list stored in the 
        database object and clears all the requests after.
        """ 
        self._slab_inventory.execute_requests()


        