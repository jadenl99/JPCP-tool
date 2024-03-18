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
    
    parser.add_argument('--tasksize',
                        metavar='<number of images per task>',
                        type=int,
                        default=100000000000,
                        help='Number of images per task')
    
    parser.add_argument('-b',
                        metavar='<beginning MM>',
                        type=str,
                        required=True,
                        help='begining MM of the segment')
    
    parser.add_argument('-e',
                        metavar='<ending MM>',
                        type=str,
                        required=True,
                        help='ending MM of the segment')

    parser.add_argument('-y', 
                        metavar='<year>',
                        type=int,
                        required=True,
                        help='Year of the data')
    
    parser.add_argument('-i', 
                        metavar='<Interstate highway>',
                        type=str,
                        required=True,
                        help='Interstate highway of the data (eg. I16WB)')
    
    dir, pxh, pxw, mmh, mmw, type, tasksize, begin_MM, end_MM, year, interstate\
        = list(vars(parser.parse_args()).values())
    
    begin_MM = int(begin_MM)
    end_MM = int(end_MM)
    year = int(year)

    if os.path.isdir(dir):
        if not os.path.isdir(os.path.join(dir, type))\
                or not os.path.isdir(os.path.join(dir, "XML")):
            raise ValueError(
                "'Image' or 'XML' subdirectory could " 
                + "not be found in provided directory."
            )
    else:
        raise ValueError("Data source directory could not be found.")
    
    if tasksize <= 0:
        raise ValueError("Please enter a valid task size.")
    
    if pxh <= 0 or mmh <= 0:
        raise ValueError("Please enter a valid image size.")
    
    if begin_MM < 0 or end_MM < 0:
        raise ValueError("MM cannot be negative")
    
    if len(str(year)) != 4 or year < 0:
        raise ValueError("Please enter a valid year.")
    
    if ('EB' not in interstate 
        and 'WB' not in interstate 
        and 'NB' not in interstate 
        and 'SB' not in interstate):
        raise ValueError("Please specify direction of interstate highway \
                         (eg. I16WB)")
    
    XML_CVAT_Parser(dir, pxh, pxw, mmh, mmw, type, tasksize, begin_MM,
                    end_MM, year, interstate)