import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QAction, 
                             QMenu, QFileDialog, QPushButton, QWidget, QLabel,
                             QWidget, QComboBox)
from PyQt5.QtGui import QPalette, QColor
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.uic import loadUi

class MainMenu(QMainWindow):
    def __init__(self, menu_controller, menu_model, classification_view,
                 registration_view):
        super().__init__()
        self._menu_controller = menu_controller
        self._menu_model = menu_model
        self._classification_view = classification_view 
        self._registration_view = registration_view
        loadUi('resources/menu.ui', self)
        self.setWindowTitle('Main Menu')

        # listen to changes from model
        self._menu_model.directory_changed.connect(self.on_directory_changed)

        self.seg_selector.currentIndexChanged.connect(self.on_seg_changed)
        self.dir_select_btn.clicked.connect(
            lambda: self._menu_controller.select_directory(self))

        self.submit_btn.clicked.connect(
            lambda: self._menu_controller.submit(self)
        )

        # connect the menu buttons to the widgets
        self.stacked_widget.addWidget(QWidget())
        self.stacked_widget.addWidget(QWidget())
        self.stacked_widget.addWidget(self._registration_view)
        self.stacked_widget.addWidget(self._classification_view)    
        self.action_reg.triggered.connect(
            lambda: self.stacked_widget.setCurrentIndex(3)
        )
        self.action_class.triggered.connect(
            lambda: self.stacked_widget.setCurrentIndex(4)
        )
        self.populate_seg_selector()
        
        
        
    

    def populate_seg_selector(self):
        """Populates the registration selector with the registrations from the
        database.
        """
        self.seg_selector.addItem('')
        seg_id_list = self._menu_model._segments
        seg_id_list.sort()
        for seg in seg_id_list:
            self.seg_selector.addItem(seg)
    

    @pyqtSlot(str)
    def on_directory_changed(self, directory):
        self.dir_lbl.setText(f'Directory: {directory}')   
    

    @pyqtSlot(int)
    def on_seg_changed(self, index):
        self._menu_controller.update_segment(
            self.seg_selector.currentText()
        )   



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    app.exec()


