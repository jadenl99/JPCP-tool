######################################################
# crop_slab_image.py                                 #
# Rewritten code by Aditya Tapshalkar and Jaden Lim  #
# Georgia Institute of Technology                    #
######################################################

from tqdm import tqdm
from bs4 import BeautifulSoup
import csv
import cv2
import os
import shutil
from collections import deque
from crop_slab.subjoint import SubJoint
from crop_slab.joint import HorizontalJoint
from crop_slab.utils.functions import LinearFunction
from crop_slab.slab_writer import SlabWriter
import numpy as np
class CropSlabs:
    def __init__(self, data_path, im_size, im_unit, mode, 
                 begin_MM, end_MM, year, interstate):
        # filepath of the dataset
        self.data_path = data_path
        self.im_size = im_size
        self.im_unit = im_unit
        self.im_length_mm = 5000

        self.db_name = f'{interstate}_MM{begin_MM}_to_MM{end_MM}'
        self.slab_writer = SlabWriter(interstate, begin_MM, end_MM, year)

        self.xml_path = os.path.join(self.data_path, "ManualXML")

        self.xml_list = self.filter_files(self.xml_path, "xml")

        self.slab_path = os.path.join(self.data_path, "Slabs")
        if not os.path.exists(self.slab_path):
            os.mkdir(self.slab_path)
        
        self.csv_path = os.path.join(self.data_path, "slabs.csv")  # Slab file
        self.txt_path = os.path.join(self.data_path, "debug.txt")  # Debug file
        self.input_im_path = None
        self.output_im_path = None

    
        self.slab_num = 1
        self.first_im = 0


        self.clean_folder()  # Cleaning folders; comment as necessary
        
        for single_mode in mode:
            self.slab_num = 1
            self.input_im_path = os.path.join(self.data_path, single_mode.capitalize())
            self.input_im_files = self.filter_files(self.input_im_path, "jpg")
            self.output_im_path = os.path.join(self.slab_path, 'output_' + single_mode)
            os.mkdir(self.output_im_path)
            self.crop()
            
        


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


    def filter_files(self, path, file_type) -> list:
        # Returns files of specified file type
        filtered = list(filter(lambda file: 
                               file.split(".")[-1] == file_type, 
                               os.listdir(path)))
        filtered.sort(key=lambda f: self.get_im_id(f))
        return filtered

    def clean_folder(self):
        # Removing previous slab images and metadata; comment as necessary
        try:
            shutil.rmtree(self.slab_path)
        except:
            pass

        os.mkdir(self.slab_path)


    def crop(self):
        """Algorithm to crop slabs from the dataset. 
        """
        NUM_JOINTS_PER_IMAGE = 2    
        
        with open(self.csv_path, 'w', newline='') as range_csv:

            fields = ["slab_index", "length (mm)", "width (mm)", 
                      "start_im", "end_im", "y_offset (mm)",
                      "y_min (mm)", "y_max (mm)"]
            writer = csv.DictWriter(range_csv, fieldnames=fields)
            writer.writeheader()
            
            joint_queue = deque()
            curr_joint = None
            # Iterate through all manual_xml files
            for i, xml_file in enumerate(tqdm(self.xml_list)):
                xml_data = open(os.path.join(self.xml_path, xml_file))
                xml_soup = BeautifulSoup(xml_data, "lxml")

                # Fetch all horizontal joint data in the xml file
                v_joints_data = []
                left_joint = 0
                right_joint = 3500
                try:
                    v_joints_data = xml_soup.findAll('lanemark')
                except:
                    pass
                
                try:
                    left_joint = float(
                        v_joints_data[0].find('position').get_text())
                except:
                    pass

                try:
                    right_joint = float(
                        v_joints_data[1].find('position').get_text())
                except:
                    pass
                
                if curr_joint is None:
                    # change if cutoff slab is not necessary to include
                    curr_joint = HorizontalJoint([SubJoint(0, 0, 3600, 0)],
                        left_bound=left_joint, right_bound=right_joint)
                # Fetch all joint segments data in the xml file
                subjoints_data = xml_soup.findAll('joint')
                subjoints = self.generate_subjoints_list(subjoints_data, i)
                for subjoint in subjoints:
                    if not curr_joint.belongs_to_joint(subjoint):
                        joint_queue.append(curr_joint)
                        # handle image cropping when two joints are collected
                        if len(joint_queue) == NUM_JOINTS_PER_IMAGE:
                            self.produce_image(joint_queue[0], joint_queue[1], 
                                             writer)
                            # with open(self.txt_path, 'a') as debug_file:
                            #     debug_file.write(str(self.slab_num - 1) + '__________________________\n')
                            #     debug_file.write(str(joint_queue[0]) + '\n')
                            #     debug_file.write(str(joint_queue[1]) + '\n')
                            #     debug_file.write('__________________________\n')
                            joint_queue.popleft()
                        # create new joint
                        curr_joint = HorizontalJoint(
                            [], left_joint, right_joint)
                        
                    curr_joint.add_subjoint(subjoint)

            if len(joint_queue) == 1:
                self.produce_image(joint_queue[0], curr_joint, writer)

            # delete if cutoff slab is not necessary to include
            top_y = len(self.xml_list) * self.im_length_mm - 1
            top_joint = HorizontalJoint([SubJoint(0, top_y, 3600, top_y)])   
            self.produce_image(curr_joint, top_joint, writer)
        # end write
                    
                    
    def generate_subjoints_list(self, subjoints_data, i: int) -> list[SubJoint]:
        """Given a piece of subjoint data extracted from BeautifulSoup, creates
        a list of subjoint objects

        Args:
            subjoint_data (bs4.ResultSet): A piece of subjoint data extracted
            from BeautifulSoup
            i (int): current index, representing the i-th xml file the loop is
            currently in

        Returns:
            list[SubJoint]: the list of SubJoint objects created from the 
            subjoint data. Subjoints are ordered from bottom to top 
            (by y1-value)
        """
        subjoints = []
        for subjoint_data in subjoints_data:
            subjoint = self.create_subjoint_obj(subjoint_data, i)
            if subjoint is not None and subjoint.dist > 200:
                subjoints.append(subjoint)
        subjoints.sort(key=lambda subjoint: subjoint.y1)
        return subjoints               
    

    def create_subjoint_obj(self, subjoint_data, i) -> SubJoint:
        """Given a piece of subjoint data extracted from BeautifulSoup, creates
        a subjoint object

        Args:
            subjoint_data (bs4.ResultSet): subjoint data extracted
            from BeautifulSoup
            i (int): current index, representing the i-th xml file the loop is
            currently in

        Returns:
            SubJoint: the SubJoint object created from the subjoint data or
            None if subjoint data is invalid (i.e. a point instead of a line)
        """
        
        x1 = float(subjoint_data.find('x1').get_text())
        y1 = float(subjoint_data.find('y1').get_text()) + \
            self.im_length_mm * i # for absolute position
        x2 = float(subjoint_data.find('x2').get_text())
        y2 = float(subjoint_data.find('y2').get_text()) + \
            self.im_length_mm * i       
        
            
        
        try:
            subjoint = SubJoint(int(x1), int(y1), int(x2), int(y2))
        except ValueError:
            return None
        
        return subjoint
    

    def produce_image(self, 
                    bottom_joint: HorizontalJoint, 
                    top_joint: HorizontalJoint,
                    writer: csv.DictWriter) -> None:
        """Given the bottom and top joint, crops image so that the relevant
        picture of the slab of interest between these joints is shown. The 
        corners are padded with black pixels. Also writes data to csv file.

        Args:
            bottom_joint (HorizontalJoint): the bottom joint
            top_joint (HorizontalJoint): the top joint
            writer (csv.DictWriter): the csv writer to write slab metadata to
        """
        bottom_img_index = bottom_joint.get_bottom_img_id(0, self.im_length_mm)
        top_img_index = top_joint.get_top_img_id(0, self.im_length_mm)
        #print(bottom_img_index, top_img_index)
        num_imgs_spanned = top_img_index - bottom_img_index + 1
        y_offset = self.im_length_mm * bottom_img_index
        scale_factor = self.im_size / self.im_length_mm
        y_min = int(bottom_joint.get_min_y() - y_offset)
        y_max = int(top_joint.get_max_y() - y_offset)
        x_min = int(bottom_joint.get_min_x())
        x_max = int(bottom_joint.get_max_x())
        if (x_max - x_min) < 2750:
            x_min = 0
            x_max = 3600
        img = self.join_images(bottom_img_index, top_img_index)
        
        # since (0, 0) is top left and we take (0, 0) as bottom left, some
        # adjustments are needed
        adj_y_min = int(scale_factor 
                        * (num_imgs_spanned * self.im_length_mm - y_max))
        adj_y_max = int(scale_factor 
                        * (num_imgs_spanned * self.im_length_mm - y_min))
        adj_x_min = int(scale_factor * x_min)
        adj_x_max = int(scale_factor * x_max)    
        #crop image first so less black pixels need to be added
        img = img[adj_y_min:adj_y_max, adj_x_min:adj_x_max]
        

        # blacken corners of image
        height, width, _ = img.shape
        subjoints = bottom_joint.subjoints

        # trim bottom, function created using absolute position (mm)
        bottom_func = LinearFunction(
            subjoints[0].x1, 
            subjoints[0].y1 - y_offset,
            subjoints[-1].x2, 
            subjoints[-1].y2 - y_offset
            )
        for x in range(width):
            # the y-cutoff is expressed relative to the cropped image
            y = (height) - scale_factor * (bottom_func.get_y(x * (1 / scale_factor) + x_min) - y_min)
            # account for edge calculations that may be slightly off
            if y < 0:
                y = 0
            elif y >= height:
                y = height - 1
            y = int(y)
            img[y:, x] = [0, 0, 0]

        # trim top
        subjoints = top_joint.subjoints
        top_func = LinearFunction(
            subjoints[0].x1, 
            subjoints[0].y1 - y_offset, 
            subjoints[-1].x2, 
            subjoints[-1].y2 - y_offset
            )
        for x in range(width):
            # the y-cutoff is expressed relative to the cropped image
            y = (height) - scale_factor * (top_func.get_y(x * (1 / scale_factor) + x_min) - y_min)
            # account for edge calculations that may be slightly off
            if y < 0:
                y = 0
            elif y >= height:
                y = height - 1
            y = int(y)
            img[:y, x] = [0, 0, 0]
            
        
        

        # save image to files
        cv2.imwrite(
            os.path.join(self.output_im_path, str(self.slab_num) + '.jpg'), img
            )    

        
        self.write_slab_metadata(writer, bottom_joint, top_joint)
        self.slab_num += 1

    
    def join_images(self, bottom_img_index, top_img_index):
        """Joins images together into one image
        Args:
            bottom_img_index (int): the index of the bottom image
            top_img_index (int): the index of the top image

        Returns:
            np.ndarray: the joined image
        """
        img = cv2.imread(
            os.path.join(self.input_im_path, self.input_im_files[bottom_img_index]))
        for i in range(bottom_img_index + 1, top_img_index + 1):
            temp_img = cv2.imread(
                os.path.join(self.input_im_path, self.input_im_files[i])
                )
            img = cv2.vconcat([temp_img, img])
        return img


    def write_slab_metadata(self, 
                            writer: csv.DictWriter, 
                            bottom_joint: HorizontalJoint, 
                            top_joint: HorizontalJoint):
        """Writes slab metadata to csv file (one row)

        Args:
            writer (csv.DictWriter): csv writer
            bottom_joint (HorizontalJoint): the bottom joint
            top_joint (HorizontalJoint): the top joint
        """
        bottom_img_index = bottom_joint.get_bottom_img_id(0, self.im_length_mm)
        top_img_index = top_joint.get_top_img_id(0, self.im_length_mm)
        width = bottom_joint.right_bound - bottom_joint.left_bound
        # measured from midpoint to midpoint
        length = top_joint.get_y_midpoint() - bottom_joint.get_y_midpoint()
        # uses absolute location of the bottom joint's midpoint
        y_offset = bottom_joint.get_y_midpoint()
        y_min = int(bottom_joint.get_min_y())
        y_max = int(top_joint.get_max_y())
 
        writer.writerow({
                        "slab_index": self.slab_num,
                        "length (mm)": length,
                        "width (mm)": width,
                        "start_im": self.xml_list[bottom_img_index],
                        "end_im": self.xml_list[top_img_index],
                        # y_offset calculated always using bottom left corner
                        "y_offset (mm)": y_offset, 
                        "y_min (mm)": y_min,
                        "y_max (mm)": y_max  
                        })
        
        start_im = self.get_im_id(self.xml_list[bottom_img_index])  
        end_im = self.get_im_id(self.xml_list[top_img_index])
        self.slab_writer.write_slab_entry(self.slab_num, length, width, 
                                          start_im, end_im, y_offset, 
                                          y_min, y_max, bottom_joint)

if __name__ == '__main__':
    CropSlabs('../data/MP18-17')
