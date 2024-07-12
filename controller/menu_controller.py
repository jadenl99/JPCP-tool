from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtWidgets import QFileDialog, QMessageBox

class MenuController(QObject):
    def __init__(self, menu_model):
        """Constructor for MenuController

        Args:
            menu_model (MenuModel): Model for main menu
            app (App): Main application
        """
        super().__init__()
        self._menu_model = menu_model

    

    @pyqtSlot(bool)
    def select_directory(self, menu_view):
        dir = QFileDialog.getExistingDirectory(menu_view, 'Select Directory')
        self._menu_model.directory = dir
    

    @pyqtSlot(str)
    def update_segment(self, seg):
        self._menu_model.segment_id = seg

    
    @pyqtSlot(bool)
    def submit(self, menu_view):
        """Submit the form and check if the segment and directory are
        filled out correctly. If not, display an error message.

        Args:
            menu_view (MainMenu): The main menu window/view
        """
        dir = self._menu_model.directory
        seg = self._menu_model.segment_id
        popup = QMessageBox()
        popup.setIcon(QMessageBox.Critical)
        popup.setWindowTitle('Error')
        if dir == '':
            popup.setText('Please select a directory.')
            popup.exec_()
            return

        if seg == '':   
            popup.setText('Please select a segment.')
            popup.exec_()
            return
        
        # enable the menu buttons to navigate to widgets
        for action in menu_view.stage_menu.actions():
            action.setEnabled(True)
        
        menu_view.submit_btn.setEnabled(False)  
        menu_view.dir_select_btn.setEnabled(False)
        menu_view.seg_selector.setEnabled(False)

        menu_view._classification_view._classification_controller.fill_registrations()
        menu_view._registration_view._registration_controller.fill_years()
        

