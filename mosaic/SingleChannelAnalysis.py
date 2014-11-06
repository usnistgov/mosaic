"""
	Top level module to run a single channel analysis.

	:Created:	05/15/2014
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT	
	:ChangeLog:
	.. line-block::
		5/15/14		AB	Initial version
"""
__docformat__ = 'restructuredtext'

import settings
import multiprocessing
import os
import signal
import json

def run_eventpartition( trajdataObj, eventPartHnd, eventProcHnd, settingsdict):
	try:
		with eventPartHnd(
							trajdataObj, 
							eventProcHnd, 
							settingsdict.getSettings(eventPartHnd.__name__),
							settingsdict.getSettings(eventProcHnd.__name__),
							json.dumps(settingsdict.settingsDict, indent=4)
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
	"""
	def __init__(self, dataPath, trajDataHnd, dataFilterHnd, eventPartitionHnd, eventProcHnd):
		"""
		"""
		# Read and parse the settings file
		self.settingsDict=settings.settings( dataPath )

		# Pull out trajectory settings to construct an IO object
		trajSettings=self.settingsDict.getSettings(trajDataHnd.__name__)
		
		if dataFilterHnd:
			self.trajDataObj=trajDataHnd( datafilter=dataFilterHnd, dirname=dataPath, **trajSettings )
		else:
			self.trajDataObj=trajDataHnd( **trajSettings )
		self.eventPartitionHnd=eventPartitionHnd
		self.eventProcHnd=eventProcHnd

		self.subProc=None

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
						args=(self.trajDataObj, self.eventPartitionHnd, self.eventProcHnd, self.settingsDict,)
					)
				self.subProc.start()
				# self.proc.join()
			except:
				self.subProc.terminate()
				self.subProc.join()
		else:
			run_eventpartition( self.trajDataObj, self.eventPartitionHnd, self.eventProcHnd, self.settingsDict )

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

