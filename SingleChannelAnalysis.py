import settings

class SingleChannelAnalysis(object):
	"""
	"""
	def __init__(self, trajDataObj, eventPartitionHnd, eventProcHnd):
		"""
		"""
		# Read and parse the settings file
		self.settingsDict=settings.settings( trajDataObj.datPath )

		self.mEventPartition=eventPartitionHnd(
								trajDataObj, 
								eventPartitionHnd, 
								self.settingsDict.getSettings(eventPartitionHnd.__name__),
								self.settingsDict.getSettings(eventProcHnd.__name__)
							)

	def Run(self):
		"""
		"""
		