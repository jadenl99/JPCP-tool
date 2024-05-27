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
from db_operation.slab_writer import SlabWriter
from file_manager.crop_files import CropFileManager
from utils.px_mm_converter import PXMMConverter
import numpy as np
import sys
class CropSlabsCVAT:
    def __init__(self, data_path, 
                 px_height, px_width, 
                 mm_height, mm_width,
                 mode, begin_MM, end_MM, year, interstate, validation_only=False):
        # filepath of the dataset
        self.recorded = False
        self.data_path = data_path
        self.px_height = px_height
        self.px_width = px_width
        self.mm_height = mm_height
        self.mm_width = mm_width
        self.validation_only = validation_only
        self.im_length_mm = 5000
        self.file_manager = CropFileManager(data_path, year)
        self.scaler = None
        self.slab_writer = None
        self.slab_num = 1
        self.first_im = 0
        for single_mode in mode:
            with open(self.file_manager.debug_path, 'w') as debug_file:
                writer = csv.writer(debug_file)
                writer.writerow(["start_img", "end_img", "message"]) 
            self.slab_num = 1
            self.file_manager.switch_image_mode(single_mode)
            if not self.scaler:
                self.scaler = PXMMConverter(self.px_height, self.px_width, 
                                            self.mm_height, self.mm_width,
                                            len(self.file_manager.input_im_files))
            if not self.slab_writer and not self.validation_only:
                self.slab_writer = SlabWriter(interstate, begin_MM, end_MM, year, self.scaler) 
            self.num_files = len(self.file_manager.input_im_files)  
            self.crop()
            self.recorded = True

 
    def crop(self):
        """Algorithm to crop slabs from the dataset. 
        """
        NUM_JOINTS_PER_IMAGE = 2    
        
        with open(self.file_manager.csv_path, 'w', newline='') as range_csv:

            fields = ["slab_index", "length (mm)", "width (mm)", 
                      "start_im", "end_im", "y_offset (mm)",
                      "y_min (mm)", "y_max (mm)"]
            writer = csv.DictWriter(range_csv, fieldnames=fields)
            writer.writeheader()

            joint_queue = deque()
            curr_joint = None
            # Iterate through all manual_xml files
            xml_data = open(self.file_manager.annotation_file)
            xml_soup = BeautifulSoup(xml_data, "lxml")
            images = xml_soup.find_all('image')
            for i, image in enumerate(tqdm(images)):
                subjoints_data = image.find_all('polyline')
                subjoints_data = [subjoint for subjoint in subjoints_data
                             if subjoint['label'] == 'subjoint']

                if curr_joint is None:
                    bottom_y = len(self.file_manager.input_im_files) * self.px_height - 1
                    curr_joint = HorizontalJoint([SubJoint(0, bottom_y, self.px_width - 1, bottom_y)])
                # Fetch all joint segments data in the xml file
                subjoints = self.generate_subjoints_list(subjoints_data, i)
                for subjoint in subjoints:
                    if not curr_joint.belongs_to_joint(subjoint):
                        joint_queue.append(curr_joint)
                        # handle image cropping when two joints are collected
                        if len(joint_queue) == NUM_JOINTS_PER_IMAGE:
                            self.produce_image(joint_queue[0], joint_queue[1], 
                                             writer)
                            joint_queue.popleft()
                        # create new joint
                        curr_joint = HorizontalJoint([])
                        
                    curr_joint.add_subjoint(subjoint)

            if len(joint_queue) == 1:
                self.produce_image(joint_queue[0], curr_joint, writer)

            # delete if cutoff slab is not necessary to include
            top_joint = HorizontalJoint([SubJoint(0, 0, self.px_width - 1, 0)])   
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
            if subjoint is not None and subjoint.dist > 50:
                subjoints.append(subjoint)
        subjoints.sort(key=lambda subjoint: subjoint.y1, reverse=True)
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
        
        points = subjoint_data['points']     
        points = points.replace(',', ';')
        points = points.split(';')
        x1 = int(float(points[0]))
        y1 = self.scaler.px_abs_to_rel(int(float(points[1])), i)
        x2 = int(float(points[2]))
        y2 = self.scaler.px_abs_to_rel(int(float(points[3])), i)
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
        bottom_img_index = bottom_joint.get_bottom_img_id(self.num_files, self.px_height)
        top_img_index = top_joint.get_top_img_id(self.num_files, self.px_height)
        y_offset = self.scaler.px_abs_to_rel(0, top_img_index)
        
        if not self.validation_only:
            img = self.join_images(bottom_img_index, top_img_index)
            img = self.modify_image(img, bottom_joint, top_joint, y_offset)
            # save image to files
            cv2.imwrite(
                os.path.join(self.file_manager.output_im_path, str(self.slab_num) + '.jpg'), img
                )
        self.write_slab_metadata(writer, bottom_joint, top_joint)
        self.slab_num += 1

    
    def modify_image(self, img: np.ndarray, bottom_joint: HorizontalJoint, 
                     top_joint: HorizontalJoint, y_offset: float) -> np.ndarray:
        """Modifies the image by cropping it to the slab of interest and padding
        with black pixels

        Args:
            img (np.ndarray): stiched image(s) of the slab of interest
            bottom_joint (HorizontalJoint): bottom joint of the slab of interest
            top_joint (HorizontalJoint): top joint of the slab of interest
            y_offset (float): y-offset of the slab of interest

        Returns:
            np.ndarray: _description_
        """
        # crop image first so less black pixels need to be added
        y_abs_min = int(top_joint.get_min_y() - y_offset)
        y_abs_max = int(bottom_joint.get_max_y() - y_offset)
        x_abs_min = int(bottom_joint.get_min_x())
        x_abs_max = int(bottom_joint.get_max_x())
        img = img[y_abs_min:y_abs_max, x_abs_min:x_abs_max]
        

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
            y = bottom_func.get_y(x_abs_min + x) - y_abs_min
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
            y = top_func.get_y(x_abs_min + x) - y_abs_min
            # account for edge calculations that may be slightly off
            if y < 0:
                y = 0
            elif y >= height:
                y = height - 1
            y = int(y)
            img[:y, x] = [0, 0, 0]
        return img

        

    def join_images(self, bottom_img_index: int, top_img_index: int) -> None:
        """Joins images together into one image
        Args:
            bottom_img_index (int): the index of the bottom image
            top_img_index (int): the index of the top image

        Returns:
            np.ndarray: the joined image
        """
        input_path = self.file_manager.input_im_path
        input_files = self.file_manager.input_im_files
        img = cv2.imread(
            os.path.join(input_path, input_files[bottom_img_index]))
        if self.file_manager.image_mode == 'segmentation':
            img = cv2.resize(img, (self.px_width, self.px_height))
        for i in range(bottom_img_index + 1, top_img_index + 1):
            temp_img = cv2.imread(
                os.path.join(input_path, input_files[i])
                )
            if self.file_manager.image_mode == 'segmentation':
                temp_img = cv2.resize(temp_img, (self.px_width, self.px_height))
            img = cv2.vconcat([temp_img, img])
        return img


    def write_slab_metadata(self, 
                            writer: csv.DictWriter, 
                            bottom_joint: HorizontalJoint, 
                            top_joint: HorizontalJoint) -> None:
        """Writes slab metadata to csv file (one row)

        Args:
            writer (csv.DictWriter): csv writer
            bottom_joint (HorizontalJoint): the bottom joint
            top_joint (HorizontalJoint): the top joint
        """
        bottom_img_index = bottom_joint.get_bottom_img_id(self.num_files, 
                                                          self.px_height)
        mid_img_index = bottom_joint.get_midpoint_img_id(self.num_files, 
                                                         self.px_height)
        top_img_index = top_joint.get_top_img_id(self.num_files, self.px_height)

        px_width = bottom_joint.get_max_x() - bottom_joint.get_min_x()
        px_length = bottom_joint.get_y_midpoint() - top_joint.get_y_midpoint()

        mm_width = float(px_width) / self.scaler.scale_factor_x
        mm_length = float(px_length) / self.scaler.scale_factor_y
        round(mm_width, 2)
        round(mm_length, 2)

        y_px_offset = bottom_joint.get_y_midpoint()
        y_px_bottom = int(bottom_joint.get_max_y())
        y_px_top = int(top_joint.get_min_y())

        y_mm_bottom = self.scaler.convert_px_to_mm_relative(
            0, y_px_bottom % self.px_height, bottom_img_index
            )[1]               
        y_mm_offset = self.scaler.convert_px_to_mm_relative(
            0, y_px_offset % self.px_height, mid_img_index
            )[1]
        y_mm_top = self.scaler.convert_px_to_mm_relative(
            0, y_px_top % self.px_height, top_img_index
            )[1]        
        
        input_files = self.file_manager.input_im_files
        if not self.validation_only:
            writer.writerow({
                            "slab_index": self.slab_num,
                            "length (mm)": mm_length,
                            "width (mm)": mm_width,
                            "start_im": input_files[bottom_img_index],
                            "end_im": input_files[top_img_index],      
                            "y_offset (mm)": y_mm_offset, 
                            "y_min (mm)": y_mm_bottom,
                            "y_max (mm)": y_mm_top  
                            })
        

        start_im = self.file_manager.get_im_id(input_files[bottom_img_index]) 
        end_im = self.file_manager.get_im_id(input_files[top_img_index])
        if not self.recorded and not self.validation_only:
            self.slab_writer.write_slab_entry(self.slab_num, mm_length, mm_width, 
                                          start_im, end_im, y_mm_offset, 
                                          y_mm_bottom, y_mm_top, bottom_joint)
            
        if mm_width < 2750:
            with open(self.file_manager.debug_path, 'a') as debug_file:
                writer = csv.writer(debug_file)
                writer.writerow([start_im, end_im, 
                                 "Check CVAT for mislabeled joint since width " 
                                 "of detected joint is less than 2.75m"])
        
if __name__ == '__main__':
    CropSlabsCVAT('../data/MP18-17')
