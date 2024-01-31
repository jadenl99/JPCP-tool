import math
class SubJoint:
    def __init__(self, x1: int, y1: int, x2: int, y2: int, dist: int=None):
        """A SubJoint is a line segment, defined by two endpoints, that is part
        of a HorizontalJoint.

        Coordinate pairs can be passed in any order, but in the SubJoint data 
        field, the first coordinate pair is always the leftmost.

        Args:
            x1 (int): x-value of the first coordinate pair
            y1 (int): y-value of the first coordinate pair
            x2 (int): x-value of the second coordinate pair
            y2 (int): y-value of the second coordinate pair
            dist (int, optional): Distance between the two coordinates.
            Defaults to None.

        Raises:
            ValueError: If the distance between the two coordinates is zero.
        """

        # first coordinate pair is always the leftmost
        if x1 <= x2:
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2
        else:
            self.x1 = x2
            self.y1 = y2
            self.x2 = x1
            self.y2 = y1
        
        if (self.x1 == self.x2) and (self.y1 == self.y2):
            raise ValueError("Subjoint cannot have zero length.")
        
        if dist is None:
            dist = math.hypot(self.x2 - self.x1, self.y2 - self.y1)
            dist = round(dist, 2)
        
        self.dist = dist

    def __str__(self):
        return f"({self.x1}, {self.y1}), ({self.x2}, {self.y2})"