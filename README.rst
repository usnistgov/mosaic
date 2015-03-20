MOSAIC: A modular single-molecule analysis interface
=================================


MOSAIC is a single molecule analysis toolbox that automatically decodes multi-state nanopore data. By modeling the nanopore system with an equivalent circuit, MOSAIC leverages the transient response of a molecule entering the channel to quantify pore-molecule interactions. In contrast to existing techniques such as ionic current thresholding or Viterbi decoding, this technique allows the estimation of short-lived transient events that are otherwise not analyzed.

Nanometer-scale pores have demonstrated potential use in biotechnology applications, including DNA sequencing, single-molecule force spectroscopy, and single-molecule mass spectrometry. The data modeling and analysis methods implemented in MOSAIC allow for dramatic improvements in the quantification of molecular interactions with the channel in each of these applications.

**If you use MOSAIC in your work, please cite:**

\A. Balijepalli, J., Ettedgui, A. T. Cornio, J. W. F. Robertson K. P. Cheung, J. J. Kasianowicz & C. Vaz, "`Quantifying Short-Lived Events in Multistate Ionic Current Measurements. <http://pubs.acs.org/doi/abs/10.1021/nn405761y>`_" *ACS Nano* 2014, **8**, 1547–1553.


Installation
=================================

Please refer to the `Installation <https://usnistgov.github.io/mosaic/html/doc/GettingStarted.html>`_ section of the MOSAIC documentation for details on installation.


Getting Help
=================================

For questions and help, please join our `mailing list <https://usnistgov.github.io/mosaic/html/doc/mailingList.html>`_. 

To subscribe:

	Email `mosaic-request@nist.gov <mailto:mosaic-request@nist.gov?subject=subscribe>`_ with subject 'subscribe'

To unsubscribe:

	Email `mosaic-request@nist.gov <mailto:mosaic-request@nist.gov?subject=unsubscribe>`_ with subject 'unsubscribe'

Once subscribed, you can send messages by emailing `mosaic@nist.gov <mailto:mosaic@nist.gov>`_.


Reporting Problems
=================================

Report problems using our `issue tracker <https://github.com/usnistgov/mosaic/issues>`_ on Github.


Change Log
=================================

**v1.3**

- Added CUSUM algorithm (see pull request #34, #43)
- [GUI] Added CUSUM support to MOSAIC GUI.
- [GUI] Fit window in MOSAIC GUI displays idealized pulses overlays.
- [Addons] Added CUSUM support to Mathematica addon (PlotEvents in MosaicUtils.m)
- Added a new metadata column (mdStateResTime) that saves the residence time of each state to the database. This affects multiStateAnalysis and cusumLevelAnalysis.
- Removed mosaicgui from PyPi. 'pip install mosaic-nist' only installs command line modules. 
- Top level ConvertToCSV supports arbitrary file extensions.
- Fixes issues #36 and #37.
- Known Issues: See #8 and #10.

**v1.2**

- Added support for arbitrary binary file formats (#33)
- [GUI] Included binary file support.
- Documentation updates and bug fixes.
- *Known Issues:* See #8 and #10.

**v1.1**

- [Addons] IGOR_ support.
- PyPi package automatically installs MOSAIC dependencies.
- Miscellaneous bug fixes.
- *Known Issues:* See #8 and #10.

**v1.0**

- Fixed a bug in multistate code that constrained the RC constant resulting in systematic fitting errors (pull request #25).
- Updated multistate to include a separate RC constant for each state, to be consistent with functional form in Balijepalli et al., ACS Nano 2014.
- Misc bug fixes in tsvTrajIO parsing.
- The number of states is saved to the MDIO DB for multistate analysis (issue #26).
- Created a new package on PyPI (mosaic-nist) to allow installation with setuptools.
- [GUI] Updated help link to point to Sphinx documentation on Github.
- *Known Issues:* See #8 and #10 

**v1.0b3.2**

- [GUI] Misc bug fixes
- [Addons] Added code to import MOSAIC output into Matlab (pull requests #18 and #20)
- [Addons] Updated Mathematica addons to automatically decode multi-state data.
- Resolves issues #16 and #22

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


**v1.0b2**

- [GUI] Fixed threshold update error from 1.0b1.
- Considerably improved automatic open channel state detection.
- The default settings string is now included within the source code.
- Implemented new top-level class ConvertToCSV that allows conversion of data read by any TrajIO object to comma separated files.
- Updated build system and unit testing framework.
- [GUI] Misc UI updates.


**v1.0b1**

- [GUI] Added a menu option to save a settings file prior to starting the analysis.
- [GUI] Current threshold is now defined by an ionic current. The trajectory viewer displays the deviation of the threshold from the mean current.
- Analysis settings are saved within the analysissettings table of the sqlite database. When an analysis database is loaded into the GUI, settings are parsed from within the database.
- When an analysis file is loaded, widgets in the main window remain enabled. This allows starting a new analysis run with the current settings.
- [GUI] Implemented an analysis log viewer that displays the event processing log.
- [GUI] Initial commit of wavelets based peak detection in blockdepthview.
- [GUI] Added all points histogram to trajectory viewer. 
- *Known Issues:* Selecting automatic baseline detection can sometimes cause the threshold in the trajectory viewer to change. Moving the slider will cause the settings and trajectory windows to synchronize.
