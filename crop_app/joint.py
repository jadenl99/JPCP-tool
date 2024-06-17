import sys
import crop_app.subjoint as subjoint
class HorizontalJoint:
    """A horizontal joint is a joint that spans from the left boundary of the
    lane to the right boundary of the lane. Joints need not be parallel to the
    horizontal plane. A horizontal joint can possibly be diagonal, as long as
    it satisfies the condition in the first sentence. Each horizontal joint is
    composed of multiple subjoints.

    In the XML files, each horizontal joint is often broken up into two seperate
    joints, one for each side of the lane. This is because there are two cameras


    Attributes:
        subjoints (list): list of subjoints that compose the horizontal joint
        left_bound (int): left boundary of the lane/joint
        right_bound (int): right boundary of the lane/joint
    """
    def __init__(self, subjoints, left_bound: int=0, right_bound: int=3500):
        self.subjoints = subjoints
        self.left_bound = left_bound
        self.right_bound = right_bound
    

    def add_subjoint(self, subjoint: subjoint.SubJoint) -> None:
        """Adds a subjoint to the horizontal joint's list of subjoints and
        orders the subjoints from left to right.

        
        Args:
            subjoint (SubJoint): subjoint to add to the horizontal joint
        """ 
        self.subjoints.append(subjoint)
        self.subjoints.sort(key=lambda subjoint: subjoint.x1)

    
    def belongs_to_joint(self, new_subjoint: subjoint.SubJoint) -> bool:
        """Determines if a subjoint belongs to the horizontal joint. Checks if
        new subjoint has a y1 or y2 value that is within 100 pixels of the range
        of the horizontal joint's current subjoints.


        Args:
            subjoint (SubJoint): subjoint to check

            
        Returns:
            bool: True if the subjoint belongs to the horizontal joint, False
            otherwise
        """

        # no subjoints added yet
        if not self.subjoints:
            return True

        y_max = self.get_max_y()
        y_min = self.get_min_y()
        return (y_min - 25 <= new_subjoint.y1 <= y_max + 25 
                or y_min - 25 <= new_subjoint.y2 <= y_max + 25)
            
    

    def get_max_y(self) -> int:
        """Gets the maximum y value of the horizontal joint.

        
        Returns:
            int: maximum y value of the horizontal joint
        """
        return max(max([subjoint.y2 for subjoint in self.subjoints]), 
                   (max([subjoint.y1 for subjoint in self.subjoints])))
    

    def get_min_y(self) -> int:
        """Gets the minimum y value of the horizontal joint.

        
        Returns:
            int: minimum y value of the horizontal joint
        """
        return min(min([subjoint.y2 for subjoint in self.subjoints]),
                   (min([subjoint.y1 for subjoint in self.subjoints])))


    def get_max_x(self) -> int:
        """Gets the maximum x value of the horizontal joint.

        
        Returns:
            int: maximum x value of the horizontal joint
        """
        return max(max([subjoint.x2 for subjoint in self.subjoints]),
                   (max([subjoint.x1 for subjoint in self.subjoints])))
    

    def get_min_x(self) -> int:
        """Gets the minimum x value of the horizontal joint.

        
        Returns:
            int: minimum x value of the horizontal joint
        """
        return min(min([subjoint.x2 for subjoint in self.subjoints]),
                   (min([subjoint.x1 for subjoint in self.subjoints])))
    
    
    def get_bottom_img_id(self, num_images: int, img_size: int):
        """Gets the image id of the bottom of the horizontal joint.

        
        Args:
            num_images (int): number of images in the segment
            img_size (int): size (length from top to bottom in px) 
            of the input images

            
        Returns:
            int: image id of the bottom of the horizontal joint
        """
        return num_images - 1 - int(self.get_max_y()) // img_size
    

    def get_midpoint_img_id(self, num_images: int, img_size: int):
        """Gets the image id of the midpoint of the horizontal joint.

        
        Args:
            num_images (int): number of images in the segment
            img_size (int): size (length from top to bottom in px) of the input 
            images

        Returns:
            int: image id of the midpoint of the horizontal joint
        """
        return num_images - 1 - int(self.get_y_midpoint()) // img_size
    

    def get_top_img_id(self, num_images: int, img_size: int):
        """Gets the image id of the top of the horizontal joint.

        
        Args:
            num_images (int): number of images in the segment
            img_size (int): size (length from top to bottom in px) of the input 
            images

            
        Returns:
            int: image id of the top of the horizontal joint
        """
        return num_images - 1 - int(self.get_min_y()) // img_size
        
    
    def get_y_midpoint(self) -> int:
        """Gets the y-value of the midpoint of the horizontal joint.

        
        Returns:
            int: y-value of the midpoint of the horizontal joint
        """
        return (self.subjoints[-1].y2 + self.subjoints[0].y1) // 2
    


    def __str__(self):
        s = ''
        for subjoint in self.subjoints:
            s += str(subjoint) + '\n'
        return s
