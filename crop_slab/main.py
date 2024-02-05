import argparse
import os
from crop_slab.crop_slab_image import CropSlabs
from crop_slab.continuous_range import ContinuousRange

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

    func, dir, size, unit, mode = list(vars(parser.parse_args()).values())

    if func not in {"crop-slabs", "detect-joints"}:
        raise ValueError("Please enter a valid function name.")

    if os.path.isdir(dir):
        if not os.path.isdir(os.path.join(dir, "Range"))\
                or not os.path.isdir(os.path.join(dir, "XML")):
            raise ValueError(
                "'Range' or 'XML' subdirectory could not be found in provided directory."
            )
    else:
        raise ValueError("Data source directory could not be found.")

    if size <= 0:
        raise ValueError("Please enter a valid image size.")

    if unit not in {"px", "mm"}:
        raise ValueError("Please enter a valid unit.")

    if len(mode) > 2:
        raise ValueError("Mode argument can only have two or less values")

    if func == "crop-slabs":
        cs = CropSlabs(dir, size, unit, mode)
