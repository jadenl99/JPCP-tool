# LCMS XML to CVAT Annotations for Manual Joint Editing
Jaden Lim  
Georgia Institute of Technology  
Smart City Infrastructure  

## Running the Program
On the root directory of this application, run in the command line:  
`python main.py -d <path_to_data>`  
Ensure the folder with all the data contains the XML folder, which should contain all the XML files from the LCMS output, as well as the range/intensity folders. The file structure of the data should look something like this after running LCMS roadinspect. 
```
├───your_data_folder  
|  ├───Intensity  
|  ├───Range  
|  └───XML  
```
To optionally partition the dataset into multiple tasks to distribute to others, run the command with the additional argument `--tasksize <number>`.  

After running the program, the folder `CVAT_data` should be created, and inside contains one or more zip files that can be fed into CVAT.


# Changelog
## [1.0.1] - 2024-02-24
* Additions
    * A new feature was added to optionally specify the task size. This would split the images, as well as its corresponding annotations, into multiple zip folders for distribution to be run locally. 
* Fixes
    * Vertical joints are no longer added to the annotations file since LCMS inaccurately detects them.
## [1.0.0] - 2024-02-17
* Initial release. 

