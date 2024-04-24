# Changelog
## [2.2.1] - 2024-04-23
* Additions
  * Median faulting values for each zone are now stored in the database. 
  * Outlier detection implemented for faulting values and other statistics for faulting are computed for each slab.
* Fixes
  * Debug file to check joints is now in CSV format.
## [2.2.0] - 2024-03-30
* Additions
  * Data is stored in MongoDB. For now, there is only support to connection to the default local MongoDB server.
  * Faulting values are now automatically calculated. For now, averages of faulting values along wheelpath of the bottom joint for each slab are used for each slab.
  * Debug.txt file outputs full joints that are less than 2.75m, since it is impossible to have a lanewidth smaller than that.
  * Major refactoring done to modularize code.
* Fixes
  * Better cropping along lanemarkers. Uses bottom of the joint instead of lanemarker annotations, which may be inaccurate.
* Deletions
  * Removed support for Crack Digitzer. Now only supports CVAT annotations.
## [2.1.0] - 2024-02-27
* Additions
  * Can now support modified annotations from CVAT. Data extraction from ManualXML files might be sunset soon once the new pipeline is working.
## [2.0.2] - 2024-02-17
* Fixes
  * Zero length subjoints would halt the program. Now subjoints that are too small in length are ignored.
## [2.0.1] - 2024-02-04
* Additions
  * Add support to simutaneously crop range and intensity images
* Fixes
  * y-offset and length on slabs.csv were calculated incorrectly for each slab. This has been fixed.
* Removed
  * Input images are not scaled up anymore to correspond to the slab's dimensions in mm before cropping. Cropping is now done on the original input image's dimensions to improve runtime of the program and to save space for the output files. 
## [2.0.0] - 2024-01-31
* Additions
  * The lower and upper corners that do not belong to the slab of interest are blackened out.
  * y_min and y_max information displays on the slabs.csv file.
* Fixes
  * Previously, the slabs were cropped at the midpoint of both the bottom and top joints, resulting in the loss of information on the corners of slabs. The slab cropper now crops at the y_min and y_max of the bottom and top slabs, respectively.
  * Output images were previously saved in png format, which took up too much space. Output images are now saved to jpg format to match the format of input images.