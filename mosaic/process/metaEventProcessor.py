""" 
	A meta class that defines the interface for event processing functions. The class object stores the 
	raw data for the event as well as meta-data after processing individual events. The meta-data is
	defined by specfic implementations of this class.

	:Created:	7/16/2012
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		9/22/17 	AB 	Add a parameter to save unfiltered event padding.
		8/3/16		JF	Fixed missing dependency (time)
		5/27/16 	AB 	Add a flagEvent function that should be used to set a non-critical warning status.
		5/26/16 	AB 	If developer mode is enabled (in mosaic/_global), metadata is not set to -1 when an error occurs.
		3/30/16 	AB 	Fixed function timing resolution on Windows
		8/30/14		AB 	Added a timeout/retry to handle DB locked error.
		5/17/14		AB  Add metaMDIO support for meta-data and time-series storage
		2/16/14		AB 	Define new kwarg, absdatidx to allow capture rate estimation.
		6/28/13		AB 	Added a new keyword argument 'savets'. When set to False, the event time-series
						is set to None. This can save a lot of memory when handling large data sets. 
		7/16/12		AB	Initial version
"""
from abc import ABCMeta, abstractmethod
import types
import time
import mosaic.utilities.mosaicTiming as mosaicTiming
import mosaic.utilities.mosaicLogging as mlog
import sqlite3
import numpy as np
import mosaic

__all__ = ["metaEventProcessor", "MissingMDIOError"]

# custom errors
class MissingMDIOError(Exception):
	pass

class metaEventProcessor(object, metaclass=ABCMeta):
	"""
		.. warning:: |metaclass|

		Defines the interface for specific event processing algorithms. Each event processing
		algorithm must sub-class metaEventProcessor and implement the following abstract
		functions:
			- `processEvent` : 	process raw event data and populate event meta-data. Store each 
							piece of processed event data in a class attribute starting with 'md'.
							For example, the blockade depth meta-data can be defined as 'mdBlockadeDepth'
			- `printMetadata` :	print meta-data set by event processing in a human readable format.

		:Parameters:
				- `icurr` :				ionic current in pA
				- `icurrU`:				ionic current in pA with unfiltered event padding
				- `Fs` :				sampling frequency in Hz

		:Keyword Args:
				- `eventstart` :		the event start point
				- `eventend` :			the event end point
				- `baselinestats` : 	baseline conductance statistics: a list of [mean, sd, slope] for the baseline current
				- `algosettingsdict` : 	settings for event processing algorithm as a dictionary
				- `absdatidx` :			index of data start. This arg can allow arrival time estimation.
				- `datafilehnd` :		reference to an metaMDIO object for meta-data IO
	"""

	def __init__(self, icurr, icurrU, Fs, **kwargs):
		"""
			Store a ref to the raw event data.
			
		"""
		self.eventData=icurr
		self.eventDataU=icurrU
		self.Fs=Fs

		self.logger=mlog.mosaicLogging().getLogger(name=__name__)

		# Will throw a key error if not passed
		self.eStartEstimate=kwargs['eventstart']
		self.eEndEstimate=kwargs['eventend']

		self.settingsDict=kwargs['algosettingsdict']

		self.absDataStartIndex=kwargs['absdatidx']

		[ self.baseMean, self.baseSD, self.baseSlope ]=kwargs['baselinestats']

		self.saveTS=kwargs['savets']
		
		# Optional args. If dataFileHnd is not passed at init, it must be set later
		# If not set before WriteEvent is called, it will result in a MissingMDIOError
		self.dataFileHnd=kwargs.pop("datafilehnd", None)
		# self.dataFileHnd=kwargs['datafileHnd']

		# meta-data attrs that are common to all event processing
		self.mdProcessingStatus='normal'

		# Setup function timing
		self.timingObj=mosaicTiming.mosaicTiming()

		self.mdEventProcessTime=0.0
		# print self.settingsDict
		# Call sub-class initialization
		self._init(**kwargs)

	def processEvent(self):
		"""
			This is the equivalent of a pure virtual function in C++. 
		"""
		start_time=self.timingObj.time()

		self.dataPolarity=float(np.sign(np.mean(self.eventData)))

		self._processEvent()

		self.mdEventProcessTime=1000.*(self.timingObj.time()-start_time)

		if not self.saveTS:
			self.eventData=[]

		self.writeEvent()

	@abstractmethod
	def _init(self, **kwargs):
		"""
			.. important:: |abstractmethod|
		"""
		pass

	@abstractmethod
	def _processEvent(self):
		"""
			.. important:: |abstractmethod|
		"""
		pass

	@abstractmethod
	def _mdList(self):
		"""
			.. important:: |abstractmethod|

			Return a list of meta-data set by event processing.  				
		"""
		pass
	
	@abstractmethod
	def _mdHeadings(self):
		"""
			.. important:: |abstractmethod|

			Return a list of meta-data tags for display purposes.
		"""
		pass

	@abstractmethod
	def _mdHeadingDataType(self):
		"""
			.. important:: |abstractmethod|

			Return a list of meta-data tags data types.
		"""
		pass

	@abstractmethod
	def mdAveragePropertiesList(self):
		"""
			.. important:: |abstractmethod|

			Return a list of meta-data properties that will be averaged 
			and displayed at the end of a run. This function must be overridden
			by sub-classes of metaEventProcessor. As a failsafe, an empty list
			is returned.
		"""
		pass
		#return []

	def mdHeadings(self):
		"""
			Return a list of meta-data tags for display purposes.
		"""
		return self._mdHeadings()+['ProcessTime', 'TimeSeries']

	def mdHeadingDataType(self):
		"""
			Return a list of meta-data tags data types.
		"""
		return self._mdHeadingDataType()+['REAL', 'REAL_LIST']


	def flagEvent(self, status):
		"""
			Set a warning status that starts with 'w' for non-critical errors. 
			Metadata for these events is preserved and the user can be warned (e.g., in the GUI.)

		"""
		# Trigger if this is the first warning i.e. status == normal
		if self.mdProcessingStatus=='normal':
			self.mdProcessingStatus=status

	def rejectEvent(self, status):
		"""
			Set an event as rejected if it doesn't pass tests in processing.
			The status is assigned to mdProcessingStatus.
		"""
		# Only reject events if this is the first error i.e. status == normal
		if self.mdProcessingStatus=='normal':
			if not mosaic.DeveloperMode:
				# set all meta data to -1
				[ self._setRejectMetadata(mdHead) for mdHead in list(self.__dict__.keys()) if mdHead.startswith('md')==True ]
			
			# set processing status to status
			self.mdProcessingStatus=status

	def writeEvent(self):
		"""
			Write event meta data to a metaMDIO object.
		"""
		try:
			if self.dataFileHnd:
				self.dataFileHnd.writeRecord( (self._mdList())+[self.mdEventProcessTime, self.eventDataU] )
		except sqlite3.OperationalError as err:
			# If the db is locked, wait 1 s and try again.
			print(err)
			time.sleep(1)
			self.writeEvent()
		# else:
		# 	raise MissingMDIOError("Meta-data I/O object not initialized.")

	###########################################################################
	# Local functions
	###########################################################################
	def _setRejectMetadata(self, metadata):
		try:
			if len(getattr(self, metadata)) > 1:
				setattr(self, metadata, [-1])
		except TypeError:
			setattr(self, metadata, -1)

	def __mdformat(self, dat):
		"""
			Round a float to 3 decimal places. Leave ints and strings unchanged
		"""
		if type(dat) is float:
			return round(dat, 3)
		else:
			return dat
