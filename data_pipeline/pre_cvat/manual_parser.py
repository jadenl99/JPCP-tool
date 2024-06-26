from bs4 import BeautifulSoup
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
from tqdm import tqdm
from datetime import datetime
class ManualXML_CVAT_Parser:
    def __init__(self, data_dir, px_height, px_width, 
                 mm_height, mm_width, mode, task_size,
                 begin_MM, end_MM, year, interstate):
        self.data_dir = os.path.join(data_dir, str(year))  
        self.xml_dir = os.path.join(self.data_dir, "ManualXML")
        self.xml_files = os.listdir(self.xml_dir)
        self.img_dir = os.path.join(self.data_dir, mode.capitalize())
        self.output_dir = os.path.join(self.data_dir, "CVAT_data")
        self.id = 0
        self.px_height = px_height
        self.scale_factor_y = float(px_height) / mm_height
        self.scale_factor_x = float(px_width) / mm_width
        self.mode = mode
        self.task_size = task_size
        self.clean_folder(self.output_dir)
        self.year = year
    
        # Create database name based off the name of interstate
        interstate = interstate.replace('-', '')
        
      
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
        annotations = None
        task_dir = ''
        output_img_dir = ''
        for xml_file in tqdm(self.xml_files):
            if self.id != 0 and self.id % self.task_size == 0:
                self.create_task_zip(annotations, task_dir)
    
            if self.id % self.task_size == 0:
                # Top level element#############################################
                annotations = ET.Element('annotations')
                ################################################################
                task_num = self.id // self.task_size
                task_dir = os.path.join(self.output_dir, f'task_{task_num}')
                os.mkdir(task_dir)
                output_img_dir = os.path.join(task_dir, 'images')
                os.mkdir(output_img_dir)

            img_name = self.image_name(xml_file)
            with open(os.path.join(self.xml_dir, xml_file), "r") as f:
                xml = f.read()
            # Image element#####################################################
            image = ET.SubElement(annotations, 'image', 
                                    id=str(self.id), 
                                    name=img_name)
            with open(os.path.join(self.img_dir, img_name), 'rb') as f, \
                open(os.path.join(output_img_dir, img_name), 'wb') as f2:
                shutil.copyfileobj(f, f2)
            ####################################################################               
            soup = BeautifulSoup(xml, features='lxml')
            joint_list = soup.find('jointlist')
            subjoints_data = joint_list.find_all('joint')
            for subjoint in subjoints_data:
                endpoints = self.extract_endpoints(subjoint)
                endpoints = self.convert_endpoints(endpoints)
                endpoints = ';'.join([str(i) for i in endpoints])
                # Subjoint polyline element#####################################
                subjoint = ET.SubElement(image, 'polyline', 
                                        label='subjoint',
                                        occluded='0',
                                        points=endpoints,
                                        z_order='0')   
                ################################################################
            
            lanemarkers_data = soup.find_all('lanemark')
            for lanemarker in lanemarkers_data:
                x = float(lanemarker.find('position').get_text())
                x = self.convert_val_x(x)
                # Lanemarker point element######################################
                lanemarker = ET.SubElement(image, 'polyline', 
                                            label='lane_marker',
                                            occluded='0',
                                            points=f'{x},{self.px_height};{x},0',
                                            z_order='0')
                ################################################################
            self.id += 1

        self.create_task_zip(annotations, task_dir)


    
        
            

    def create_task_zip(self, annotations: ET.Element, task_dir: str):
        """Creates a zip file of the task directory

        Args:
            annotations (ET.element): annotations top level element of the XML
            file
            task_dir (str): path to the task directory
        """
        tree = ET.ElementTree(annotations)
        ET.indent(tree, space='\t', level=0)
        tree.write(os.path.join(task_dir, 'annotations.xml'),
                   encoding='utf-8', 
                   xml_declaration=True) 
        shutil.make_archive(task_dir, 'zip', task_dir)
        shutil.rmtree(task_dir)
       

    def extract_endpoints(self, subjoint):
        """Extracts the endpoints of the subjoint

        Args:
            subjoint (bs4.element.Tag): subjoint element

        Returns:
            tuple: (x1, y1, x2, y2)
        """
        x1 = float(subjoint.find('x1').get_text())
        y1 = float(subjoint.find('y1').get_text())
        x2 = float(subjoint.find('x2').get_text())
        y2 = float(subjoint.find('y2').get_text())
        return (x1, y1, x2, y2)


    def convert_endpoints(self, endpoints):
        """Converts the endpoints from millimeters to pixels

        Args:
            endpoints (tuple): (x1, y1, x2, y2)

        Returns:
            tuple: (x1, y1, x2, y2) in pixels
        """
        x1, y1, x2, y2 = endpoints
        x1 = self.convert_val_x(x1)
        x2 = self.convert_val_x(x2)
        y1 = self.convert_val_y(y1)
        y2 = self.convert_val_y(y2)
        return (x1, y1, x2, y2)
    

    def extract_date(self, date_str: str) -> datetime:
        """Extracts the date from the string

        Args:
            date_str (str): date string

        Returns:
            datetime: date object
        """ 
        date_str = date_str.split('.', 1)[0]
        return datetime.strptime(date_str, '%Y/%m/%d %H:%M:%S')

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

        return (s[start_index:end_index][::-1])
    

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
    



if __name__ == "__main__":
    data_dir = 'data'
    px_height = 1250
    px_width = 1040
    mm_height = 1250 * 4
    mm_width = 1040 * 4
    mode = 'range'
    task_size = 1000000000
    begin_MM = 22
    end_MM = 12
    year = 2014
    interstate = 'I16WB'
    ManualXML_CVAT_Parser(data_dir, px_height, px_width, 
                          mm_height, mm_width, mode, task_size,
                          begin_MM, end_MM, year, interstate)


    
    
                
