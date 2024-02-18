from bs4 import BeautifulSoup
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
class XML_CVAT_Parser:
    def __init__(self, data_dir, px_height, px_width, 
                 mm_height, mm_width, mode):
        self.data_dir = data_dir  
        self.xml_dir = os.path.join(data_dir, "XML")
        self.xml_files = os.listdir(self.xml_dir)
        self.output_dir = os.path.join(data_dir, "CVAT_data")
        self.id = 0
        self.px_height = px_height
        self.scale_factor_y = float(px_height) / mm_height
        self.scale_factor_x = float(px_width) / mm_width
        self.mode = mode
        self.clean_folder(self.output_dir)

        self.parse()
            
    

    def clean_folder(self, dir):
        """Cleans everything in the directory specified. 

        Args:
            dir (str): path of the folder to clean out
        """
        try:
            shutil.rmtree(dir)
        except:
            pass
        os.mkdir(dir)


    def parse(self):
        """Looks through the XML files produced by the crack digitizer and
        converts the data to a format that can be read by CVAT.
        """
        # Top level element#####################################################
        annotations = ET.Element('annotations')
        ########################################################################
        for xml_file in self.xml_files:
            with open(os.path.join(self.xml_dir, xml_file), "r") as f:
                # Image element#################################################
                image = ET.SubElement(annotations, 'image', 
                                      id=str(self.id), 
                                      name=self.image_name(xml_file))
                ################################################################
                xml = f.read()
                soup = BeautifulSoup(xml, 'xml')
                subjoints_data = soup.find_all('Joint')
                for subjoint in subjoints_data:
                    x1 = float(subjoint.find('X1').get_text())
                    y1 = float(subjoint.find('Y1').get_text())
                    x2 = float(subjoint.find('X2').get_text())
                    y2 = float(subjoint.find('Y2').get_text())
                    x1 = self.convert_val_x(x1)
                    x2 = self.convert_val_x(x2)
                    y1 = self.convert_val_y(y1)
                    y2 = self.convert_val_y(y2)
                    # Subjoint polyline element#################################
                    subjoint = ET.SubElement(image, 'polyline', 
                                            label='subjoint',
                                            occluded='0',
                                            points=f'{x1},{y1};{x2},{y2}',
                                            z_order='0')
                    ############################################################
                
                lanemarkers_data = soup.find_all('LaneMark')
                for lanemarker in lanemarkers_data:
                    x = float(lanemarker.find('Position').get_text())
                    x = self.convert_val_x(x)
                    # Lanemarker point element##################################
                    lanemarker = ET.SubElement(image, 'polyline', 
                                               label='lane_marker',
                                               occluded='0',
                                               points=f'{x},{self.px_height};{x},0',
                                               z_order='0')
                    ############################################################
            self.id += 1
        tree = ET.ElementTree(annotations)
        ET.indent(tree, space='\t', level=0)
        tree.write(os.path.join(self.output_dir, 'annotations.xml'),
                   encoding='utf-8', 
                   xml_declaration=True)   
            
                



    def image_name(self, xml_file):
        """Gets the name of the image from the XML file

        Args:
            xml_file (str): name of the XML file

        Returns:
            str: name of the image
        """
        s = 'LcmsResult_Image'
        if self.mode == 'range':
            s += 'Rng_'
        else:
            s += 'Int_'

        return s + str(self.get_im_id(xml_file)) + '.jpg'
            




    def get_im_id(self, s):

        # From util file; retrieves image by ID
        s = s[::-1]
        start_index = -1
        end_index = -1
        for i, c in enumerate(s):
            if c.isdigit():
                end_index = i + 1
                if start_index == -1:
                    start_index = i
            elif start_index > -1:
                break
        if start_index == -1:
            return None

        return int(s[start_index:end_index][::-1])
    

    def convert_val_y(self, val):
        """Converts the value from millimeters to pixels in y. Additional
        measures have to be taken to ensure that (0, 0) is at the top left, 
        since the crack digitizer references (0, 0) at the bottom left.

        Args:
            val (int): value in millimeters

        Returns:
            int: value in pixels
        """
        return round(self.px_height - val * self.scale_factor_y, 2)
    

    def convert_val_x(self, val):
        """Converts the value from millimeters to pixels in x

        Args:
            val (int): value in millimeters

        Returns:
            int: value in pixels
        """
        return round(val * self.scale_factor_x, 2)
    

    def zip_folder(self, output, folder):
        """Zips the folder of interest

        Args:
            output (_type_): _description_
            folder (_type_): _description_
        """
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for foldername, subfolders, filenames in os.walk(folder):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, folder)
                    zip_file.write(file_path, arcname)

    
    
                

    
