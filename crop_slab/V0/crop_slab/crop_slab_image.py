#########################################
# crop_slab_image.py                    #
# Rewritten code by Aditya Tapshalkar   #
# Fall 2021 - Special Problems          #
# Georgia Institute of Technology       #
#########################################

from tqdm import tqdm
from bs4 import BeautifulSoup
import csv
import cv2
import os
from .continuous_range import ContinuousRange
import shutil


class CropSlabs:
    def __init__(self, data_path, im_size=5000, im_unit="px", mode='range'):
        self.data_path = data_path
        self.im_size = im_size
        self.im_unit = im_unit

        if mode == 'range':
            self.range_path = os.path.join(self.data_path, "Range")
        elif mode == 'intensity':
            self.range_path = os.path.join(self.data_path, "Intensity")

        # try:
        #    self.xml_path = os.path.join(self.data_path, "ManualXML")
        # except:
        self.xml_path = os.path.join(self.data_path, "XML")

        self.img_list = self.filter_files(self.range_path, "jpg")
        self.xml_list = self.filter_files(self.xml_path, "xml")

        self.slab_path = os.path.join(self.data_path, "Slabs")
        self.csv_path = os.path.join(self.data_path, "slabs.csv")  # Slab file
        self.txt_path = os.path.join(self.data_path, "debug.txt")  # Debug file

        self.slab_len = None
        self.slab_num = 0
        self.first_im = 0
        self.y_offset = self.im_size * self.first_im

        # Continuous Range stitches images together
        self.cr = ContinuousRange(self.range_path, im_height=self.im_size, units=self.im_unit)

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

    def filter_files(self, path, file_type):

        # Returns files of specified file type
        filtered = list(filter(lambda file: file.split(".")[-1] == file_type, os.listdir(path)))
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

            fields = ["slab_index", "length", "width", "start_im", "end_im", "y_offset"]
            writer = csv.DictWriter(range_csv, fieldnames=fields)
            writer.writeheader()

            # First image slab cropping
            bottom_im = open(os.path.join(self.xml_path, self.xml_list[self.first_im]))
            bottom_soup = BeautifulSoup(bottom_im, "lxml")

            try:
                bot_h_joints = bottom_soup.findAll("jointlist")[0].findAll("joint")
            except:
                bot_h_joints = []

            try:
                bot_v_joints = bottom_soup.findAll("lanemarkinformation")[0].findAll("lanemark")
            except:
                bot_v_joints = bottom_soup.findAll("verticaljointlist")[0].findAll("joint")

            bot_h_left_joints = []
            bot_h_right_joints = []

            # Detection of horizontal joints
            for bot_h in bot_h_joints:
                x1_val = float(bot_h.findAll("x1")[0].get_text())
                x2_val = float(bot_h.findAll("x2")[0].get_text())
                y1_val = float(bot_h.findAll("y1")[0].get_text())
                y2_val = float(bot_h.findAll("y2")[0].get_text())
                joint_len = float(bot_h.findAll("length")[0].get_text())

                # If joint spans one full lane, or is at the top or bottom of range image
                ### JOINT THRESHOLD ###
                if joint_len > 900 \
                        or (y1_val < 10
                            or y1_val > 4990
                            or y2_val < 10
                            or y2_val > 4990):
                    if x1_val < 2050:  # left lane
                        if x2_val < 3000:
                            bot_h_left_joints.append([y1_val, y2_val])
                        else:  # joint spans both lanes
                            bot_h_left_joints.append([y1_val, (y1_val + y2_val) // 2])
                            bot_h_right_joints.append([(y1_val + y2_val) // 2, y2_val])
                    elif x1_val < 3000:  # right lane
                        bot_h_right_joints.append([y1_val, y2_val])

            bot_h_left_joints.sort()
            bot_h_right_joints.sort()

            # vertical joint/lane marking detection
            try:
                bot_v_left_joint = float(bot_v_joints[0].findAll("position")[0].get_text())
                bot_v_right_joint = float(bot_v_joints[-1].findAll("position")[0].get_text())
            except:
                bot_v_left_joint = 0
                try:
                    bot_v_right_joint = float(bot_v_joints[0].findAll("x1")[0].get_text())
                except:
                    bot_v_right_joint = 3500
            first_pic = self.xml_list[self.first_im]

            with open(self.txt_path, 'w') as debug_file:

                # Iterating through all range and XML files with sliding window technique.
                # Keeps track of current and previous joint data.
                # Slabs are cropped from previous image.
                for curr_im in tqdm(range(self.first_im + 1, len(self.xml_list))):

                    debug_file.write("\n_________________________________________\n")
                    top_im = open(os.path.join(self.xml_path, self.xml_list[curr_im]))

                    debug_file.write(f"Bottom Image:\t {self.xml_list[curr_im - 1]}\n")
                    debug_file.write(f"Top Image:\t\t {self.xml_list[curr_im]}\n")

                    top_soup = BeautifulSoup(top_im, "lxml")

                    # Gathering current image's joint data
                    try:
                        top_h_joints = top_soup.findAll("jointlist")[0].findAll("joint")
                    except:
                        top_h_joints = []

                    try:
                        top_v_joints = top_soup.findAll("lanemarkinformation")[0].findAll("lanemark")
                    except:
                        top_v_joints = []

                    top_h_left_joints = []
                    top_h_right_joints = []
                    for top_h in top_h_joints:
                        x1_val = float(top_h.findAll("x1")[0].get_text())
                        x2_val = float(top_h.findAll("x2")[0].get_text())
                        y1_val = float(top_h.findAll("y1")[0].get_text()) + self.im_size * curr_im
                        y2_val = float(top_h.findAll("y2")[0].get_text()) + self.im_size * curr_im
                        joint_len = float(top_h.findAll("length")[0].get_text())

                        ### JOINT THRESHOLD ###
                        if joint_len > 900 \
                                or (y1_val < 10 + self.im_size * curr_im
                                    or y1_val > 4990 + self.im_size * curr_im
                                    or y2_val < 10 + self.im_size * curr_im
                                    or y2_val > 4990 + self.im_size * curr_im):
                            if x1_val < 2050:  # left side
                                if x2_val < 3000:
                                    top_h_left_joints.append([y1_val, y2_val])
                                else:
                                    top_h_left_joints.append([y1_val, (y1_val + y2_val) // 2])
                                    top_h_right_joints.append([(y1_val + y2_val) // 2, y2_val])
                            elif x1_val < 3000:  # right side
                                top_h_right_joints.append([y1_val, y2_val])

                    top_h_left_joints.sort()
                    top_h_right_joints.sort()

                    try:
                        top_v_left_joint = float(top_v_joints[0].findAll("position")[0].get_text())
                        top_v_right_joint = float(top_v_joints[-1].findAll("position")[0].get_text())
                    except:
                        top_v_left_joint = 0
                        top_v_right_joint = 3500

                    debug_file.writelines([str(bot_h_left_joints), "\t", str(bot_h_right_joints), "\n"])
                    debug_file.writelines([str(top_h_left_joints), "\t", str(top_h_right_joints), "\n"])

                    if self.y_offset is None:  # second image in dataset
                        first_h_left = bot_h_left_joints[0]
                        first_h_right = bot_h_right_joints[0]
                        if abs(first_h_left[1] - first_h_right[0]) < 100:  # bottom-most left and right joints preset
                            self.y_offset = (first_h_left[1] + first_h_right[0]) / 2 + self.im_size * self.first_im
                            bot_h_left_joints.pop(0)
                            bot_h_right_joints.pop(0)
                        else:  # only right joint present at bottom

                            # left joint comes first
                            if (first_h_left[1] - first_h_right[0]) > 100:
                                self.y_offset = 0 + self.im_size * self.first_im
                                bot_h_left_joints.pop(0)

                            # right joint comes first
                            else:
                                self.y_offset = 0 + self.im_size * self.first_im
                                bot_h_right_joints.pop(0)

                    debug_file.write(f"curr y_offset: {self.y_offset}\n")

                    # Merging current and previous image right lane joints if applicable
                    if len(top_h_right_joints) > 0 and len(bot_h_right_joints) > 0:
                        if abs(top_h_right_joints[0][0] - bot_h_right_joints[-1][1]) < 100:
                            bot_h_right_joints[-1][1] = top_h_right_joints[0][1]
                            top_h_right_joints.pop(0)

                    # Merging current and previous image left lane joints if applicable
                    if len(top_h_left_joints) > 0 and len(bot_h_left_joints) > 0:
                        if abs(top_h_left_joints[0][0] - bot_h_left_joints[-1][1] < 100):
                            bot_h_left_joints[-1][1] = top_h_left_joints[0][1]
                            top_h_left_joints.pop(0)

                    debug_file.writelines([str(bot_h_left_joints), "\t", str(bot_h_right_joints), "\n"])
                    debug_file.writelines([str(top_h_left_joints), "\t", str(top_h_right_joints), "\n"])

                    # Collecting joint from bottom-most left and right lane joints from previous image
                    while len(bot_h_left_joints) > 0 and len(bot_h_right_joints) > 0:
                        next_left = bot_h_left_joints.pop(0)
                        next_right = bot_h_right_joints.pop(0)
                        if abs(next_left[1] - next_right[0]) < 100:  # Same joint
                            slab_offset = (next_left[1] + next_right[0]) / 2 + self.im_size * self.first_im
                            debug_file.writelines([str(slab_offset), "\n"])
                            slab_len = slab_offset - self.y_offset
                            self.slab_num += 1
                            new_im = self.cr.load_chunk(self.y_offset,
                                                        slab_offset,
                                                        int(bot_v_left_joint),
                                                        int(bot_v_right_joint),
                                                        padding=0)
                            if new_im is not None:
                                new_slab_path = os.path.join(self.slab_path, str(self.slab_num) + '.png')
                                debug_file.write(new_slab_path + "\n")
                                cv2.imwrite(new_slab_path, new_im)
                            self.y_offset = slab_offset

                            writer.writerow({
                                "slab_index": self.slab_num,
                                "length": f"{slab_len:.2f}",
                                "width": (bot_v_right_joint - bot_v_left_joint),
                                "start_im": first_pic,
                                "end_im": self.xml_list[curr_im],
                                "y_offset": self.y_offset
                            })
                            first_pic = self.xml_list[curr_im]

                        else:  # Different joint; only reinsert right joint at beginning
                            bot_h_right_joints.insert(0, next_left)

                    # Collecting joint from bottom-most left joint and top image's bottom-most right joint
                    if len(bot_h_left_joints) > 0 and len(top_h_right_joints) > 0:
                        next_left = bot_h_left_joints.pop(-1)
                        next_right = top_h_right_joints.pop(0)
                        if abs(next_right[0] - next_left[1]) < 100:  # Same joint
                            slab_offset = (next_left[1] + next_right[0]) / 2 + self.im_size * self.first_im
                            debug_file.writelines([str(slab_offset), "\n"])
                            slab_len = slab_offset - self.y_offset
                            self.slab_num += 1
                            new_im = self.cr.load_chunk(self.y_offset, slab_offset, int(bot_v_left_joint),
                                                        int(bot_v_right_joint),
                                                        padding=0)
                            if new_im is not None:
                                new_slab_path = os.path.join(self.slab_path, str(self.slab_num) + '.png')
                                debug_file.writelines([new_slab_path, "\n"])
                                cv2.imwrite(new_slab_path, new_im)
                            self.y_offset = slab_offset

                            writer.writerow({
                                "slab_index": self.slab_num,
                                "length": f"{slab_len:.2f}",
                                "width": (bot_v_right_joint - bot_v_left_joint),
                                "start_im": first_pic,
                                "end_im": self.xml_list[curr_im],
                                "y_offset": self.y_offset
                            })
                            first_pic = self.xml_list[curr_im]

                        else:
                            top_h_right_joints.insert(0, next_right)

                    # Setting previous image as current image's joints
                    bot_h_left_joints, bot_h_right_joints = top_h_left_joints, top_h_right_joints
                    bot_v_left_joint = top_v_left_joint
                    bot_v_right_joint = top_v_right_joint
                # end loop

                # slab cropping for last image, due to sliding window processing all previous images
                while len(bot_h_left_joints) > 0 and len(bot_h_right_joints) > 0:
                    next_left = bot_h_left_joints.pop(0)
                    next_right = bot_h_right_joints.pop(0)
                    if abs(next_left[1] - next_right[0]) < 100:
                        slab_offset = (next_left[1] + next_right[0]) / 2 + self.im_size * self.first_im
                        debug_file.writelines([str(slab_offset), "\n"])
                        slab_len = slab_offset - self.y_offset
                        self.slab_num += 1
                        new_im = self.cr.load_chunk(self.y_offset, slab_offset, int(bot_v_left_joint),
                                                    int(bot_v_right_joint),
                                                    padding=0)
                        if new_im is not None:
                            new_slab_path = os.path.join(self.slab_path, str(self.slab_num) + '.png')
                            debug_file.writelines([str(new_slab_path), "\n"])
                            cv2.imwrite(new_slab_path, new_im)
                        self.y_offset = slab_offset

                        writer.writerow({
                            "slab_index": self.slab_num,
                            "length": f"{slab_len:.2f}",
                            "width": (bot_v_right_joint - bot_v_left_joint),
                            "start_im": first_pic,
                            "end_im": self.xml_list[curr_im],
                            "y_offset": self.y_offset
                        })
                        first_pic = self.xml_list[curr_im]
                    else:
                        bot_h_right_joints.insert(0, next_left)


if __name__ == '__main__':
    CropSlabs('../data/MP18-17')
