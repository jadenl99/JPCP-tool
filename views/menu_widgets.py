import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QAction, 
                             QMenu, QFileDialog, QPushButton, QWidget, QLabel,
                             QWidget, QComboBox, QCheckBox, QRadioButton,
                             QButtonGroup, QAbstractButton)
from PyQt5.QtGui import QPalette, QColor
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.uic import loadUi


class ClassificationMenu(QWidget):
    def __init__(self, classification_controller, classification_model):
        super().__init__()
        self._classification_controller = classification_controller
        self._classification_model = classification_model
        loadUi('resources/classification_menu.ui', self)
        self.setWindowTitle('Classification Menu')

    
        self.populate_reg_selector()

  
        self.submit_btn.clicked.connect(
            lambda: self._classification_controller.submit(self)  
        )

        self._classification_model.registrations_changed.connect(
            lambda: self.populate_reg_selector()
        )

        # detect when views update
        self.reg_selector.currentIndexChanged.connect(
            lambda: self._classification_controller.update_registration(
                self.reg_selector.currentText()
            )
        )   


    def populate_reg_selector(self):
        """Populates the registration selector with the registrations from the
        database.
        """
        self.reg_selector.clear()
        self.reg_selector.addItem('')
        reg_list = list(self._classification_model.registrations.keys())
        reg_list.sort()
        for reg in reg_list:
            self.reg_selector.addItem(reg)
    

class RegistrationMenu(QWidget):
    def __init__(self, registration_controller, registration_model):
        """Constructor for RegistrationMenu

        Args:
            registration_controller (RegistrationController): the controller for
            the registration menu
            registration_model (RegistrationModel): the model for the
            registration menu
        """
        super().__init__()
        self._registration_controller = registration_controller
        self._registration_model = registration_model
        loadUi('resources/registration_menu.ui', self)
        self.setWindowTitle('Registration Menu')
        self.year_btn_group = QButtonGroup()
        self.year_btn_group.setExclusive(False)
        self.by_btn_group = QButtonGroup()
        self.by_btn_group.setExclusive(False)
        self.faulting_btn_group = QButtonGroup()
        self.faulting_btn_group.addButton(self.avg_btn, 1)
        self.faulting_btn_group.addButton(self.most_btn, 2) 
        self.by_select.setLayout(QVBoxLayout())   
        self.year_select.setLayout(QVBoxLayout())
    
        
        self._registration_model.years_changed.connect(
            self.populate_years_selector    
        )

        self.year_btn_group.buttonClicked.connect(self.on_year_selected)
        self.by_btn_group.buttonClicked.connect(self.on_by_selected)
        self.faulting_btn_group.buttonClicked.connect(
            self.on_faulting_selected
        )
        self.submit_btn.clicked.connect(
            self._registration_controller.submit
        )   



    
    @pyqtSlot(list)
    def populate_years_selector(self, years):
        """Populates the year selector with the years from the database.
        """
        year_select_layout = self.year_select.layout()
        by_select_layout = self.by_select.layout()
        for i, year in enumerate(years):
            year_checkbox = QCheckBox(str(year))
            year_radio_btn = QRadioButton(str(year))
            year_radio_btn.setEnabled(False)

            year_select_layout.addWidget(year_checkbox)
            by_select_layout.addWidget(year_radio_btn)
            self.year_btn_group.addButton(year_checkbox, i + 1)
            self.by_btn_group.addButton(year_radio_btn, i + 1)
    

    @pyqtSlot(QAbstractButton)
    def on_year_selected(self, btn):
        """Update the year selected and enforce selection options for BY
        """
        btn_id = self.year_btn_group.id(btn)
        self._registration_controller.update_years_selected(
            btn.text(), btn.isChecked()
        )

        by_btn = self.by_btn_group.button(btn_id)

        if btn.isChecked():
            by_btn.setEnabled(True)
        
        else:
            if by_btn.isChecked():
                self._registration_controller.update_by_selected(
                    by_btn.text(), False
                    )
            by_btn.setChecked(False)
            by_btn.setEnabled(False)
            
    
    @pyqtSlot(QAbstractButton)
    def on_by_selected(self, btn):
        """Update the BY selected
        """
        self._registration_controller.update_by_selected(
            btn.text(), btn.isChecked()
            )
        
        if btn.isChecked():
            for curr_btn in self.by_btn_group.buttons():
                if curr_btn != btn:
                    curr_btn.setChecked(False)
    

    @pyqtSlot(QAbstractButton)
    def on_faulting_selected(self, btn):
        """Update the faulting mode selected
        """
        self._registration_controller.update_faulting_mode(
            self.faulting_btn_group.id(btn)
        )


    

        


        
        

