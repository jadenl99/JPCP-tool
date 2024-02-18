import argparse
import os
from pre_cvat.parser import XML_CVAT_Parser
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate CVAT XML files so annotations from the crack digitizer can be loaded' 
    )

    parser.add_argument('-d',
                        metavar='<filepath>',
                        type=str,
                        required=True,
                        help='Directory where the XML and pictures reside')

    parser.add_argument('--pxheight', 
                        metavar='<height in pixels>',
                        type=int,
                        default=1250,
                        help='Height of the images in pixels')
    
    parser.add_argument('--pxwidth', 
                        metavar='<width in pixels>',
                        type=int,
                        default=1040,
                        help='Width of the images in pixels')
    
    parser.add_argument('--mmheight', 
                        metavar='<height in mm>',
                        type=int,
                        default=5000,
                        help='Height of the images in millimeters')
    
    parser.add_argument('--mmwidth', 
                        metavar='<width in mm>',
                        type=int,
                        default=4160,
                        help='Width of the images in millimeters')
    
    parser.add_argument('--mode',
                        metavar='<cropping mode>',
                        choices=['range', 'intensity'],
                        type=str,
                        default='range',
                        help='Image layer to annotate ("range" | "intensity")')
    
    dir, pxh, pxw, mmh, mmw, type = list(vars(parser.parse_args()).values())

    if os.path.isdir(dir):
        if not os.path.isdir(os.path.join(dir, type))\
                or not os.path.isdir(os.path.join(dir, "XML")):
            raise ValueError(
                "'Image' or 'XML' subdirectory could not be found in provided directory."
            )
    else:
        raise ValueError("Data source directory could not be found.")
    
    if pxh <= 0 or mmh <= 0:
        raise ValueError("Please enter a valid image size.")
    
    XML_CVAT_Parser(dir, pxh, pxw, mmh, mmw, type)