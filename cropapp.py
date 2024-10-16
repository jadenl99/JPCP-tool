import argparse
from crop_app.crop_slab_cvat import CropSlabsCVAT
from database.db import SlabInventory
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
                        help='Function to run ("crop-slabs" | "validation-only" | "crop-only")')

    parser.add_argument('-d',
                        metavar='<filepath>',
                        type=str,
                        required=True,
                        help='Directory of XML and Range image data')

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
                        choices=['range', 'intensity', 'segmentation'],
                        nargs='*',
                        type=str,
                        default=['range'],
                        help='Image layer to process ("range" | "intensity | segmentation")')
    
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
    
    parser.add_argument('--overwrite',
                        default=False,
                        action='store_true',
                        help='delete segment entries in database before running')
    

    func, dir, pxh, pxw, mmh, mmw, mode, begin_MM, end_MM, year, interstate, overwrite = list(vars(parser.parse_args()).values())
    begin_MM = int(begin_MM)
    end_MM = int(end_MM)
    year = int(year)

    if func not in {"crop-slabs", "validation-only", "crop-only"}:
        raise ValueError("Please enter a valid function name.")

    
    if len(mode) > 3:
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

    v_only = False
    crop_only = False
    if func == "crop-slabs":
        response = input("Are you sure you want to update the database? Use '-f crop-only' if you only want to crop slabs. (Y/n): ")
        if response.lower() == 'y':
            pass
        else:
            exit()
    if func == "validation-only":
        v_only = True
    if func == "crop-only":
        crop_only = True
    CropSlabsCVAT(dir, pxh, pxw, mmh, mmw, mode, 
                  begin_MM, end_MM, year, interstate, 
                  SlabInventory(), overwrite, v_only, crop_only)
