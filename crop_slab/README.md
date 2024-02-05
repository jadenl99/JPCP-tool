# replaced-slab-detection
Originally created by Aditya Tapshalkar

Improvements by Jaden Lim

___
1.) University of California Pavement Research Center (UCPRC) data processing and You Only Look Once (YOLOv5) model generation
* `ucdavis-data.csv`: CSV record of joints supplied by UCPRC
* `data_collection.ipynb`: Jupyter Notebook script for aggregate and splitting of UCPRC joint images and data into training and testing datasets, and generation of YOLO annotated `.txt` files
  * Important features: joint image, replaced slab ground truth (`ucprc_isr_ahead`)
* YOLOv5 (https://github.com/ultralytics/yolov5) found in Microsoft Teams "Code Deliverable" directory
  * Configuration: `data=slab.yaml; epochs=300; image_size=320; batch_size=16; device=NVIDIA GeForce RTX 2070 SUPER`
  * Results found in `YOLO_results` folder
  
2.) LinearSVM Model with Georgia Tech's LCMS data
  * Data includes MP18-17 and MP22 Range and Intensity image data
  * `crop_slab_image.py`: Refined slab cropping code, using a sliding window technique while iterating through XML files
  * `LinearSVM-model` folder contains data processing and SVM model generation techniques
    * `slab_data` contains manually-generated ground truth annotations for processed slabs (1 for replaced slab; 0 for unreplaced slab; -1 for improperly cropped slab)
    * `slab-analysis.ipynb`: Experimenting with unreplaced/replaced slab differentiation, using techniques such as Gaussian filtering and Local Binary Patterning; generation of `all_inputs_gts.csv` file for slab image features after processing, including slab length and histogram data
    * `slab-classification.ipynb`: Testing and tuning of LinearSVC model from Scikit-learn on replaced slab classification and analysis of LinearSVC model accuracy metrics 

___
Directions for running code:
* UCPRC data with YOLOv5:
  * Run `data_collection.ipynb`
  * Download `yolov5` folder from Microsoft Teams; ensure `train`, `val`, and `test` paths in `slab.yaml` point to `train` and `test` folders generated from `data_collection.ipynb`
  * `cd` into `yolov5` folder; run `python train.py --data slab.yaml --batch-size 16 --epochs 300 --device 0 --img 320 --weights yolov5s.pt`
  * To test the model after training, run `python val.py --task test --data slab.yaml --device 0 --weights runs/train/{exp#}/weights/best.pt`

* Georgia Tech data with LinearSVC:
  * Run `python main.py -f crop-slabs -d {path-to-data}` on both MP18-17 and MP22 datasets
  * Manually create ground truth CSV files classifying each extracted slab image as unreplaced (0)/replaced (1)/faulty (-1)
  * Run `slab-analysis.ipynb` to generate CSV file from slab length and histogram data
  * Run `slab-classification.ipynb` to create and train LinearSVC model, and determine best hypertuning parameters and metrics analysis with Scikit-learn
* To crop both range and intensity images:
  * To install dependencies, run `pip install -r requirements.txt`.
  * Run `python main.py -f crop-slabs -d {path-to-data} --mode range intensity`
  * Ensure the range and intensity images are included in the `Range` and `Intensity` folders, respectively. Also ensure the manual XML data to read from is included in the `XML` folder.

# Changelog

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
