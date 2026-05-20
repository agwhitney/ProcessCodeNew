# ProcessCodeNew
This package was written by Xavi Bosch-Lluis in 2014 to post-process data acquired by HAMMR. It takes Level 0b data (organized raw data) in the form of an HDF5.h5 file and outputs Level 1a data (two-point calibrated and integrated to an angular resolution), also in HDF5.h5 format. The original code can seemingly go to further levels of post-processing, but this is not supported here.

Prior to HAMMR-HD, this package was most recently? used for sounding channel data in the MiniMAC project. Only the microwave channels remain in HAMMR-HD. As written, the package required following a number of steps and applying some specific changes. This repo adds `newprocessor.py`, which wraps the entire procedure, and makes changes to the original code that primarily serve to improve clarity. Mostly this is taking advantage of `pathlib`, type hinting, and coding style. Some logic may be updated with this goal as well, and/or to keep support with updated packages such as `numpy`.


## Usage
Place .h5 files that will be used for two-point calibration (i.e., measurements of LN2-cooled absorber) in `L0bFiles/Calibration`, and the files that you would like calibrated in `L0bFiles/Data`. Running `newprocessor.py` should do everything else! There are three major steps, and the output will be placed in `Reader/Results`. The receiver calibration values are the result of the first two steps and will be placed in a .csv file in `Reader/Calibration`.

### Notes
1) This will NOT work with legacy HAMMR data because of changes to the `system.json` configuration file and to the HDF5 structure.
   * Appropriate loading methods and flattening of arrays could add compatability, likely with little effort.
2) A limitation of the legacy scripts requires at least three files for calibration.