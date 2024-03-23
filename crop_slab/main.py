import argparse
import os
from crop_slab.crop_slab_cvat import CropSlabsCVAT
from crop_slab.crop_slab_image import CropSlabs

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Slab detection project for Georgia Tech Smart Cities Lab\n'
                    'Fall 2021, Aditya Tapshalkar' 
    )

    parser.add_argument('-f',
                        metavar='<function>',
                        type=str,
                        # default='crop-slabs',
                        required=True,
                        help='Function to run ("crop-slabs" | "detect-joints")')

    parser.add_argument('-d',
                        metavar='<filepath>',
                        type=str,
                        required=True,
                        help='Directory of XML and Range image data')

    parser.add_argument('--size',
                        metavar='<image size>',
                        type=int,
                        default=1250,
                        help='Size of images')

    parser.add_argument('--unit',
                        metavar='<size units>',
                        type=str,
                        default='px',
                        help='Units of image size ("mm" | "px")')

    parser.add_argument('--mode',
                        metavar='<cropping mode>',
                        choices=['range', 'intensity'],
                        nargs='*',
                        type=str,
                        default=['range'],
                        help='Image layer to process ("range" | "intensity")')
    
    parser.add_argument('-o',
                        action='store_true', 
                        help='Whether to use the old version or not')
    
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
                        metavar='<interstate>',
                        type=str,
                        required=True,
                        help='Interstate of data (eg. I16WB)')
    

    func, dir, size, unit, mode, o, begin_MM, end_MM, year, interstate = list(vars(parser.parse_args()).values())
    begin_MM = int(begin_MM)
    end_MM = int(end_MM)
    year = int(year)

    if func not in {"crop-slabs", "detect-joints"}:
        raise ValueError("Please enter a valid function name.")

    if size <= 0:
        raise ValueError("Please enter a valid image size.")

    if unit not in {"px", "mm"}:
        raise ValueError("Please enter a valid unit.")

    if len(mode) > 2:
        raise ValueError("Mode argument can only have two or less values")


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
    
    if func == "crop-slabs" and o:
        cs = CropSlabs(dir, size, unit, mode, begin_MM, end_MM, year, interstate)
    else:
        cs = CropSlabsCVAT(dir, size, unit, mode, begin_MM, end_MM, year, interstate)
