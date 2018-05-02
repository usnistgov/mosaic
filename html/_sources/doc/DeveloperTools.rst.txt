.. _developer-tools-page:

Developer Tools
=================================

We provide several tools to simplify developing and extending |projname| including debug information logging and function timing and profiling tools. Developer settings can be modified from ``mosaic/_globals.py``. The master switch to turn on developer mode is the ``DeveloperMode`` attribute. **NOTE:** When ``DeveloperMode=False``, all remaining attributes in ``mosaic/_globals.py`` are ignored.

.. sourcecode:: python

	# Control global settings
	DeveloperMode=True		# Turn on developer options.

	CodeProfiling='summary'		# Either 'summary' to print a summary at the end of a run, 
					# 'none' for no timing, or 
					# 'all' to print timing of every function call profiled.
	LogProperties=False		# Log all class properties defined with mosaic_property.
	LogSizeBytes=int(2<<20) 	# 2 MB


Debug Logs
---------------------------------------------

When ``DeveloperMode`` is active, logs are simultaneously saved the SQLite_ database, the console, and to a file using the Python_ logging module as described below. Details of the logging module can be found  `here <https://docs.python.org/2/library/logging.html>`_. The logging facility provides different classes of messages with increasing severity, ranging from ``debug`` to help trace problems with code, ``info`` to provide feedback, ``warn`` to generate warnings, and ``error`` for error messages.

By default log messages in |projname| with a level of ``info`` and higher are saved to the console and to the SQLite_ database. On the other hand, ``debug`` messages are saved to a log file (see table below for log file locations). Since ``debug`` output can be verbose, the log file size is limited to the ``LogSizeBytes`` attribute in ``mosaic/_globals.py``. The default value for this attribute is 2 MB. The log file is implemented with a rotating file structure, where  only the previous five log files are saved to conserve disk space.

+--------------------+----------------------------------------------+
|  **Platform**      |  **Log File Location**                       |
+====================+==============================================+
|  macOS             |  ~/Library/Logs/MOSAIC/mosaic.log            |
+--------------------+----------------------------------------------+
|  linux             |  ~/mosaic.log                                |
+--------------------+----------------------------------------------+
|  linux (with sudo) |  /var/logs/mosaic.log                        |
+--------------------+----------------------------------------------+
|  Windows           |  <user home>/mosaic.log                      |
+--------------------+----------------------------------------------+

Log messages can be added by first creating a logger instance and then logging a message as seen in the code sample below. For debug logs, the helper functions :py:func:`~mosaic.utilities.mosaicLogFormat._d` or :py:func:`~mosaic.utilities.mosaicLogFormat._dprop`, defined in the :py:mod:`~mosaic.utilities.mosaicLogFormat` module should be used. The helper functions append stack information to debug logs, allowing users to trace the calling function and its location in the source code.

.. sourcecode:: python
	:linenos:

	import mosaic.utilities.mosaicLogging as mlog
	from mosaic.utilities.mosaicLogFormat import _d


	queryString="select ProcessingStatus, TimeSeries, RCConstant, EventDelay, CurrentStep, OpenChCurrent from metadata limit 10000"
	logger=mlog.mosaicLogging().getLogger(name=__name__, dbHnd=self.mdioDBHnd)

	logger.debug(_d("{0}", queryString))


.. figure:: ../images/DevelLog.png
  :width: 75 %
  :align: center

The above code results in the following log message. 

.. sourcecode:: python
	
	2016-06-18 12:58:11 DEBUG    mosaic.sqlite3MDIO: 
		select ProcessingStatus, TimeSeries, RCConstant, EventDelay, CurrentStep, OpenChCurrent from metadata limit 10000 
		(queryDB:_updatequery:mosaic/mosaicgui/fiteventsview/fiteventsview.py:295)

.. sourcecode:: python
	
	2016-06-17 13:36:30 WARNING  mosaic.metaEventPartition: 
		WARNING: Automatic open channel state estimation has been disabled.

.. sourcecode:: python

	2016-06-20 22:56:38 CRITICAL mosaic.utilities.mosaicLogging: 
		Traceback (most recent call last):
			File "mosaic/utilities/mosaicTiming.py", line 180, in <module>
				raise NotImplementedError("Feature not implemented.")
		NotImplementedError: Feature not implemented.


Function Timing and Profiling
---------------------------------------------

.. sourcecode:: python
	:linenos:

	import mosaic.utilities.mosaicTiming as mosaicTiming

	partitionTimer=mosaicTiming.mosaicTiming()

	class metaEventPartition(object):
		... ... ...

		@metaEventPartition.partitionTimer.FunctionTiming
		def _processEvent(self, eventobj):
			... ... ...

		def Stop(self):
			... ... ...

			partitionTimer.PrintStatistics()

			... ... ...

.. sourcecode:: python
	:linenos:

	import mosaic.utilities.mosaicTiming as mosaicTiming

	with mosaicTiming.mosaicTiming() as funcTimer:
		@funcTimer.FunctionTiming
		def someFunc():
			... ... ...

			do something

			... ... ...



.. sourcecode:: python

	2016-06-18 12:58:16 DEBUG    mosaic.utilities.mosaicTiming: 
		Summary timing for "_processEvent": iterations=582, total=13475.599 ms, maximum=296.641 ms, average=23.154 ms 
		(PrintStatistics:Stop:mosaic/metaEventPartition.py:171)

.. include:: ../aliases.rst

