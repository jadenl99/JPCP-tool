import sys, os
from PyQt5.QtWidgets import QWidget, QButtonGroup, QAbstractButton, QStyle, QApplication

from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QIcon
class YearPanel(QWidget):
    def __init__(self, year_panel_controller, year_panel_model):    
        super().__init__()
        self._year_panel_controller = year_panel_controller
        self._year_panel_model = year_panel_model
        self.secondary_icon = self.style().standardIcon(
            QStyle.SP_DialogYesButton
            ) 
        loadUi('resources/year_panel.ui', self)
        # Set up buttons so slab states can be annotated
        self.state_btn_group = QButtonGroup()   
        self.state_btn_group.setExclusive(False)
        self.state_btn_group.addButton(self.l1_btn)
        self.state_btn_group.addButton(self.l2_btn)
        self.state_btn_group.addButton(self.t1_btn)
        self.state_btn_group.addButton(self.t2_btn)
        self.state_btn_group.addButton(self.cc_btn)
        self.state_btn_group.addButton(self.ss_btn)
        self.state_btn_group.addButton(self.nc_btn)
        self.state_btn_group.addButton(self.error_btn)

        self.vertical_panel_layout.setAlignment(Qt.AlignCenter)
        # listen to updates from model
        self._year_panel_model.image_signal.image_changed.connect(
            self.on_BY_slab_changed
        )
        self._year_panel_model.lock_panel_signal.lock_panel.connect(
            self.on_lock_panel_changed
        )

        self._year_panel_model.next_btn_enable_signal.next_btn_enable.connect(
            self.on_next_btn_enable
        )

        self._year_panel_model.back_btn_enable_signal.back_btn_enable.connect(
            self.on_back_btn_enable
        )
        self._year_panel_model.state_changed_signal.state_changed.connect(
            self.on_state_menu_changed
        )
        
        self.next_btn.clicked.connect(
            lambda: self._year_panel_controller.increment_slab(next=True)
        )
        self.back_btn.clicked.connect(
            lambda: self._year_panel_controller.increment_slab(next=False)
        )
        
        self.yr_label.clicked.connect(
            self._year_panel_controller.popup_original_image
        )

        
    @pyqtSlot(str)
    def on_BY_slab_changed(self, slab_dir):
        try:
            img = self._year_panel_controller.get_slab_image()
            img = img.scaled(330, 500, 1, 0)
            self.slab_img.setPixmap(img)
        except Exception as e:
            self.slab_img.setText(str(e))
            

    @pyqtSlot(bool)
    def on_lock_panel_changed(self, lock):
        """If the lock is on, the panel is disabled. If the lock is off, the
        panel is enabled.

        Args:
            lock (bool): Whether to lock the panel or unlock it. If True, locks
            the panel.
        """
        self.back_btn.setEnabled(not lock)  
        self.next_btn.setEnabled(not lock)
        self.replaced_box.setEnabled(not lock)  
        self.faulting_lbl.setText('Average Faulting: N/A')
        self.length_lbl.setText('Length: N/A')
        self.width_lbl.setText('Width: N/A')
        self.cy_index_lbl.setText('CY Index: N/A')  

        for btn in self.state_btn_group.buttons():
            if lock:
                btn.setChecked(False)
                btn.setIcon(QIcon())
            btn.setEnabled(not lock)
    

    @pyqtSlot(bool)
    def on_next_btn_enable(self, enable):
        """Sets the next button to be enabled or disabled

        Args:
            enable (bool): if enable is True, sets the next button to be 
            enabled. Else, sets the next button to be disabled.
        """
        self.next_btn.setEnabled(enable)
    

    @pyqtSlot(bool)
    def on_back_btn_enable(self, enable):
        """Sets the back button to be enabled or disabled

        Args:
            enable (bool): if enable is True, sets the back button to be 
            enabled. Else, sets the back button to be disabled.
        """
        self.back_btn.setEnabled(enable)
        

    @pyqtSlot(tuple)
    def on_state_menu_changed(self, state_tuple):
        """Updates the state of the slab based on the state tuple provided and 
        also updates slab information such as length, width, and average
        faulting.

        Args:
            state_tuple (tuple[str, str, str, float, float, float, int, int, 
            int]): tuple containing the primary state, secondary state, special 
            state, length, width, average faulting of slab, CY index, start im, 
            end im
        """
        primary_state, secondary_state, special_state, length, width, \
        avg_faulting, cy_index, start_im, end_im = state_tuple

        for btn in self.state_btn_group.buttons():
            btn.setIcon(QIcon())
            if primary_state and btn.text() == primary_state:
                btn.setChecked(True)
            elif secondary_state and btn.text() == secondary_state:
                btn.setChecked(True)
                btn.setIcon(self.secondary_icon)
            else:
                btn.setChecked(False)
            
        if special_state == 'R':
            self.replaced_box.setChecked(True)
        else:
            self.replaced_box.setChecked(False)
        
        
        faulting_txt = f'Average Faulting: {avg_faulting:.2f}' if avg_faulting \
            else 'Average Faulting: N/A'
        length_txt = f'Length: {length:.2f} ft.' if length else 'Length: N/A'
        width_txt = f'Width: {width:.2f} ft.' if width else 'Width: N/A'

        if primary_state is None:
            self.slab_img.setStyleSheet('border: 3px solid red;')
        else:
            self.slab_img.setStyleSheet('border: 3px solid green;')
        self.length_lbl.setText(length_txt)
        self.width_lbl.setText(width_txt)
        self.faulting_lbl.setText(faulting_txt)
        self.cy_index_lbl.setText(f'CY Index: {cy_index}')   
        self.start_im_lbl.setText(f'Start Image: {start_im}')
        self.end_im_lbl.setText(f'End Image: {end_im}')