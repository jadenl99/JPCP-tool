from PyQt5.QtCore import QObject, pyqtSignal
import os
class MenuModel(QObject):
    directory_changed = pyqtSignal(str) 
    segment_id_changed = pyqtSignal(str)
    def __init__(self, slab_inventory):
        super().__init__()
        
        self._directory = ''
        self._segment_id = ''
        self._segments = slab_inventory.fetch_seg_ids()
        self._slab_inventory = slab_inventory
    

    @property
    def directory(self):
        return self._directory
    

    @directory.setter
    def directory(self, directory):
        self._directory = directory
        self.directory_changed.emit(directory)
    

    @property
    def segment_id(self):
        return self._segment_id
    

    @segment_id.setter
    def segment_id(self, segment_id):
        self._segment_id = segment_id
        self._slab_inventory.segment_id = segment_id
        self.segment_id_changed.emit(segment_id)

    


    


    



    




    