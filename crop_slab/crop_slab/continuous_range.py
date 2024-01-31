import os
import cv2
import numpy as np
# from utils import utils


class ContinuousRange:
    def __init__(self, range_path, units="mm", im_height=1250):
        if units not in ["mm", "px"]:
            raise ValueError("Invalid value for argument \"units\":\n\tUnits must be mm (millimeters) or px (pixels)") 
        if not os.path.exists(range_path):
            raise ValueError("Invalid value for argument \"range_path\":\n\tInvalid path at {}, no such path exists".format(range_path))
        self.units = units
        self.path = range_path
        self.im_names = list(filter(lambda p: p.split(".")[-1] == "jpg", os.listdir(range_path)))
        self.im_names.sort(key=lambda f: self.get_im_id(f))
        self.im_paths = [os.path.join(self.path, iname) for iname in self.im_names]
        self.num_ims = len(self.im_names)

    def get_im_id(self, s):
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

    def _merge_ims(self, ims, padding=0):
        im = np.concatenate(ims, axis=0).astype(np.float64)

        padded_im = np.zeros((im.shape[0] + padding, im.shape[1], im.shape[2]))
        padded_im[padding:] = im[:]
        return padded_im

    def load_chunk(self, start, end, left, right, padding=0, run=""):
        if self.units == "mm": # Units are millimeters, not pixels, so we divide by 4 to get pixel values
           start //= 4
           end //= 4


        start_im = int(start // 5000)
        start_px = int(start % 5000)

        end_im = int(end // 5000)
        end_px = int(end % 5000)

        if end - start > 50000:  # ten images
            print("Image too large")
            raise "Image is too large for some reason"

            # return None



        if start_im < 0:
            raise ValueError("Invalid value for argument \"start\":\n\tLess than zero")
        if end_im < 0:
            raise ValueError("Invalid value for argument \"end\":\n\tLess than zero")

        if start_im >= self.num_ims:
            raise ValueError("Invalid value for argument \"start\":\n\tToo large, not enough range images\nrun {}\n{} <= {}\nend: {}".format(run, self.num_ims, start_im, end_im)) 
        if end_im >= self.num_ims:
            #raise ValueError("Invalid value for argument \"end\":\n\tToo large, not enough range images") 
            print("Invalid value for argument \"start\":\n\tToo large, not enough range images\nrun {}\n{} <= {}".format(run, self.num_ims, end_im)) 
            end_im = self.num_ims - 1
            end_px = 0

        ims = []
        if start_im == end_im:  # multiple joints in single image
            im = cv2.imread(self.im_paths[start_im])
            im = cv2.resize(im, (4160, 5000))  # for 4-mm resolution image only
            start_px = 1 if start_px == 0 else start_px  # avoid the corner case of start_px=0

            im = im[-1*end_px : -1*start_px, left:right]
            ims.append(im)
        else:
            for i in range(start_im, end_im + 1):
                im = cv2.imread(self.im_paths[i])
                im = cv2.resize(im, (4160, 5000))  # for 4-mm resolution image only
                if i == start_im:
                    im = im[:-1 * start_px, left:right] # Cut off the bottom start_px pixels
                elif i == end_im:
                    im = im[-1 * end_px:, left:right] # Cut off the top end_px pixels
                else:
                    im = im[:, left:right]
                ims.append(im)

        chunk = self._merge_ims(ims[::-1], padding)
        return chunk
