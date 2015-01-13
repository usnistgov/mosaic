.. _igor-addons-sec:

IGOR
---------------------------------

Data extraction in IGOR_ is a work in progress, but a number of users have found a successful route to queerying the data and manipulating it in the IGOR_ environment.  The installation and setup for these features requires an understanding of setup and use of ODBC drivers as well as rudimentary programming within the IGOR_ envitonment.  To date, this has been tested on Mac OS X 10.9.  Details may vary for other systems.  

Activating SQL database access in IGOR
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Database functionality in IGOR is preloaded, but not activated for use in the standard installation of SQL.xop_.  To activate this feature follow the instructions detailed in "Igor Pro Folder/More Extensions/utilities/SQL Help.ihf".  The next few steps are reproduced from the IGOR_ instructoins.   First, activate the  step in the activation process is open the folder, "Igor Pro Folder/More Extensions/utilities" and creade an alias for SQL.xop_.  Then move the alias to "Igor Pro/Igor Extensions" or a similar folder that is in the search folder for IGOR_.  It may be necessary to delete the "alias" text from the file name for functionality.  Restart IGOR_ to activate.

IGOR_ relies on an external ODBC driver for database access.  Depending on the operating system, it may be necessary to install a stand alone ODBC driver administrator package.  First check your machine for ODBC administrator.app  in the "~/Applications/Utilities".  If not present `ODBC administrator`_ can be downloaded directly from the apple support pages.  To test the functionality, it is useful to follow the *Installing MySQL ODBC Driver...* instructions on the IGOR_ help page.  The MySQL drivers are not necessary for functionally within Mosaic.

With the ODBC administrator program installed, the next step is to install the `SQLite driver for IGOR`_ necessary to interface with the database.  Once downloaded run the installation package in "sqlite3-odbc-0.93.dmg" and follow the setup instructions within the disk image.  The driver should be ready to use withn IGOR_.

Running and Queery in IGOR
^^^^^^^^^^^^^^^^^^^^^^^^^^

IGOR_ operates on databases with a single High Level operation command.  This one commance handels the database connection, queery, export of data and closing of the database in one simple function or macro.  To access this functionality, first open the proceedure window and create the following function:

.. code-block:: igor

	#include <SQLUtils>

	Function QueerySQLData()

		String connectionStr= "DRIVER={SQLite3 Driver;DATABASE='database path';"
		String statement = "select Blockdepth, ResTime from metadata where ProcessingStatus ='normal'"

		SQLHighLevelOp/CSTR={connectionStr, SQL_Driver_COMPLETE}/O/E=1 statement
	End

Running this function will extract all normal events and create two waves containing the Blockade depth and Residence time of the events in sequence for further processing in IGOR_.





.. include:: ../aliases.rst
