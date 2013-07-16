"""
	A meta class that defines the interface for filtering data that is read in by any 
	implementation of metaTrajIO

	Author: 	Arvind Balijepalli
	Created:	7/1/2013

	ChangeLog:
		7/1/13		AB	Initial version
"""
from abc import ABCMeta, abstractmethod
import util

class metaIOFilter(object):
	"""
		Defines the interface for specific filter implementations. Each filtering
		algorithm must sub-class metaIOFilter and implement the following abstract
		function:
			filterData: 	apply a filter to self.eventData
	"""
	__metaclass__=ABCMeta

	def __init__(self, **kwargs):
		"""
			Keyword Args:
				decimate			sets the downsampling ratio of the filtered data (default:1, no decimation). 

			Properties:
				filteredData		list of filtered and decimated data
				filterFs			sampling frequency after filtering and decimation
		"""
		self.decimate=int(kwargs.pop('decimate', 1))

	@abstractmethod
	def filterData(self, icurr, Fs):
		"""
			This is the equivalent of a pure virtual function in C++. Specific filtering
			algorithms must implement this method and then call this base function using super for
			additional processing.

			Implementations of this method MUST store (1) a ref to the raw event data in self.eventData AND 
			(2) the sampling frequence in self.Fs.

			Args:
				icurr				ionic current in pA
				Fs 					original sampling frequency in Hz
		"""
		pass

	@abstractmethod
	def formatsettings(self):
		"""
			Return a formatted string of filter settings
		"""
		pass

	@property
	def filteredData(self):
		"""
			Decimate the data when it is accessed
		"""
		# return util.decimate(self.eventData, self.decimate)
		return self.eventData[::self.decimate]

	@property
	def filterFs(self):
		return self.Fs/self.decimate


