.. _changelog-page:

Change Log
=================================

**v1.0.0b2**


**v1.0.0b1**

- Added a menu option to save a settings file prior to starting the analysis.
- Current threshold is now defined by an ionic current. The trajectory viewer displays the deviation of the threshold from the mean current.
- Analysis settings are saved within the analysissettings table of the sqlite database. When an analysis database is loaded into the GUI, settings are parsed from within the database.
- When an analysis file is loaded, widgets in the main window remain enabled. This allows starting a new analysis run with the current settings.
- Implemented an analysis log viewer that displays the event processing log.
- Initial commit of wavelets based peak detection in blockdepthview.
- Added all points histogram to trajectory viewer. 

*Known Issues:*

- Selecting automatic baseline detection can sometimes cause the threshold in the trajectory viewer to change. Moving the slider will cause the settings and trajectory windows to synchronize.