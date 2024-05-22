# LCMS Data Processing Pipeline
Jaden Lim 

Smart City Infrastructure Lab 

Spring 2024 Improvement Project  

## Overview 
Given the LCMS XML files and processed range and intensity images, a slab inventory for a specific segement, as well as useful data that can be used for can be created using this application. The pipeline is split into subapplications, the first one being the `pre_cvat` application, which extracts XML data, the second one being the  `crop_slab` application, which crops images, and the third being `registration`, which actually creates the slab inventory. All these subapplications can be run in the root directory of `data_pipeline`. 

## Setting Up the File System for all Data
Your data folder should initially look something like this, which will serve as input for the pipeline application:
```
├───<data>
│   ├───2014
│   │   └───Range
│   │   └───Intensity
│   │   └───XML
|   |   └───CVAT_output
│   ├───2015
│   ├───2016
│   ├───... (continue with all the years to register)
```
with your `<data>` folder (which you can name it anything you want) containing all your data for the segment of interest that you are interested in preparing. The `<data>` folder should have many subfolders, one for each year in the format `XXXX`, and each year should contain folders containing all the XML data, Intensity, and Range images. Create a new empty folder called `CVAT_output` for each year.

## Step 1: Extracting LCMS XML Data 
### Input 
Set up the file system as follows above. 
### Output 
Creates zip files to feed into the CVAT application. These zip files will be under a newly created folder under `CVAT_data` in the `year` folders that the script is run on. Also stores image metadata and faulting information for each joint into the database. 
### Instructions for Running 
* On the root directory of this application, run in the command line for each year:  
  * `python xml_parse.py -d <path_to_data> -i <interstate> -b <begining MM> -e <ending MM> -y <year>` 
* Note that `<path_to_data>` should not be the `<year>` subdirectory - it should be the path to the folder containing all the segment data. 
* If you want to get a `debug.csv` file to selectively annotate joints that might be incorrectly identified, run the above command first, then unzip the zip file and copy the generated `annotations.xml` file into the `CVAT_output` file for the year you are interested in annotating, then run:
  * `python cropapp.py -f validation-only -d <path_to_data> -i <interstate> -b <begining MM> -e <ending MM> -y <year>` 
* Refer to the Slab Boundary Annotation Guideline document for information on how to verify joints before proceeding to step 2. 

## Step 2: Slab Cropping 
### Input 
For each year, the necessary inputs are
```
├───<year>
│   ├───CVAT_output
│   │   └───annotations.xml
│   ├───Intensity
│   ├───Range
``` 
Note that the `annotations.xml` file generated after CVAT modifications should go under the `CVAT_output` folder. 
### Output
In the specified `<year>` folder, a `Slabs` folder will be created/overriden with the cropped range and/or intensity images. A `debug.csv` file indicating joints to be fixed in CVAT as well as a `slabs.csv` file that contains slab data will be generated. In addition, data for each slab, such as slab length, y-offset, faulting values, etc. will be stored in the database. 
### Instructions for Running
* Run `python cropapp.py -f crop-slabs -d <path-to-data> -b <beginMM> -e <endMM> -i <interstate> -y <year> --mode range intensity`. The interstate argument should be formated like `I16WB`, include direction as well. Run this for each year in the segment.
  * If you only want to crop the range or intensity, drop `range` or `intensity`.
* If you only want to validate the joints are correctly annotated, run the function `-f validation-only` instead. Note that the check for the joints is not comprehensive. 

## Step 3: Slab Registration 
### Input 
There is no input, other than the connection to the database. 
### Output 
Registration data will be stored in the database. 
### Instructions for Running 
* Run `python reg_slabs.py -b <beginMM> -e <endMM> -i <interstate> -d <directory to store spreadsheet output>` to associate BY and CY slab pairs if you have not done that yet for the segment. When this is done, or if the slab assoctiations have already been stored in the database, then go to the slab classification application and annotate those slabs.
* After, come back to the slab registration application. Run the same command again. Faulting values can be calculated in two ways:
  * If you add the `-a` flag, if there are are more than one CY slab for a BY slab, then faulting values will be averaged.
  * If not, then the faulting value of the largest contributor/overlapper CY slab will be taken.
  * Regardless of how the faulting value is calculated, the state of the largest contributor CY slab will be recorded.
* Follow the prompts to set up BY and start slabs. The slab ID input for starting slab refers to the slab images outputted by the slab cropping app. 



