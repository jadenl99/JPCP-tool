from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QAbstractButton
class ClassificationController(QObject):
    def __init__(self, classification_model, app):
        """Constructor for ClassificationController

        Args:
            menu_model (ClassificationModel): Model for main menu
            app (App): Main application
        """
        super().__init__()
        self._classification_model = classification_model
        self._app = app
    

    def fill_registrations(self):
        """Fill the registration list with the registrations for the selected
        segment.
        """
        self._classification_model.construct_registration_list()

    

    @pyqtSlot(bool)
    def submit(self, menu_view):
        """Submit the form and check if the registration and directory are
        filled out correctly. If not, display an error message. If everything 
        works, then the menu window is closed and the annotation tool is 
        started.

        Args:
            menu_view (MainMenu): The main menu window/view
        """
        reg = self._classification_model.registration
        popup = QMessageBox()
        popup.setIcon(QMessageBox.Critical)
        popup.setWindowTitle('Error')
        if reg == '':   
            popup.setText('Please select a registration.')
            popup.exec_()
            return
        
        

        self._app.run_annotation_tool()   
    
    
    @pyqtSlot(str)
    def update_registration(self, reg):
        self._classification_model.registration = reg
    

class RegistrationController(QObject):
    def __init__(self, registration_model):
        """Constructor for RegistrationController

        Args:
            registration_model (RegistrationModel): Model for registration menu
        """
        super().__init__()
        self._registration_model = registration_model
    

    def fill_years(self):
        """Fill the years list with with the possible years to register for the
        selected interstate
        """
        self._registration_model.construct_years_list()
    

    def update_years_selected(self, year, checked):
        """Update the years selected list when a year is checked or unchecked.

        Args:
            year (str): The year that was checked or unchecked
            checked (bool): Whether the year was checked or unchecked
        """
        if checked:
            self._registration_model.years_selected.add(int(year))
        else:
            self._registration_model.years_selected.remove(int(year))
    

    def update_by_selected(self, by, checked):
        """Update the by selected list when a by is checked or unchecked.

        Args:
            by (str): The by that was checked or unchecked
            checked (bool): Whether the by was checked or unchecked
        """
        if checked:
            self._registration_model.by_selected = int(by)
        else:
            self._registration_model.by_selected = None
    

    @pyqtSlot(int)
    def update_faulting_mode(self, id):
        if id == 1:
            self._registration_model.faulting_mode = 'average'
        else:
            self._registration_model.faulting_mode = 'single'
    

    @pyqtSlot(bool)
    def submit(self, b):
        popup = QMessageBox()
        popup.setIcon(QMessageBox.Critical)
        popup.setWindowTitle('Error')
        if not self._registration_model.years_selected:
            popup.setText('Please select at least one year.')
            popup.exec_()
            return
        elif self._registration_model.by_selected is None:
            popup.setText('Please select a BY year.')
            popup.exec_()
            return
        
        
        self._app.run_registration_script()
    

    
