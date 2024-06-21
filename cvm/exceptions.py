class MissingImageError(Exception):
    """Exception raised for errors when missing images.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str = "There is already input image!"):
        self.message = message
        super().__init__(self.message)


class RedundantImageError(Exception):
    """Exception raised for errors when both segmentation and range images are specified.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str = "Please use either segmentation or range image!"):
        self.message = message
        super().__init__(self.message)


class ExistedGeojsonObjectError(Exception):
    """Exception raised for errors when geojson object is already input.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str = "There is already input geojson object!"):
        self.message = message
        super().__init__(self.message)


class GeojsonFormatError(Exception):
    """Exception raised for errors when the geojson object is not in the expected format.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str = "The geojson object is not in the expected format!"):
        self.message = message
        super().__init__(self.message)


class MissingImageOrGeojsonError(Exception):
    """Exception raised for errors when missing either segmentation or geojson object.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message: str = "Missing either segmentation or geojson object as input!"):
        self.message = message
        super().__init__(self.message)
