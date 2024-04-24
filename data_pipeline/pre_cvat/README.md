# Changelog
## [1.1.0] - 2024-03-30
* Additions
    * Subjoint data, including faulting data, is stored in MongoDB, as well as image metadata. 
## [1.0.1] - 2024-02-24
* Additions
    * A new feature was added to optionally specify the task size. This would split the images, as well as its corresponding annotations, into multiple zip folders for distribution to be run locally. 
* Fixes
    * Vertical joints are no longer added to the annotations file since LCMS inaccurately detects them.
## [1.0.0] - 2024-02-17
* Initial release. 
