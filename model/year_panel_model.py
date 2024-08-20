from PyQt5.QtCore import QObject, pyqtSignal

class ImageSignal(QObject):
    """Signal class for sending changes to the YearPanelView to update the
    image displayed
    """
    image_changed = pyqtSignal(str)


class BackButtonEnableSignal(QObject):
    """Signal class for sending changes to the YearPanelView to enable or
    disable the back button. If True, the back button is enabled. If False, the
    back button is disabled.
    """
    back_btn_enable = pyqtSignal(bool)


class NextButtonEnableSignal(QObject):
    """Signal class for sending changes to the YearPanelView to enable or
    disable the next button. If True, the next button is enabled. If False, the
    next button is disabled.
    """
    next_btn_enable = pyqtSignal(bool)


class LockPanelSignal(QObject):
    """Signal class for sending changes to the YearPanelView to lock or unlock
    the year panel.
    """
    lock_panel = pyqtSignal(bool)

class SlabStateSignal(QObject):
    """Signal class for sending changes to the YearPanelView to update the 
    state of the slab. Will be in the form (primary_state, secondary_state, 
    special_state, length, width, mean_faulting)
    """
    state_changed = pyqtSignal(tuple)


class YearPanelModel(QObject):
    
    def __init__(self, year, slab_inventory, seg_str):
        """Constructor for YearPanelModel, containing all data for a speicific
        image in a given year to display in a YearPanel.

        Args:
            year (int): year the model is responsible
            slab_inventory (SlabInventory): database containing all the slab 
            data
            seg_str (str): segment string identifying the segment
        """
        super().__init__()
        self.image_signal = ImageSignal()
        self.lock_panel_signal = LockPanelSignal()
        self.next_btn_enable_signal = NextButtonEnableSignal()
        self.back_btn_enable_signal = BackButtonEnableSignal()
        self.state_changed_signal = SlabStateSignal()   
        self._panel_updated = False
        self._year = year
        self._slab_inventory = slab_inventory
        self._slab_id_list = None
        self._lock_panel = False
        self._slab_id_list_index = None
        self._base_img_directory = None
        self._img_directory = None
        self._primary_states = None
        self._secondary_states = None
        self._special_states = None
        self._intensity_replaced = None
        self._slabs_info = None
        self._seg_str = seg_str


    @property
    def panel_updated(self):
        return self._panel_updated
    

    @panel_updated.setter
    def panel_updated(self, panel_updated):
        self._panel_updated = panel_updated


    @property
    def year(self):
        return self._year
    

    @property
    def base_img_directory(self):
        return self._base_img_directory
    
    
    @base_img_directory.setter
    def base_img_directory(self, base_img_directory):
        self._base_img_directory = base_img_directory


    @property
    def img_directory(self):
        return self._img_directory
    

    @img_directory.setter
    def img_directory(self, img_directory):
        self._img_directory = img_directory
        self.image_signal.image_changed.emit(self._img_directory)


    @property
    def lock_panel(self):
        return self._lock_panel 
    

    @lock_panel.setter
    def lock_panel(self, lock_panel):
        self._lock_panel = lock_panel
        self.lock_panel_signal.lock_panel.emit(self._lock_panel)


    @property
    def primary_states(self):
        return self._primary_states
    

    @primary_states.setter
    def primary_states(self, primary_states):
        self._primary_states = primary_states
    
    
    @property
    def secondary_states(self):
        return self._secondary_states
    

    @secondary_states.setter
    def secondary_states(self, secondary_states):
        self._secondary_states = secondary_states


    @property
    def special_states(self):
        return self._special_states
    

    @special_states.setter
    def special_states(self, special_states):
        self._special_states = special_states
    

    @property
    def intensity_replaced(self):
        return self._intensity_replaced


    @intensity_replaced.setter
    def intensity_replaced(self, intensity_replaced):
        self._intensity_replaced = intensity_replaced


    @property
    def slabs_info(self):
        return self._slabs_info
    

    @slabs_info.setter
    def slabs_info(self, slabs_info):
        self._slabs_info = slabs_info


    @property
    def slab_id_list_index(self):
        return self._slab_id_list_index
    

    @slab_id_list_index.setter
    def slab_id_list_index(self, slab_id_list_index):
        self._slab_id_list_index = slab_id_list_index


    @property
    def slab_id_list(self):
        return self._slab_id_list


    @slab_id_list.setter
    def slab_id_list(self, slab_id_list):
        self._slab_id_list = slab_id_list


    def populate_slab_info(self):
        """Populates necessary fields for the current slab based on slab ID. 
        Fetches data from the database and notifies view of changes upon the
        slab switch.

        Args:
            slab_id (int): slab ID to switch to
        """
        for slab_id in self._slab_id_list:
            slab_data = self._slab_inventory.fetch_slab(self._year, slab_id,
                                                        self._seg_str)
            self._primary_states.append(slab_data['primary_state'])
            self._secondary_states.append(slab_data['secondary_state'])
            self._special_states.append(slab_data['special_state'])
            if 'intensity_replaced' not in slab_data:
                self._intensity_replaced.append(None)
            else:
                self._intensity_replaced.append(slab_data['intensity_replaced'])
            if slab_data['length'] is None:
                self._slabs_info['length'].append(None)
            else:
                self._slabs_info['length'].append(slab_data['length'] / 304.8)
            if slab_data['width'] is None:
                self._slabs_info['width'].append(None)
            else:
                self._slabs_info['width'].append(slab_data['width'] / 304.8)
            self._slabs_info['mean_faulting'].append(slab_data['mean_faulting'])
            self._slabs_info['start_im'].append(slab_data['start_im'])
            self._slabs_info['end_im'].append(slab_data['end_im'])

        self.refresh_CY_slab_info()
    
    
    def refresh_CY_slab_info(self):
        """Updates state information about the current slab id.  
        """
        slab_id = self._slab_id_list_index
        print(slab_id)
        state_tuple = (self._primary_states[slab_id], 
                        self._secondary_states[slab_id],
                        self._special_states[slab_id],
                        self._intensity_replaced[slab_id],
                        self._slabs_info['length'][slab_id],
                        self._slabs_info['width'][slab_id],
                        self._slabs_info['mean_faulting'][slab_id],
                        self._slab_id_list[slab_id],
                        self._slabs_info['start_im'][slab_id],
                        self._slabs_info['end_im'][slab_id])
        self.state_changed_signal.state_changed.emit(state_tuple)

        # update the back and next buttons
        if self._slab_id_list_index == 0:
            self.back_btn_enable_signal.back_btn_enable.emit(False)
        else:
            self.back_btn_enable_signal.back_btn_enable.emit(True)
        if self._slab_id_list_index < len(self._slab_id_list) - 1:
            self.next_btn_enable_signal.next_btn_enable.emit(True)
        else:
            self.next_btn_enable_signal.next_btn_enable.emit(False)
        

    def push_updates_to_db(self, seg_str):
        """Sends a request to the database to update a certain slab. 

        Args:
            seg_str (str): segment string identifying the segment
        """
        if self._panel_updated and not self._lock_panel:
            for i in range(len(self._slab_id_list)):
                self._slab_inventory.add_slab_update_request(
                    self._year, self._slab_id_list[i],
                    {
                        'primary_state': self._primary_states[i],
                        'secondary_state': self._secondary_states[i],
                        'special_state': self._special_states[i],
                        'intensity_replaced': self._intensity_replaced[i]
                    },
                    seg_str
                )

                
            
           

