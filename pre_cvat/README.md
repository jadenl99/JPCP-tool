# LCMS XML to CVAT Annotations for Manual Joint Editing
Jaden Lim  
Georgia Institute of Technology  
Smart City Infrastructure  
## Overview
The XML to CVAT parsers will take the LCMS data and create an annotations file that can be easily inputted to CVAT. In addition, the parser looks through other fields in the LCMS data, like faulting values, and store it into the database. Run this script for each year of data for the segment, then annotate the joints in CVAT, and feed the fixed annotations into the slab cropping application.
## Running the Program
On the root directory of this application, run in the command line:  
`python main.py -d <path_to_ALL_data> -i <interstate> -b <begining MM> -e <ending MM> -y <year>` 
An example command line call for the I-16 WB segment for MM 22-12 is: 
`python main.py -i I16WB -b 22 -e 12 -y 2014 -d data/2014`.
Ensure the folder with all the data contains the XML folder, which should contain all the XML files from the LCMS output, as well as the range/intensity folders. The file structure of the data should look something like this after running LCMS roadinspect. 
```
├───<year>  
|  ├───Intensity  
|  ├───Range  
|  └───XML  
```
To optionally partition the dataset into multiple tasks to distribute to others, run the command with the additional argument `--tasksize <number>`.  

After running the program, the folder `CVAT_data` should be created, and inside contains one or more zip files that can be fed into CVAT.


# Changelog
## [1.1.0] - 2014-03-30
* Additions
    * Subjoint data, including faulting data, is stored in MongoDB, as well as image metadata. 
## [1.0.1] - 2024-02-24
* Additions
    * A new feature was added to optionally specify the task size. This would split the images, as well as its corresponding annotations, into multiple zip folders for distribution to be run locally. 
* Fixes
    * Vertical joints are no longer added to the annotations file since LCMS inaccurately detects them.
## [1.0.0] - 2024-02-17
* Initial release. 

