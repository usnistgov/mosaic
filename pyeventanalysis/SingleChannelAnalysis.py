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
					proc = multiprocessing.Process( target=EventPartition.PartitionEvents )
					proc.start()
					proc.join()
				except:
					proc.join()
			else:
				EventPartition.PartitionEvents()
