"""
	Top level module to run a single channel analysis.

	:Created:	05/15/2014
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT	
	:ChangeLog:
	.. line-block::
		3/25/17 	AB 	Allow an optional argument to pass a database name.
		5/15/14		AB	Initial version
"""
__docformat__ = 'restructuredtext'

import mosaic.settings as settings
from mosaic.utilities.ga import registerStart, registerStop
import multiprocessing
import os
import signal
import json

__all__ = ["SingleChannelAnalysis", "run_eventpartition"]

def run_eventpartition( dataPath, trajDataHnd, dataFilterHnd, eventPartHnd, eventProcHnd, dbFilename):
	# Read and parse the settings file
	settingsdict=settings.settings( dataPath )	

	# Pull out trajectory settings to construct an IO object
	trajSettings=settingsdict.getSettings(trajDataHnd.__name__)
	
	if dataFilterHnd:
		trajDataObj=trajDataHnd( datafilter=dataFilterHnd, dirname=dataPath, **trajSettings )
	else:
		trajDataObj=trajDataHnd( dirname=dataPath, **trajSettings )

	if dbFilename=='':
		kwargs={}
	else:
		kwargs={'dbFilename': dataPath+'/'+dbFilename}

	try:
		with eventPartHnd(
							trajDataObj, 
							eventProcHnd, 
							settingsdict.getSettings(eventPartHnd.__name__),
							settingsdict.getSettings(eventProcHnd.__name__),
							json.dumps(settingsdict.settingsDict, indent=4),
							**kwargs
						) as EventPartition:
			EventPartition.PartitionEvents()
	except KeyboardInterrupt:
		raise

class SingleChannelAnalysis(object):
	"""
		Run a single channel analysis. This is the entry point class for the analysis.

		:Parameters:
			- `dataPath` : full path to the data directory
			- `trajDataHnd` : a handle to an implementation of :class:`~mosaic.metaTrajIO`
			- `dataFilterHnd` : a handle to an impementation of :class:`~mosaic.metaIOFilter`
			- `eventPartitionHnd` : a handle to a sub-class of :class:`~mosaic.metaEventPartition`
			- `eventProcHnd` : a handle to a sub-class of :class:`~mosaic.metaEventProcessor`
			- `dbFilename` : explicitly set the database name (optional kwarg).
	"""
	def __init__(self, dataPath, trajDataHnd, dataFilterHnd, eventPartitionHnd, eventProcHnd, **kwargs):
		"""
		"""
		self.dataPath=dataPath	

		if dataFilterHnd:
			self.dataFilterHnd=dataFilterHnd
		else:
			self.dataFilterHnd=None

		self.trajDataHnd=trajDataHnd
		self.eventPartitionHnd=eventPartitionHnd
		self.eventProcHnd=eventProcHnd

		self.dbFilename=kwargs.get('dbFilename', '')

		self.subProc=None

	@registerStart
	def Run(self, forkProcess=False):
		"""
			Start an analysis. 

			:Parameters:
				- `forkProcess` : start the analysis in a separate process if *True*. This option is useful when the main thread is used for other processing (e.g. GUI implementations).
		"""
		if forkProcess:
			try:
				self.subProc = multiprocessing.Process( 
						target=run_eventpartition,
						args=(self.dataPath, self.trajDataHnd, self.dataFilterHnd, self.eventPartitionHnd, self.eventProcHnd, self.dbFilename,)
					)
				self.subProc.start()
				# self.proc.join()
			except:
				self.subProc.terminate()
				self.subProc.join()
		else:
			run_eventpartition( self.dataPath, self.trajDataHnd, self.dataFilterHnd, self.eventPartitionHnd, self.eventProcHnd, self.dbFilename, )

	@registerStop
	def Stop(self):
		"""
			Stop a running analysis.
		"""
		if self.subProc:
			os.kill( self.subProc.pid, signal.SIGINT )
		else:
			os.kill( os.getpid(), signal.SIGINT )

	@property 
	def DataPath(self):
		return self.trajDataObj.datPath

