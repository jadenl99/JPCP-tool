import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QHBoxLayout, 
                             QAbstractButton, QStyle, QWidget)
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.uic import loadUi

class AnnotationTool(QMainWindow):
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1" 
    def __init__(self, tool_controller, tool_model, year_panels):
        """Constructor for the main annotation tool window

        Args:
            tool_controller (ToolController): Controller for tool window
            tool_model (ToolModel): Model for tool window
            year_panels (dict[int, YearPanel]): Dictionary of year panels for
            each registration year
        """
        super().__init__()
        self._tool_controller = tool_controller
        self._tool_model = tool_model
        self._year_panels = year_panels
        loadUi('resources/mainapp.ui', self)
        self.setWindowTitle('JPCP Annotation Tool')
        self.secondary_icon = self.style().standardIcon(
            QStyle.SP_DialogYesButton
            ) 
        years_layout = QHBoxLayout()
        years_layout.setSpacing(0)
        sorted_year_panels = sorted(year_panels.items())
        for panel in sorted_year_panels:
            panel[1].state_btn_group.buttonClicked.connect(
                self.on_state_changed
                )
            panel[1].replaced_box.clicked.connect(
                lambda: self.on_replaced_changed()
            )
            years_layout.addWidget(panel[1])
        self.scroll_year_contents.setLayout(years_layout)
        
        # Set up the slab form validator
        slab_form_validator = QIntValidator()
        self.slab_form.setValidator(slab_form_validator)
        # textChanged
        self.slab_form.returnPressed.connect(
            lambda: self._tool_controller.update_slabs_displayed(
                self.slab_form.text(),
                self.slab_form))
        
        # back and next buttons setup
        self.back_btn.clicked.connect(
            lambda: self._tool_controller.update_slabs_displayed(
                str(int(self.slab_form.text()) - 1),
                self.slab_form))
        self.next_btn.clicked.connect(
            lambda: self._tool_controller.update_slabs_displayed(
                str(int(self.slab_form.text()) + 1),
                self.slab_form)
        )
        
        # replaced year and type setup
        self._tool_model.replaced_year_changed.connect(
            self.on_replaced_year_changed
        )
        self._tool_model.replaced_type_changed.connect( 
            self.on_alignment_changed
        )
        
        # menu bar actions
        self.action_range.triggered.connect(
            lambda: self._tool_controller.update_image_type('output_range')
        )
        self.action_intensity.triggered.connect(
            lambda: self._tool_controller.update_image_type('output_intensity')
        )
        self.action_uncropped_range.triggered.connect(
            lambda: self._tool_controller.update_image_type('Range')
        )
        self.action_uncropped_intensity.triggered.connect(
            lambda: self._tool_controller.update_image_type('Intensity')
        )
        self.action_range.setShortcut('Ctrl+R')
        self.action_intensity.setShortcut('Ctrl+I')
        self.action_uncropped_range.setShortcut('Ctrl+Shift+R')
        self.action_uncropped_intensity.setShortcut('Ctrl+Shift+I')

        
        
        # set up labels
        self.slab_form.setText(str(self._tool_model.first_BY_index))    
        self.num_lbl.setText("/"+ str(self._tool_model.last_BY_index))
        self.populate_year_buttons()

        # radiate a signal to display the first slabs
        self._tool_controller.update_slabs_displayed(
            str(self._tool_model.first_BY_index),
            self.slab_form)

    
    def populate_year_buttons(self):
        """Populates the text of the year buttons in the main annotation tool
        """
        for year, year_panel in self._year_panels.items():
            year_panel.yr_label.setText(str(year))  

    
    @pyqtSlot(QAbstractButton)
    def on_state_changed(self, button):
        """Slot for when any state button is clicked. Supports shift click 
        functionality, where all buttons of the same state from the year 
        the button was clicked onward are updated (if able to be updated). 
        Ensures that only two (or less) buttons are checked at a time.

        Args:
            button (QPushButton): button that is pushed by the user
        """
        modifiers = QApplication.keyboardModifiers()
    
        sorted_year_panels = sorted(self._year_panels.items())  
        btn_id = None
        pressed_yr = None
        for year, year_panel in sorted_year_panels:
            btn_id = year_panel.state_btn_group.id(button) 
            if btn_id != -1:
                pressed_yr = year
                break
        

        pressed_state = None
        for year, year_panel in sorted_year_panels:
            if year == pressed_yr or (year > pressed_yr 
                                      and modifiers == QtCore.Qt.ShiftModifier
                                      and not 
                                      year_panel._year_panel_model.lock_panel):
                curr_btn_group = year_panel.state_btn_group
                curr_btn = curr_btn_group.button(btn_id)
                if year > pressed_yr:
                    curr_btn.setChecked(pressed_state)
                
                # enforce only buttons checked at a time
                checked_states = self.button_selection(curr_btn_group, curr_btn)

                # change borders based if there is any checked button
                if checked_states[0] is None:
                    year_panel.slab_img.setStyleSheet('border: 3px solid red;')
                else:
                    year_panel.slab_img.setStyleSheet('border: 3px solid green;')

                # send to controller
                year_panel._year_panel_controller.change_slab_state_info(
                    checked_states
                    )
                if year == pressed_yr:
                    pressed_state = curr_btn.isChecked()
        

    @pyqtSlot(bool)
    def on_replaced_changed(self):
        checkbox = self.sender()
        modifer = QApplication.keyboardModifiers()
        sorted_year_panels = sorted(self._year_panels.items())
        pressed_yr = None
        for year, year_panel in sorted_year_panels:
            if year_panel.replaced_box == checkbox:
                
                pressed_yr = year
                break
        
        
        is_checked = checkbox.isChecked()
        for year, year_panel in sorted_year_panels:
            if year == pressed_yr or (year > pressed_yr 
                                      and modifer == QtCore.Qt.ShiftModifier
                                      and not 
                                      year_panel._year_panel_model.lock_panel):
                year_panel.replaced_box.setChecked(is_checked)  
                year_panel._year_panel_controller.change_replaced_info(
                    is_checked
                )
                


    
    def button_selection(self, btn_group, curr_btn):
        """Given the button group and the current button, updates the button
        group display and ensures only two buttons are checked at a time. If the
        newly selected button is the second button, the secondary state is the
        text of that selected button. If there are already two buttons selected,
        then the button toggle is ignored. 

        Args:
            btn_group (QButtonGroup): button group to update
            curr_btn (QPushButton): button clicked by the user

        Returns:
            list[str]: list of buttons checked in the button group after
            the two button check has been done. For buttons checked, 
            list[0] is the primary state and list[1] is the secondary 
            state
        """

        checked_btns = [button for button in btn_group.buttons() 
                        if button.isChecked()]

        if len(checked_btns) > 2:
            curr_btn.setChecked(False)
            checked_btns.remove(curr_btn)
        elif len(checked_btns) == 2 and curr_btn.isChecked():
            curr_btn.setIcon(self.secondary_icon)
        elif len(checked_btns) == 2 and not curr_btn.isChecked():
            curr_btn.setIcon(QIcon())
        elif len(checked_btns) == 1:
            curr_btn.setIcon(QIcon())
            checked_btns[0].setIcon(QIcon())
        
        # Ensure that the primary state is always the first button checked
        if (len(checked_btns) == 2 and 
            checked_btns[0].icon().cacheKey() 
            == self.secondary_icon.cacheKey()):
            checked_btns[0], checked_btns[1] = checked_btns[1], checked_btns[0]

        checked_btns = [button.text() for button in checked_btns]

        # append None if there are less than 2 buttons checked
        if len(checked_btns) < 2:
            checked_btns.append(None)
        if len(checked_btns) < 2:
            checked_btns.append(None)

        return checked_btns


    @pyqtSlot(int)
    def on_replaced_year_changed(self, year):
        """Slot for when the detected replacent year is changed.

        Args:
            year (int): year a replacement was detected
        """
        
        if 1 <= year <= 3000:
            self.replaced_yr_lbl.setText(f'Replaced Year: {year}')  
            self.replaced_yr_lbl.setStyleSheet('border: 3px solid red;')
            self.align_lbl.setStyleSheet('border: 3px solid red;')
        else:
            self.replaced_yr_lbl.setText('Replaced Year: N/A')
            self.replaced_yr_lbl.setStyleSheet('')
            self.align_lbl.setStyleSheet('')
        

    @pyqtSlot(str)
    def on_alignment_changed(self, alignment):
        """Slot for when the alignment is changed.

        Args:
            alignment (str): alignment of the slab
        """
        
        self.align_lbl.setText(f'Misalignment Type: {alignment}')
    