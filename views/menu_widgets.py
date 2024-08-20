import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QAction, 
                             QMenu, QFileDialog, QPushButton, QWidget, QLabel,
                             QWidget, QComboBox, QCheckBox, QRadioButton,
                             QButtonGroup, QAbstractButton, QLineEdit)
from PyQt5.QtGui import QPalette, QColor, QIntValidator, QDoubleValidator
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
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
        self.id_text_edits = {}
        loadUi('resources/registration_menu.ui', self)
        self.setWindowTitle('Registration Menu')
        self.reg_progress.setVisible(False)
        self.year_btn_group = QButtonGroup()
        self.year_btn_group.setExclusive(False)
        self.by_btn_group = QButtonGroup()
        self.by_btn_group.setExclusive(False)
        self.faulting_btn_group = QButtonGroup()
        self.faulting_btn_group.addButton(self.avg_btn, 1)
        self.faulting_btn_group.addButton(self.most_btn, 2) 


        self.replaced_btn_group = QButtonGroup()
        self.replaced_btn_group.addButton(self.auto_check, 1)
        self.replaced_btn_group.addButton(self.intensity_check, 2)
        self.replaced_btn_group.setExclusive(False)

        self.by_select.setLayout(QVBoxLayout())   
        self.year_select.setLayout(QVBoxLayout())
        self.id_select.setLayout(QVBoxLayout()) 
        validate_ratio = QDoubleValidator()
        #validate_ratio.setRange(0.01, 1, 2)
        self.ratio_line_edit.setValidator(validate_ratio)
        self.ratio_line_edit.editingFinished.connect(self.on_ratio_edited)

        self._registration_model.years_changed.connect(
            self.populate_years_selector    
        )

        self.year_btn_group.buttonClicked.connect(self.on_year_selected)
        self.by_btn_group.buttonClicked.connect(self.on_by_selected)
        self.faulting_btn_group.buttonClicked.connect(
            self.on_faulting_selected
        )

        self.replaced_btn_group.buttonClicked.connect(
            self.on_replaced_selected
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
        id_select_layout = self.id_select.layout()
        self._id_text_edits = {}  
          
        for i, year in enumerate(years):
            year_checkbox = QCheckBox(str(year))
            year_radio_btn = QRadioButton(str(year))
            id_text_edit = QLineEdit()
            id_text_edit.setEnabled(False)
            id_text_edit.setPlaceholderText('Start ID')
            id_text_edit.setValidator(QIntValidator())
            id_text_edit.editingFinished.connect(self.on_id_text_edited)
            year_radio_btn.setEnabled(False)

            year_select_layout.addWidget(year_checkbox)
            id_select_layout.addWidget(id_text_edit)
            by_select_layout.addWidget(year_radio_btn)
            self.year_btn_group.addButton(year_checkbox, i + 1)
            self.id_text_edits[i + 1] = {'year': year, 'text_edit': id_text_edit}
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
            self.id_text_edits[btn_id]['text_edit'].setEnabled(True)
        
        else:
            if by_btn.isChecked():
                self._registration_controller.update_by_selected(
                    by_btn.text(), False
                    )
            self.id_text_edits[btn_id]['text_edit'].setEnabled(False)
            self.id_text_edits[btn_id]['text_edit'].clear()
            by_btn.setChecked(False)
            by_btn.setEnabled(False)
            
    
    def on_ratio_edited(self):
        """Update the ratio when the user edits it
        """
        if (self.ratio_line_edit.text() == '' 
            or self.ratio_line_edit.text() == '.'
            or float(self.ratio_line_edit.text()) > 1
            ):
            self.ratio_line_edit.setText('0.5')
        self._registration_controller.update_ratio(
            self.ratio_line_edit.text()
        )

        
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


    def on_replaced_selected(self, btn):   
        """Update the replaced annotations to use
        """
        self._registration_controller.update_replaced(
            self.replaced_btn_group.id(btn)
        )



    def on_id_text_edited(self):
        """Update the starting ID for a particular year
        """
        text_edit = self.sender()   
        for data in self.id_text_edits.values():
            if data['text_edit'] == text_edit:
                self._registration_controller.update_starting_id(
                    data['year'], text_edit.text()
                )
                break
    
    @pyqtSlot()
    def update_progress(self, value):
        """Update the progress bar
        """
        self.reg_progress.setValue(value)
        


        
        

