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
from crop_slab.continuous_range import ContinuousRange
import shutil
from collections import deque
from crop_slab.subjoint import SubJoint
from crop_slab.joint import HorizontalJoint
from crop_slab.utils.functions import LinearFunction
import numpy as np
class CropSlabs:
    def __init__(self, data_path, im_size=5000, im_unit="px", mode='range'):
        # filepath of the dataset
        self.data_path = data_path
        self.im_size = im_size
        self.im_unit = im_unit

        if mode == 'range':
            self.range_path = os.path.join(self.data_path, "Range")
        elif mode == 'intensity':
            self.range_path = os.path.join(self.data_path, "Intensity")

        self.xml_path = os.path.join(self.data_path, "XML")

        self.img_list = self.filter_files(self.range_path, "jpg")
        self.xml_list = self.filter_files(self.xml_path, "xml")

        self.slab_path = os.path.join(self.data_path, "Slabs")
        self.csv_path = os.path.join(self.data_path, "slabs.csv")  # Slab file
        self.txt_path = os.path.join(self.data_path, "debug.txt")  # Debug file

        self.slab_len = None
        self.slab_num = 1
        self.first_im = 0
        # # Continuous Range stitches images together
        # self.cr = ContinuousRange(self.range_path, im_height=self.im_size, units=self.im_unit)

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
        self.clean_folder()  # Cleaning folders; comment as necessary
        with open(self.csv_path, 'w', newline='') as range_csv:

            fields = ["slab_index", "length", "width", 
                      "start_im", "end_im", "y_offset",
                      "y_min", "y_max"]
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
                        if len(joint_queue) >= 2:
                            self.slice_image(joint_queue[0], joint_queue[1], 
                                             writer)
                            with open(self.txt_path, 'a') as debug_file:
                                debug_file.write(str(self.slab_num - 1) + '__________________________\n')
                                debug_file.write(str(joint_queue[0]) + '\n')
                                debug_file.write(str(joint_queue[1]) + '\n')
                                debug_file.write('__________________________\n')
                            joint_queue.popleft()
                        # create new joint
                        curr_joint = 1
                        curr_joint = HorizontalJoint(
                            [], left_joint, right_joint)
                        
                    curr_joint.add_subjoint(subjoint)

            if len(joint_queue) == 1:
                self.slice_image(joint_queue[0], curr_joint, writer)

            # delete if cutoff slab is not necessary to include
            top_y = len(self.xml_list) * self.im_size - 1
            top_joint = HorizontalJoint([SubJoint(0, top_y, 3600, top_y)])   
            self.slice_image(curr_joint, top_joint, writer)
        # end write
                    
                    
    def generate_subjoints_list(self, subjoints_data, i) -> list[SubJoint]:
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
            SubJoint: the SubJoint object created from the subjoint data
        """
        
        x1 = float(subjoint_data.find('x1').get_text())
        y1 = float(subjoint_data.find('y1').get_text()) + \
            self.im_size * i # for absolute position
        x2 = float(subjoint_data.find('x2').get_text())
        y2 = float(subjoint_data.find('y2').get_text()) + \
            self.im_size * i       
        
        return SubJoint(int(x1), int(y1), int(x2), int(y2))
    

    def slice_image(self, 
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
        bottom_img_index = bottom_joint.get_bottom_img_id(0, self.im_size)
        top_img_index = top_joint.get_top_img_id(0, self.im_size)
        num_imgs_spanned = top_img_index - bottom_img_index + 1
        y_offset = self.im_size * bottom_img_index

        y_min = int(bottom_joint.get_min_y() - y_offset)
        y_max = int(top_joint.get_max_y() - y_offset)
        x_min = int(bottom_joint.left_bound)
        x_max = int(bottom_joint.right_bound)
        
        img = cv2.imread(
            os.path.join(self.range_path, self.img_list[bottom_img_index]))
        # scale image
        img = cv2.resize(img, (int((self.im_size) * .832), self.im_size))  

        # join images together
        for i in range(bottom_img_index + 1, top_img_index + 1):
            temp_img = cv2.imread(
                os.path.join(self.range_path, self.img_list[i])
                )
            # scale image
            temp_img = cv2.resize(temp_img, 
                                  (int((self.im_size) * .832), self.im_size))
            img = cv2.vconcat([temp_img, img])
        
        # since (0, 0) is top left and we take (0, 0) as bottom left, some
        # adjustments are needed
        adj_y_min = num_imgs_spanned * self.im_size - y_max
        adj_y_max = num_imgs_spanned * self.im_size - y_min
        
        #crop image first so less black pixels need to be added
        img = img[adj_y_min:adj_y_max, x_min:x_max]
        
        # blacken corners of image
        height, width, _ = img.shape
        subjoints = bottom_joint.subjoints

        # trim bottom
        bottom_func = LinearFunction(
            subjoints[0].x1, 
            subjoints[0].y1 - y_offset,
            subjoints[-1].x2, 
            subjoints[-1].y2 - y_offset
            )
        for x in range(width):
            # the y-cutoff is expressed relative to the cropped image
            y = (height) - (bottom_func.get_y(x + x_min) - y_min)
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
            y = (height) - (top_func.get_y(x + x_min) - y_min)
            # account for edge calculations that may be slightly off
            if y < 0:
                y = 0
            elif y >= height:
                y = height - 1
            y = int(y)
            img[:y, x] = [0, 0, 0]
            
        
        

        # save image to files
        cv2.imwrite(
            os.path.join(self.slab_path, str(self.slab_num) + '.jpg'), img
            )    

        self.write_slab_metadata(writer, bottom_joint, top_joint)
        self.slab_num += 1


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
        bottom_img_index = bottom_joint.get_bottom_img_id(0, self.im_size)
        top_img_index = top_joint.get_top_img_id(0, self.im_size)
        width = bottom_joint.right_bound - bottom_joint.left_bound
        # measured from midpoint to midpoint
        length = top_joint.get_y_midpoint() - bottom_joint.get_y_midpoint()
        # uses absolute location of the bottom joint's midpoint
        y_offset = bottom_joint.get_y_midpoint()
        y_min = int(bottom_joint.get_min_y())
        y_max = int(top_joint.get_max_y())
 
        writer.writerow({
                        "slab_index": self.slab_num,
                        "length": length,
                        "width": width,
                        "start_im": self.xml_list[bottom_img_index],
                        "end_im": self.xml_list[top_img_index],
                        # y_offset calculated always using bottom left corner
                        "y_offset": y_offset, 
                        "y_min": y_min,
                        "y_max": y_max  
                        })
        

if __name__ == '__main__':
    CropSlabs('../data/MP18-17')
