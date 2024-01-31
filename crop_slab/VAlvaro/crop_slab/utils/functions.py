class LinearFunction:
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        """A linear function is defined by two points, (x1, y1) and (x2, y2). 

        Args:
            x1 (int): x-value of the first point
            y1 (int): y-value of the first point
            x2 (int): x-value of the second point
            y2 (int): y-value of the second point
        """
        self.slope = (y2 - y1) / (x2 - x1)
        self.intercept = y1 - self.slope * x1
    

    def get_y(self, x: int) -> int:
        """Gets the y-value of the linear function at a given x-value.

        Args:
            x (int): x-value

        Returns:
            int: y-value of the linear function at x
        """
        return self.slope * x + self.intercept
    

    def __str__(self):
        return f"y = {self.slope}x + {self.intercept}"