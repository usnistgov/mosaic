"""
	A meta class that defines the interface for event processing functions. The class object stores the 
	raw data for the event as well as meta-data after processing individual events. The meta-data is
	defined by specfic implementations of this class.

	Author: 	Arvind Balijepalli
	Created:	7/16/2012

	ChangeLog:
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
		"""
		self.eventData=icurr
		self.Fs=Fs

		# Will throw a key error if not passed
		self.eStartEstimate=kwargs['eventstart']
		self.eEndEstimate=kwargs['eventend']

		self.settingsDict=kwargs['algosettingsdict']

		[ self.baseMean, self.baseSD, self.baseSlope ]=kwargs['baselinestats']

		# meta-data attrs that are common to all event processing
		self.mdProcessingStatus='normal'

	@abstractmethod
	def processEvent(self):
		"""
			This is the equivalent of a pure virtual function in C++. Specific event processing
			algorithms must implement this method.
		"""
		pass

	@abstractmethod
	def mdList(self):
		"""
			Return a list of meta-data set by event processing. 
			By default this function prints all metadata attributes starting with 'md'. 
			To preserve this output, implementations of this class should
			simply invoke the base class function using super. 				
		"""
		return [ str(self.__mdformat(getattr(self, mdHead))) for mdHead in self.__dict__.keys() if mdHead.startswith('md')==True ]
	
	@abstractmethod
	def mdHeadings(self):
		"""
			Return a list of meta-data tags for display purposes. By default
			this function returns any class attributes starting with 'md' sorted alphabetically.
			To keep this functionality, sub-classes must invoke this function using super.
		"""
		# return metadata class attributes
		return [ str(mdHead)[2:] for mdHead in self.__dict__.keys() if mdHead.startswith('md')==True ]

	@abstractmethod
	def mdAveragePropertiesList(self):
		"""
			Return a list of meta-data properties that will be averaged 
			and displayed at the end of a run. This function must be overridden
			by sub-classes of metaEventProcessor. As a failsafe, an empty list
			is returned.
		"""
		return []

	def rejectEvent(self, status):
		"""
			Set an event as rejected if it doesn't pass tests in processing.
			The status is assigned to mdProcessingStatus.
		"""
		# set all meta data to -1
		[ setattr(self, mdHead, -1) for mdHead in self.__dict__.keys() if mdHead.startswith('md')==True ]
		# set processing status to status
		self.mdProcessingStatus=status

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
