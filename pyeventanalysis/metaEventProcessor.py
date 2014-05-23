"""
	A meta class that defines the interface for event processing functions. The class object stores the 
	raw data for the event as well as meta-data after processing individual events. The meta-data is
	defined by specfic implementations of this class.

	Author: 	Arvind Balijepalli
	Created:	7/16/2012

	ChangeLog:
		5/17/14		AB  Add metaMDIO support for meta-data and time-series storage
		2/16/14		AB 	Define new kwarg, absdatidx to allow capture rate estimation.
		6/28/13		AB 	Added a new keyword argument 'savets'. When set to False, the event time-series
						is set to None. This can save a lot of memory when handling large data sets. 
		7/16/12		AB	Initial version
"""
from abc import ABCMeta, abstractmethod
import types
import sys

class metaEventProcessor(object):
	"""
		Defines the interface for specific event processing algorithms. Each event processing
		algorithm must sub-class metaEventProcessor and implement the following abstract
		functions:
			processEvent: 	process raw event data and populate event meta-data. Store each 
							piece of processed event data in a class attribute starting with 'md'.
							For example, the blockade depth meta-data can be defined as 'mdBlockadeDepth'
			printMetadata 	print meta-data set by event processing in a human readable format.
	"""
	__metaclass__=ABCMeta

	def __init__(self, icurr, Fs, **kwargs):
		"""
			Store a ref to the raw event data.
			Args:
				icurr				ionic current in
				Fs 					sampling frequency in Hz
			Keyword Args:
				eventstart			the event start point
				eventend			the event end point
				baselinestats 		baseline conductance statistics: a list of [mean, sd, slope] for the baseline current
				algosettingsdict 	settings for event processing algorithm as a dictionary
				absdatidx 			index of data start. This arg can allow arrival time estimation.
				datafileHnd			reference to an metaMDIO object for meta-data IO
		"""
		self.eventData=icurr
		self.Fs=Fs

		# Will throw a key error if not passed
		self.eStartEstimate=kwargs['eventstart']
		self.eEndEstimate=kwargs['eventend']

		self.settingsDict=kwargs['algosettingsdict']

		self.absDataStartIndex=kwargs['absdatidx']

		[ self.baseMean, self.baseSD, self.baseSlope ]=kwargs['baselinestats']

		self.saveTS=kwargs['savets']
		
		self.dataFileHnd=kwargs['datafileHnd']

		# meta-data attrs that are common to all event processing
		self.mdProcessingStatus='normal'

		# Call sub-class initialization
		self._init(**kwargs)

	def processEvent(self):
		"""
			This is the equivalent of a pure virtual function in C++. 
		"""
		self._processEvent()

		if not self.saveTS:
			self.eventData=[]

		self.writeEvent()

	@abstractmethod
	def _init(self, **kwargs):
		pass

	@abstractmethod
	def _processEvent(self):
		pass

	@abstractmethod
	def mdList(self):
		"""
			Return a list of meta-data set by event processing.  				
		"""
		pass
	
	@abstractmethod
	def mdHeadings(self):
		"""
			Return a list of meta-data tags for display purposes.
		"""
		pass

	@abstractmethod
	def mdHeadingDataType(self):
		"""
			Return a list of meta-data tags data types.
		"""
		pass

	@abstractmethod
	def mdAveragePropertiesList(self):
		"""
			Return a list of meta-data properties that will be averaged 
			and displayed at the end of a run. This function must be overridden
			by sub-classes of metaEventProcessor. As a failsafe, an empty list
			is returned.
		"""
		pass
		#return []

	def rejectEvent(self, status):
		"""
			Set an event as rejected if it doesn't pass tests in processing.
			The status is assigned to mdProcessingStatus.
		"""
		# set all meta data to -1
		[ setattr(self, mdHead, -1) for mdHead in self.__dict__.keys() if mdHead.startswith('md')==True ]
		# set processing status to status
		self.mdProcessingStatus=status

	def writeEvent(self):
		"""
			Write event meta data to a metaMDIO object.
		"""
		if self.dataFileHnd:
			self.dataFileHnd.writeRecord( (self.mdList())+[self.eventData] )

	###########################################################################
	# Local functions
	###########################################################################
	def __mdformat(self, dat):
		"""
			Round a float to 3 decimal places. Leave ints and strings unchanged
		"""
		if type(dat) is types.FloatType:
			return round(dat, 3)
		else:
			return dat
