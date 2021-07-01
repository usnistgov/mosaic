.. _matlab-addons-sec:

Matlab
---------------------------------

The SQLite database output by MOSAIC can be further processed using MATLAB_.  The data can then be stored in an array in the MATLAB_ Workspace, and then manipulated as desired.

The features, of opening, querying, and storing as an array, are made available in the MATLAB_ script openandquery.m. The script does not use the MATLAB_ Database Manager GUI, a part of the Database Toolbox, which requires a paid license.  Instead, an open-source alternative, mksqlite_, an interface between MATLAB_ and SQLite_ is used.

This section of the manual provides information on how to set up the mksqlite- package for use with MATLAB_, and how to use the openandquery.m script.

All code has been successfully tested with MATLAB 2013a, MATLAB 2014a, G++ 4.7 in Ubuntu 14.04 LTS, and Windows Visual C++ 2010.  Also, SQLite_ must be installed prior to performing the following steps.

mksqlite Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Information about mksqlite_, such as function calls and examples, is available in the MKSQLITE: A MATLAB_ Interface to SQLite documentation.

Installing mksqlite in Ubuntu 14.04 LTS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the latest mksqlite_ source files from `SourceForge <http://sourceforge.net/projects/mksqlite/files/>`_
Unzip the files to a folder, and note the path to that folder (e.g., /home/mksqlitefolder)
Open MATLAB_, and change the current path to that of the mksqlite folder
In the Command Window, type `buildit`, and press Enter to build mksqlite (this will run the buildit.m script).  If the MEX files do not build, one of the following two problems may be why:
i) a compiler may not be installed -- see the `MathWorks page on Supported and Compatible Compilers <http://www.mathworks.com/support/compilers/R2014b/index.html>`_ to select and install a compiler, or ii) errors are generated during compilation of mksqlite.cpp.  In the latter case, see the “How to build mksqlite MEX file mksqlite.mexa64 in Linux?” thread in the `MathWorks MATLAB Answers forum <http://www.mathworks.com/matlabcentral/answers/86590-how-to-build-mksqlite-mex-file-mksqlite-mexa64-in-linux>`_.
If the build proceeds without errors, you will first see the notification “compiling release version of mksqlite...” in the Command Window, followed by “completed.”

.. note:: GCC/G++ Version (in Linux)

	You may have to install a version of GCC/G++ that is compatible with with your specific MATLAB release.  If so, check out the linked discussion thread on MATLAB Central on how to `set up a MEX Compiler <http://www.mathworks.com/matlabcentral/answers/137228-setup-mex-compiler-for-r2014a-for-linux>`_.

Installing mksqlite in Windows 7
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The installation steps are essentially the same as for Ubuntu, except a different compiler (e.g, contained in Windows SDK 7) may instead have to be installed.  If the SDK installer say it cannot proceed, quit the installation, uninstall previous instances of Microsoft Visual C++ 2010, and then install Windows SDK 7 again.

Opening, Querying, and Closing the MOSAIC Output Database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The MATLAB script openandquery.m contains all of the commands to:
Open a MOSAIC database (e.g., eventMD-PEG29-Reference.sqlite)
Query the database
Save queried data elements into a structure
Close the database
Convert the structure into a multi-dimensional array, that can be easily manipulated in MATLAB_

Two changes must be made to the openandquery m-file by the end-user:
The path to the database file must be changed for each database you wish to access.  An example path in Linux would be /home/Data/eventMD-PEG29-Reference.sqlite, and in Windows C:\\Data\\eventMD-PEG29-Reference.sqlite.
The query string can be changed as needed.  More information about queries in available in the :ref:`database-page` section.

Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The reference database file provided with MOSAIC is *eventMD-PEG29-Reference.sqlite*, located in the data folder of the source code root directory.  This database contains the results of an analysis performed using the *adept2State* and consists of the data fields:

	
.. code-block:: javascript

	{recIDX, ProcessingStatus, OpenChCurrent, BlockedCurrent, EventStart, EventEnd, BlockDepth, ResTime, RCConstant, AbsEventStart, ReducedChiSquared, and TimeSeries}


In the openandquery script modify line 20 by typing in, within the quotes, the correct path to the database file.

.. code-block:: matlab

	dbname = '/home/Data/eventMD-PEG29-Reference.sqlite';              

The query in line 23 is to read the names of all fields in the database.  The names, along with column ID, and data type, are stored in the structure fieldnames.  You may double-click on the variable fieldnames in the Workspace, which will open the structure for you to read the field names in which you are interested.

.. code-block:: matlab
	
	fieldnames = mksqlite('PRAGMA table_info(metadata)');
	
Next, modify line 24 to include the query.  In this example we want to select (and later manipulate) the data stored in the fields AbsEventStart and BlockDepth.  This is where mksqlite comes in: the query are arguments to the mksqlite() function.  For more information about using the mksqlite.m function check out the mksqlite documentation.

.. code-block:: matlab

	querytemp = mksqlite('select AbsEventStart, BlockDepth from metadata');

No other changes are required.  Run the script.  The queried data are stored in the variable data, seen in the MATLAB Workspace (with value 418x2 double).  This variable is a 2-column matrix.  The first column contains all 418 data elements of the field AbsEventStart, and the second column contains all elements of the field BlockDepth. Note that the query above can be replaced with any standard SQL query as outlined in the :ref:`working-with-sqlite-sec` section.

.. include:: ../aliases.rst

