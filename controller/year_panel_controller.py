from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image


import cv2
import os
class YearPanelController(QObject):
    def __init__(self, year_panel_model):
        super().__init__()
        self._year_panel_model = year_panel_model

    
    @pyqtSlot(bool)
    def increment_slab(self, next=True):
        """Updates the displayed slab image to the next slab in the slab ID list

        Args:
            next (bool): if True, increments the slab index. Else, decrements 
            thw slab index.
        """
        model = self._year_panel_model
        if next:
            model.slab_id_list_index += 1  
        else:
            model.slab_id_list_index -= 1
        self._year_panel_model.image_signal.image_changed.emit(
            self._year_panel_model.img_directory)
        self._year_panel_model.refresh_CY_slab_info()


    @pyqtSlot(bool)
    def popup_original_image(self):
        """Opens a dialog box to display the original image of the slab
        """
        try:
            img = self.get_slab_image(convertToQtImage=False)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(img_rgb)
            image.show()
        except:
            pass

    
    @pyqtSlot(list)
    def change_slab_state_info(self, states_pressed):
        """Changes the state of the slab based on the button pressed by the user
        in the model

        Args:
            states_pressed (list[str]): list of states pressed by the
            user, denoting the primary and secondary states of the slab. 
            list[0] is the primary state and list[1] is the secondary state.
        """
        primary_state_list = self._year_panel_model.primary_states
        secondary_state_list = self._year_panel_model.secondary_states
        slab_index = self._year_panel_model.slab_id_list_index

        
        primary_state_list[slab_index] = states_pressed[0]
        secondary_state_list[slab_index] = states_pressed[1]
        self._year_panel_model.panel_updated = True
    

    @pyqtSlot(bool)
    def change_sealed_info(self, is_sealed):
        """Changes the replaced state of the slab in the model

        Args:
            is_replaced (bool): whether the slab is replaced or not
        """
        index = self._year_panel_model.slab_id_list_index
        self._year_panel_model.sealed[index] = is_sealed
        self._year_panel_model.panel_updated = True

    
    @pyqtSlot(bool)
    def change_failed_spall_info(self, is_failed_spall):
        """Changes the replaced state of the slab in the model

        Args:
            is_replaced (bool): whether the slab is replaced or not
        """
        index = self._year_panel_model.slab_id_list_index
        self._year_panel_model.failed_spall[index] = is_failed_spall
        self._year_panel_model.panel_updated = True
        

    @pyqtSlot(bool)
    def change_joint_spall_info(self, is_joint_spall):
        """Changes the replaced state of the slab in the model

        Args:
            is_replaced (bool): whether the slab is replaced or not
        """
        index = self._year_panel_model.slab_id_list_index
        self._year_panel_model.joint_spall[index] = is_joint_spall
        self._year_panel_model.panel_updated = True
    

    @pyqtSlot(bool)
    def change_patched_spall_info(self, is_patched_spall):
        """Changes the replaced state of the slab in the model

        Args:
            is_patched_spall (bool): whether the slab has spall or not
        """
        index = self._year_panel_model.slab_id_list_index
        self._year_panel_model.patched_spall[index] = is_patched_spall
        self._year_panel_model.panel_updated = True


    @pyqtSlot(bool)
    def change_replaced_intensity_info(self, is_replaced):
        """Changes the replaced state of the slab in the model

        Args:
            is_replaced (bool): whether the slab is replaced or not
        """
        pass
        
        index = self._year_panel_model.slab_id_list_index
        if is_replaced:
            self._year_panel_model.intensity_replaced[index] = 'R'
        else:
            self._year_panel_model.intensity_replaced[index] = None
        self._year_panel_model.panel_updated = True
    

    @pyqtSlot(bool)
    def change_replaced_info(self, is_replaced):
        """Changes the replaced state of the slab in the model

        Args:
            is_replaced (bool): whether the slab is replaced or not
        """
        index = self._year_panel_model.slab_id_list_index
        if is_replaced:
            self._year_panel_model.replaced[index] = 'R'
        else:
            self._year_panel_model.replaced[index] = None
        self._year_panel_model.panel_updated = True


    @pyqtSlot(str)
    def change_comments(self, comments):
        """Changes the comments of the slab in the model

        Args:
            comments (str): the comments to add to the slab
        """
        index = self._year_panel_model.slab_id_list_index
        self._year_panel_model.panel_updated = True
        self._year_panel_model.slabs_info['comments'][index] = comments.strip()
        


    def get_slab_image(self, convertToQtImage=True):
        """Returns the image of the slab

        Args:
            convertToQtImage (bool, optional): if True, converts the image to a
            QPixmap. Defaults to True.
        Returns:
            QPixmap or np.arrray: the image of the slab
        """
        img_dir = self._year_panel_model.img_directory
        slab_index = self._year_panel_model.slab_id_list[
            self._year_panel_model.slab_id_list_index]
        img = None
        if img_dir == '':
            raise Exception('No slab image for the year')
        
        if 'Range' in img_dir or 'Intensity' in img_dir:
            bottom_im = self._year_panel_model.slabs_info['start_im'][
                self._year_panel_model.slab_id_list_index
            ]
            top_im = self._year_panel_model.slabs_info['end_im'][
                self._year_panel_model.slab_id_list_index
            ]
            img = self.concat_images(bottom_im, top_im)
        else: 
            img_path = os.path.join(img_dir, f'{slab_index}.jpg')
            if not os.path.exists(img_path):
                img_path = os.path.join(img_dir, f'{slab_index}.png')
            if not os.path.exists(img_path):
                raise Exception(f'Slab Image Not Found')
            img = cv2.imread(img_path)
        if convertToQtImage:
            return self.convertCvImage2QtImage(img)
       
        #return cv2.imread(img_path)    
        return img

    def concat_images(self, id1, id2):
        """Concatenates two images vertically

        Args:
            id1 (int): the bottommost image id
            img2 (int): the topmost image id
        Raises:
            Exception: if the start image id is greater than the end image id
            Exception: if there is no slab image for the year
        """
        if id1 > id2:
            raise Exception('start Im greater than end Im')
        if not id1 or not id2:
            raise Exception('No slab image for the year')
        img_dir = self._year_panel_model.img_directory
        imgs = []
        for i in range(id1, id2 + 1):
            im_path = None
            if 'Range' in img_dir:
                im_path = os.path.join(
                    img_dir, f'LcmsResult_ImageRng_{i:06}.jpg'
                    )
            else:
                im_path = os.path.join(
                    img_dir, f'LcmsResult_ImageInt_{i:06}.jpg'
                    )
            if not os.path.exists(im_path):
                raise Exception('Slab Image Not Found')
            imgs.append(cv2.imread(im_path))
        return cv2.vconcat(imgs[::-1])

        
    def convertCvImage2QtImage(self, image):
        """Converts a cv2 image to a QPixmap

        Args:
            image (np.array): the image to convert

        Returns:
            QPixmap: the converted image
        """
        image = QImage(image, image.shape[1],\
                            image.shape[0], image.shape[1] * 3, 
                            QImage.Format_RGB888)
        pix = QPixmap(image)
        return pix




    
        