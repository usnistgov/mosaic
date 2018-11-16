Change Log
++++++++++++++++++++++++++++++++++++++++++

**v2.0b2**

- Fixed an issue where spurious events were detected that were contained entirely within the open channel current (see `#102 <https://github.com/usnistgov/mosaic/issues/102>`_).
- Added detailed Windows build instructions.

**v2.0b1**

- Run MOSAIC using a new web interface.

**v1.3.6**

- Bug Fixes

**v1.3.5**

- Saves raw events in database. Resolves `#93 <https://github.com/usnistgov/mosaic/issues/93>`_.

**v1.3.4**

- Fixed a bug in the default settings that prevented the analysis from starting in some instances.

**v1.3.3**

- Added support for Chimera data files.
- Resolves issues `#92 <https://github.com/usnistgov/mosaic/issues/92>`_ and `#95 <https://github.com/usnistgov/mosaic/issues/95>`_. 

**v1.3.2**

- Fixed event partiioning bugs.
- [GUI] UI tweaks.

**v1.3.1**

- Bug fix release.

**v1.3**

- Added a new MOSAIC examples repository that contains plotting scripts and Jupyter notebooks (https://github.com/usnistgov/mosaic-examples)

- Updated Bessel fiter implementation to allow causal and non-causal filters.
- Added the CUSUM+ algorithm (see pull requests #34, #43, #45, and #46)
- Added the ability to read arbitrary binary files.
- Renamed StepResponseAnalysis to ADEPT 2-state.
- Renamed multiStateAnalysis to ADEPT.
- CUSUM+ is now used to generate initial guesses for ADEPT
- Streamlined unit test framework. Added new tests for CUSUM+.
- Updated MOSAIC dependencies to include newer package versions and pandas. Run 'python setup.py mosaic_deps' to update.
- Added a new metadata column (mdStateResTime) that saves the residence time of each state to the database. This affects ADEPT and CUSUM+.
- Processing time per event is now saved to the database.
- Added support for warning status codes that begin with 'w'. These codes preserve metadata in the SQLite output and are used to flag events that need closer inspection.
- Removed mosaicgui from PyPi. 'pip install mosaic-nist' only installs command line modules. 
- Top level ConvertTrajIO supports binary and ASCII files.
- Added Travis continous integration support.
- [GUI] Added a binary update service for Windows and OS X.
- [GUI] Added a table that displays fit parameters in the event viewer window.
- [GUI] Added more descriptive fit errors.
- [GUI] Added CUSUM+ support to MOSAIC GUI.
- [GUI] Export SQLITE database to CSV (#56).
- [GUI] Support for warning codes in fit event viewer.
- [GUI] Performance optimizations.
- [GUI] Fit window in MOSAIC GUI displays idealized pulses overlays.
- [GUI] Added additional analysis statistics.

- [Addons] Added CUSUM+ support to Mathematica addon (PlotEvents in MosaicUtils.m)
- [Addons] Mathematica queries are *optionally* handled through an external Python script to improve performance.
- [Addons] Added an option to limit PlotEvents in Mathematica addon to N events.

- Known Issues: See #8, #10, #40, #63 and #69.

**v1.2**

- Added support for arbitrary binary file formats (#33)
- [GUI] Included binary file support.
- Documentation updates and bug fixes.
- *Known Issues:* See #8 and #10.

**v1.1**

- [Addons] IGOR support.
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
