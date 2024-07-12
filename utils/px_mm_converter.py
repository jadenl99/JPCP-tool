class PXMMConverter:
    def __init__(self, px_height, px_width, mm_height, mm_width, num_images):
        self.px_height = px_height
        self.px_width = px_width
        self.mm_height = mm_height
        self.mm_width = mm_width
        self.num_images = num_images
        self.scale_factor_y = float(px_height) / mm_height
        self.scale_factor_x = float(px_width) / mm_width


    def convert_px_to_mm_relative(self, px_x, px_y, img_index):
        """Converts pixel coordinates to millimeter coordinates. Assumes that
        the origin for px measurement is the top left corner of the image and 
        the origin for the mm measurement is the bottom left corner of the 
        image. y-values are relative to the first image of the segment.

        Args:
            x (float): x-coordinate in pixels
            y (float): y-coordinate in pixels, use absolute value in terms of 
            a single image
            img_index (int): index of the image in the segment (zero-indexed)


        Returns:
            tuple: (x, y) in millimeters
        """
        mm_x = px_x / self.scale_factor_x
        abs_mm_y = (self.px_height - px_y) / self.scale_factor_y 
        mm_y = abs_mm_y + img_index * self.mm_height
        return (mm_x, mm_y)


    def convert_mm_to_px(self, mm_x, mm_y, img_index):
        """Converts millimeter coordinates to px coordinates. Assumes that
        the origin for px measurement is the top left corner of the image and 
        the origin for the mm measurement is the bottom left corner of the 
        image. y-values are relative to the first image of the segment.

        Args:
            x (float): x-coordinate in pixels
            y (float): y-coordinate in pixels, use absolute value in terms of a
            single image
            img_index (int): index of the current image in the segment
        """
        px_x = mm_x * self.scale_factor_x
        abs_px_y = self.px_height - mm_y * self.scale_factor_y
        px_y = (self.num_images - img_index - 1) * self.px_height + abs_px_y
        return (px_x, px_y)
    

    def px_abs_to_rel(self, px_y, img_index):
        """Converts absolute pixel y-coordinate to relative pixel y-coordinate
        in terms of the first image in the segment.

        Args:
            px_y (float): y-coordinate in pixels
            img_index (int): index of the current image in the segment

        Returns:
            float: relative y-coordinate in pixels
        """
        return px_y + (self.num_images - img_index - 1) * self.px_height
