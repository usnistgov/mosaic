MOSAIC: A modular single-molecule analysis interface
=================================


MOSAIC is a single molecule analysis toolbox that automatically decodes multi-state nanopore data. By modeling the nanopore system with an equivalent circuit, MOSAIC leverages the transient response of a molecule entering the channel to quantify pore-molecule interactions. In contrast to existing techniques such as ionic current thresholding {REFS} or Viterbi decoding {REFS}, this technique allows the estimation of short-lived transient events that are otherwise not analyzed.

Nanometer-scale pores have demonstrated potential use in biotechnology applications, including DNA sequencing {REFS}, single-molecule force spectroscopy {REFS}, and single-molecule mass spectrometry {REFS}. The data modeling and analysis methods implemented in MOSAIC allow for dramatic improvements in the quantification of molecular interactions with the channel in each of these applications.

MOSAIC is written in Python and developed in the Semiconductor and Device Metrology (`SDMD <http://www.nist.gov/pml/div683/about.cfm>`_) division, in the Physical Metrology Laborotory (`PML <http://www.nist.gov/pml/>`_) at the National Institute of Standards and Technology (`NIST <http://www.nist.gov>`_).

**If you use MOSAIC in your work, please cite:**

A. Balijepalli, J., Ettedgui, A. T. Cornio, J. W. F. Robertson K. P. Cheung, J. J. Kasianowicz & C. Vaz, "`Quantifying Short-Lived Events in Multistate Ionic Current Measurements. <http://pubs.acs.org/doi/abs/10.1021/nn405761y>`_" *ACS Nano* 2014, **8**, 1547–1553.



What's new in v1.0b3
=================================

**v1.0b3.1**

- [GUI] Added multiState support to mosaicgui.
- Analysis information such as alogirthms used, data type, etc. are now stored within a MDIO database.
- [GUI] Autocomplete in mosaicgui only suggests database columns that are valid when used in a query.
- Reorganized Mathematica addon code.


**v1.0b3**

- Fixed a bug that prevented events longer than ~700 data points from being correctly analyzed.
- Fixed a problem that prevented event data from being correctly padded before analysis.
- Resolves #2. TrajIO settings are now read in from the settings file.
- [GUI] Resolves #3. Threshold entry box in GUI becomes nonresponsive when meanOpenCurr is negative.
- [GUI] Resolves #4. Analysis fails when using wavletDenioseFilter from GUI.
- [GUI] Histogram in BlockDepthViewer window can be saved to a CSV file from the File Menu.
- Analysis log is saved to the MDIO database.
- [GUI] ConsoleLogViwer displays the analysis log saved in the MDIO database.
- [GUI] Added a new dialog that displays an experimental feature warning wavelet-based denoising is selected.
- Updated error codes reported in database to be more descriptive of the failure.
- Improved and expanded unit testing framework.
- Moved installation and testing to setuptools.

