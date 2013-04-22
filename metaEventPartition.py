from abc import ABCMeta, abstractmethod

class metaEventPartition(object):
	"""
		An class to abstract partitioning individual events. Once a single 
		molecule event is identified, it is handed off to to an event processor.
		If parallel processing is requested, detailed event processing will commence
		immediately. If not, detailed event processing is performed after the event 
		partition has completed.
	"""
	__metaclass__=ABCMeta

	def __init__(self, trajDataObj, eventProcHnd, eventPartitionSettings, eventProcSettings):
		"""
			Initialize a new event segment object
			Args:
				trajDataObj:			properly initialized object instantiated from a sub-class 
										of metaTrajIO.
				eventProcHnd:			handle to a sub-class of metaEventProcessor. Objects of 
										this class are initialized as necessary
				eventPartitionSettings	settings dictionary for the partition algorithm.
				eventProcSettings 		settings dictionary for the event processing algorithm.
			Returns:
				None
			
			Errors:
				None

			Common algorithm parameters from settings file (.settings in the data path or 
			current working directory):
				writeEventTS	Write event current data to file. (default: 1, write data to file)
				parallelProc	Process events in parallel using the pproc module. (default: 1, Yes)
		"""
		# Required arguments
		self.trajDataObj=trajDataObj
		self.eventProcHnd=eventProcHnd

		self.settingsDict = eventPartitionSettings 
		self.eventProcSettingsDict = eventProcSettings

		try:
			self.writeEventTS=int(segmentSettings.pop("writeEventTS",1))
			self.parallelProc=int(segmentSettings.pop("parallelProc",1))
		except ValueError as err:
			raise commonExceptions.SettingsTypeError( err )

	@abstractmethod
	def PartitionEvents(self):
		"""
			This is the equivalent of a pure virtual function in C++. Specific event processing
			algorithms must implement this method.
		"""
		pass

	@abstractmethod
	def formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		pass

	@abstractmethod
	def formatstats(self):
		"""
			Return a formatted string of statistics for display
		"""
		pass

	@abstractmethod
	def formatoutputfiles(self):
		"""
			Return a formatted string of output files.
		"""
