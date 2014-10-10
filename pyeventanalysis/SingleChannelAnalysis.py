#
#	Top level module to run a single channel analysis.
#
#	:Author: 	Arvind Balijepalli
#	:Created:	05/15/2014
#
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
		Run a single channel analysis. 
	"""
	def __init__(self, trajDataObj, eventPartitionHnd, eventProcHnd):
		"""
		"""
		# Read and parse the settings file
		self.settingsDict=settings.settings( trajDataObj.datPath )

		self.trajDataObj=trajDataObj
		self.eventPartitionHnd=eventPartitionHnd
		self.eventProcHnd=eventProcHnd

		self.subProc=None

	def Run(self, forkProcess=False):
		"""
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
		if self.subProc:
			os.kill( self.subProc.pid, signal.SIGINT )
		else:
			os.kill( os.getpid(), signal.SIGINT )

	@property 
	def DataPath(self):
		return self.trajDataObj.datPath

