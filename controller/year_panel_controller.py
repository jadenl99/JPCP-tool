from PyQt5.QtCore import QObject, pyqtSlot
from PIL import Image
class YearPanelController(QObject):
    def __init__(self, year_panel_model):
        super().__init__()
        self._year_panel_model = year_panel_model

    
    @pyqtSlot(bool)
    def increment_slab(self, next=True):
        """Updates the displayed slab image to the next slab in the slab ID list

        Args:
            next (bool): if True, increments the slab index. Else, decrements 
            thw slab index.
        """
        model = self._year_panel_model
        if next:
            model.slab_id_list_index += 1  
        else:
            model.slab_id_list_index -= 1
        model.img_directory = (
            f'{model.base_img_directory}/'
            f'{model.slab_id_list[model.slab_id_list_index]}.jpg'
        )
        self._year_panel_model.refresh_CY_slab_info()
    

    @pyqtSlot(bool)
    def popup_original_image(self):
        """Opens a dialog box to display the original image of the slab
        """
        try:
            image = Image.open(self._year_panel_model.img_directory)
            image.show()   
        except:
            pass

    
    @pyqtSlot(list)
    def change_slab_state_info(self, states_pressed):
        """Changes the state of the slab based on the button pressed by the user
        in the model

        Args:
            states_pressed (list[str]): list of states pressed by the
            user, denoting the primary and secondary states of the slab. 
            list[0] is the primary state and list[1] is the secondary state.
        """
        primary_state_list = self._year_panel_model.primary_states
        secondary_state_list = self._year_panel_model.secondary_states
        slab_index = self._year_panel_model.slab_id_list_index

        
        primary_state_list[slab_index] = states_pressed[0]
        secondary_state_list[slab_index] = states_pressed[1]
        self._year_panel_model.panel_updated = True
    

    @pyqtSlot(bool)
    def change_replaced_info(self, is_replaced):
        """Changes the replaced state of the slab in the model

        Args:
            is_replaced (bool): whether the slab is replaced or not
        """
        
        index = self._year_panel_model.slab_id_list_index
        if is_replaced:
            self._year_panel_model.special_states[index] = 'R'
        else:
            self._year_panel_model.special_states[index] = None
        self._year_panel_model.panel_updated = True



    
        