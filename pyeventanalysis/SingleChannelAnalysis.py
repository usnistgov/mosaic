import settings
import multiprocessing

class SingleChannelAnalysis(object):
	"""
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
		with self.eventPartitionHnd(
							self.trajDataObj, 
							self.eventProcHnd, 
							self.settingsDict.getSettings(self.eventPartitionHnd.__name__),
							self.settingsDict.getSettings(self.eventProcHnd.__name__)
						) as EventPartition:
			if forkProcess:
				try:
					self.subProc = multiprocessing.Process( target=EventPartition.PartitionEvents )
					self.subProc.start()
					# self.proc.join()
				except:
					self.subProc.join()
			else:
				EventPartition.PartitionEvents()
