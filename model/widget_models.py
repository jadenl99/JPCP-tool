from PyQt5.QtCore import QObject, pyqtSignal


class ClassificationModel(QObject):
    registration_changed = pyqtSignal(str)
    registrations_changed = pyqtSignal()
    def __init__(self, slab_inventory, menu_model):
        """Constructor for ClassificationModel

        Args:
            slab_inventory (SlabInventory): Database connection
            menu_model (MenuModel): Model for main menu
        """
        super().__init__()
        self._menu_model = menu_model
        self._registration = ''
        self._registrations = {}
        self._slab_inventory = slab_inventory   
 



    def construct_registration_list(self):
        """Construct a list of registrations for the given segment ID, and
        stores mapping between years and the corresponding registration 
        metadata.

        Args:
            seg_id (str): segment ID
        """
        registrations = {}
        reg_metadata = self._slab_inventory.all_registration_data(
            filter={"segment_id": self._menu_model.segment_id}
        )
        for reg in reg_metadata:
            by = reg['base_year']
            years = reg['years']
            year_str = ''
            for year in years:
                if year == by:
                    year_str += f'BY{year}, '
                else:
                    year_str += f'{year}, '
            year_str = year_str[:-2]
            registrations[year_str] = reg
        self.registrations = registrations


    @property
    def registration(self):
        return self._registration

    @registration.setter
    def registration(self, registration):
        self._registration = registration
        self.registration_changed.emit(registration)

    @property
    def registrations(self):
        return self._registrations

    @registrations.setter
    def registrations(self, registrations):
        self._registrations = registrations
        self.registrations_changed.emit()

    @property
    def years(self):
        return self._years

    @years.setter
    def years(self, years):
        self._years = years


class RegistrationModel(QObject):
    years_changed = pyqtSignal(list)
    def __init__(self, slab_inventory, menu_model):
        """Constructor for RegistrationModel
        """
        super().__init__()
        self._slab_inventory = slab_inventory
        self._menu_model = menu_model
        self._years = [] 
        self._years_selected = {}
        self._by_selected = None
        self._faulting_mode = 'average'


    def construct_years_list(self):
        """Construct a list of years for the selected interstate
        """
        seg_id = self._menu_model.segment_id
        data = seg_id.split('_')
        interstate = data[0]
        start_mm = int(data[1][2:])
        end_mm = int(data[2][2:])
        seg_data = self._slab_inventory.fetch_segment_data(
            interstate, start_mm, end_mm
        )

        years = list(seg_data['years'].keys())
        years.sort()
        self.years = years 
    

    @property
    def years(self):
        return self._years


    @years.setter
    def years(self, years):
        self._years = years
        self.years_changed.emit(years)

    @property
    def years_selected(self):
        return self._years_selected
    

    @years_selected.setter
    def years_selected(self, years_selected):
        self._years_selected = years_selected

    
    @property
    def by_selected(self):
        return self._by_selected
    

    @by_selected.setter
    def by_selected(self, by_selected):
        self._by_selected = by_selected
    

    @property
    def faulting_mode(self):
        return self._faulting_mode
    

    @faulting_mode.setter
    def faulting_mode(self, faulting_mode):
        self._faulting_mode = faulting_mode
        

    