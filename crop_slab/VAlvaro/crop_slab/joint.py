import sys

from crop_slab import subjoint
class HorizontalJoint:
    """A horizontal joint is a joint that spans from the left boundary of the
    lane to the right boundary of the lane. Joints need not be parallel to the
    horizontal plane. A horizontal joint can possibly be diagonal, as long as
    it satisfies the condition in the first sentance. Each horizontal joint is
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
        """Determines if a subjoint belongs to the horizontal joint. There are 
        three cases that occur:

        1. The subjoint to be added is directly right of the current rightmost
        subjoint of the horizontal joint.

        2. The subjoint to be added is directly left of the current leftmost
        subjoint of the horizontal joint. 

        3. The subjoint is nowhere near the other subjoints of the horiziontal
        joint of interest. 


        Args:
            subjoint (SubJoint): subjoint to check

            
        Returns:
            bool: True if the subjoint belongs to the horizontal joint, False
            otherwise
        """

        # no subjoints added yet
        if not self.subjoints:
            return True
        
        # subjoint is directly right of current the rightmost subjoint
        if abs(new_subjoint.y1 - self.subjoints[-1].y2) <= 100:
            return True
        
        # subjoint is directly left of the current leftmost subjoint
        if abs(new_subjoint.y2 - self.subjoints[0].y1) <= 100:
            return True
        
        return False
    

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
    
    
    def get_bottom_img_id(self, base_id: int, img_size: int):
        """Gets the image id of the bottom of the horizontal joint.

        
        Args:
            base_id (int): image id of the first image
            img_size (int): size (length from top to bottom) of the input images

            
        Returns:
            int: image id of the bottom of the horizontal joint
        """
        return base_id + int(self.get_min_y()) // img_size
    

    def get_top_img_id(self, base_id: int, img_size: int):
        """Gets the image id of the top of the horizontal joint.

        
        Args:
            base_id (int): image id of the first image
            img_size (int): size (length from top to bottom) of the input images

            
        Returns:
            int: image id of the top of the horizontal joint
        """
        return base_id + int(self.get_max_y()) // img_size
        
    
    def __str__(self):
        s = ''
        for subjoint in self.subjoints:
            s += str(subjoint) + '\n'
        return s
