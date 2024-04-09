import os
import shutil
from file_manager.image_type import ImageType
from file_manager.files import FileManager
import xml.etree.ElementTree as ET
class CropFileManager(FileManager):
    def __init__(self, main_path, year):
        super().__init__(main_path)
        self.image_mode = None
        self.input_im_path = None
        self.output_im_path = None
        self.input_im_files = None
        self.annotation_file = None

        self.data_path = os.path.join(main_path, str(year))
        if not os.path.exists(self.data_path):
            raise ValueError("Data path does not exist.")
        self.annotation_path = os.path.join(self.data_path, "CVAT_output")
        if not os.path.exists(self.annotation_path):
            raise ValueError("CVAT annotation folder could not be found.")
        self.slab_path = os.path.join(self.data_path, "Slabs")
        if not os.path.exists(self.slab_path):
            os.mkdir(self.slab_path)  
        self.csv_path = os.path.join(self.data_path, "slabs.csv")  # Slab file
        self.txt_path = os.path.join(self.data_path, "debug.txt")  # Debug file
    
        self.join_annotations()
        self.clean_slab_folder()  # Cleaning folders; comment as necessary
    

    def join_annotations(self):
        """Joins all the XML annotation files into a single XML file. Deletes
        the individual XML files after joining them. The joined file is saved to
        the same folder

        Raises:
            ValueError: If there are no XML annotation files in the annotation
            folder
        """
        xml_files = self.filter_files(self.annotation_path, "xml")
        if not xml_files:
            raise ValueError("No XML files found in annotation path.")
        
        file_path = os.path.join(self.annotation_path, xml_files[0])
        base_tree = ET.parse(file_path)
        base_root = base_tree.getroot()
        os.remove(file_path)
        for i in range(1, len(xml_files)):
            file_path = os.path.join(self.annotation_path, xml_files[i])
            curr_root = ET.parse(file_path).getroot()
            base_root.extend(curr_root)
            os.remove(file_path)

        self.annotation_file = os.path.join(
            self.annotation_path, "annotations.xml"
            )
        base_tree.write(self.annotation_file)
            

    def clean_slab_folder(self):
        # Removing previous slab images; comment as necessary
        try:
            shutil.rmtree(self.slab_path)
        except:
            pass

        os.mkdir(self.slab_path)

    
    def switch_image_mode(self, image_mode: str):
        """Sets the input and output paths for the slabs based on the image
        mode. Also fetches the list of image files to be processed.

        Args:
            image_mode (str): The image mode to be used for the slabs
        Raises:
            ValueError: If the input image path does not exist
            ValueError: If the annotation path does not exist
        """
        if image_mode == 'intensity':
            self.image_mode = ImageType.INTENSITY
        elif image_mode == 'range':
            self.image_mode = ImageType.RANGE
        else:
            raise ValueError("Please use a valid image mode")
        self.input_im_path = os.path.join(self.data_path, 
                                          image_mode.capitalize())
        if not os.path.exists(self.annotation_path):
            raise ValueError("Annotation path does not exist.")
        if not os.path.exists(self.input_im_path):
            raise ValueError("Input image path does not exist.")
        self.output_im_path = os.path.join(self.slab_path, 
                                           ('output_' 
                                            + self.image_mode.name.lower()))
        os.mkdir(self.output_im_path)
        
        self.input_im_files = self.filter_files(self.input_im_path, "jpg")

        
        
    
   
        
        


    
