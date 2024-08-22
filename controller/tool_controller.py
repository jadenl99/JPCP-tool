from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QLineEdit
import cv2
import os

class ToolController(QObject):
    def __init__(self, tool_model, year_controllers):
        """Constructor for ToolController, containing all the logic for the
        main window of the annotation tool.

        Args:
            tool_model (ToolModel): model containing all the data for the tool
            year_controllers (dict[int, YearPanelController]): mappings from 
            each registration year to its corresponding controller
        """
        super().__init__()
        self._tool_model = tool_model
        self._year_controllers = year_controllers
    

    @pyqtSlot(str, QLineEdit)
    def update_slabs_displayed(self, by_slab_id, slab_form):
        """Updates the displayed slabs in the annotation tool main window based
        on the base year slab ID selected by the user. Checks if within bounds
        of the first and last base year slab IDs.   

        Args:
            by_slab_id (str): base year slab ID selected by the user
            slab_form (QLineEdit): QLineEdit object containing the base year 
            slab index
        """
        if by_slab_id == '':
            return
        by_slab_id = int(by_slab_id)
        new_by_slab_id = int(by_slab_id)

        if by_slab_id < self._tool_model.first_BY_index:
            new_by_slab_id = self._tool_model.first_BY_index

        elif by_slab_id > self._tool_model.last_BY_index:
            new_by_slab_id = self._tool_model.last_BY_index
        
 
        self.update_year_slabs(new_by_slab_id)
        slab_form.setText(str(new_by_slab_id))  
    

    def update_year_slabs(self, by_slab_id):
        """Updates the displayed slabs in the annotation tool main window. 
        Also sends signals to update the database with changes made to the 
        existing slabs corresponding with the existing base year. Panels are 
        deactivated if no slabs are found for the particular year.

        Args:
            by_slab_id (int): base year slab ID to update associating CY slabs 
            to
        """
        img_type = self._tool_model.image_type.value
        reg_data = self._tool_model.reg_data
        seg_str = self._tool_model.seg_str  
        first_BY_index = self._tool_model.first_BY_index    
        for year, panel_model in self._tool_model.year_panel_models.items():
            if panel_model.panel_updated:
                panel_model.push_updates_to_db(seg_str)
                panel_model.panel_updated = False

            # fetch slab state information for CY slabs
            try:
                year_img_list = reg_data[by_slab_id - first_BY_index][str(year)]  
            except:
                year_img_list = None

            if year_img_list is None or len(year_img_list) == 0:
                # no slabs for this year, deactivate panel
                panel_model.img_directory = ''
                panel_model.lock_panel = True
            else:
                # slabs for this year, activate panel   
                if panel_model.lock_panel:
                    panel_model.lock_panel = False

                # update index, image path
                panel_model.slab_id_list_index = 0
                panel_model.slab_id_list = year_img_list    
                panel_model.base_img_directory = os.path.join(
                    self._tool_model.directory, str(year))

                suffix = None
                if img_type == 'Range' or img_type == 'Intensity':
                    suffix = img_type
                else:
                    suffix = os.path.join('Slabs', img_type)
                

                # set states for each CY slab
                panel_model.primary_states = []
                panel_model.secondary_states = []
                panel_model.special_states = []
                panel_model.intensity_replaced = []
                panel_model.slabs_info = {
                    'length' : [],
                    'width' : [],
                    'mean_faulting': [],
                    'start_im': [],
                    'end_im': [],
                    'comments': []
                }
                
                panel_model.populate_slab_info()
                panel_model.img_directory = os.path.join(
                    panel_model.base_img_directory, suffix
                    )


        self._tool_model.replaced_year = reg_data[by_slab_id - first_BY_index]['replaced']
        self._tool_model.replaced_type = reg_data[by_slab_id - first_BY_index]['replaced_type']
        # database updates   
        self._tool_model.execute_updates()
            

    @pyqtSlot(str)
    def update_image_type(self, img_type):
        """Updates the image type displayed for each year.

        Args:
            img_type (str): image type selected by the user
        """
        if img_type == self._tool_model.image_type.value:
            return
    
        self._tool_model.set_image_type(img_type)

        for panel_model in self._tool_model.year_panel_models.values():
            if not panel_model.lock_panel:
                # last_slash_index = panel_model.base_img_directory.rfind('/')
                # panel_model.base_img_directory = (
                #     panel_model.base_img_directory[:last_slash_index]
                #     + f'/{img_type}'
                # )
                suffix = None
                if img_type == 'Range' or img_type == 'Intensity':
                    suffix = img_type
                else:
                    suffix = os.path.join('Slabs', img_type)
                panel_model.img_directory = os.path.join(
                    panel_model.base_img_directory, suffix
                    )
    

    




