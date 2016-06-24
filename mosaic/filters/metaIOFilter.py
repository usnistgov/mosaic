# -*- coding: utf-8 -*-
"""
	A meta class that defines the interface for filtering data that is read in by any 
	implementation of metaTrajIO

	:Created:	7/1/2013
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		7/1/13		AB	Initial version
"""
from abc import ABCMeta, abstractmethod
import mosaic.utilities.util as util
from mosaic.utilities.mosaicLogFormat import mosaic_property

__all__ = ["metaIOFilter"]

class metaIOFilter(object):
	"""
		.. warning:: |metaclass|

		Defines the interface for specific filter implementations. Each filtering
		algorithm must sub-class metaIOFilter and implement the following abstract
		function:
			- `filterData` : 	apply a filter to self.eventData

		:Parameters:
			- `decimate` :		sets the downsampling ratio of the filtered data (default:1, no decimation). 

		:Properties:
			- `filteredData` :		list of filtered and decimated data
			- `filterFs` :			sampling frequency after filtering and decimation
	"""
	__metaclass__=ABCMeta

	def __init__(self, **kwargs):
		"""
		"""
		self.decimate=int(kwargs.pop('decimate', 1))

		# sub-class initialization
		self._init(**kwargs)

	@abstractmethod
	def _init(self, **kwargs):
		"""
			.. important:: |abstractmethod|
		"""
		pass

	@abstractmethod
	def filterData(self, icurr, Fs):
		"""
			.. important:: |abstractmethod|

			This is the equivalent of a pure virtual function in C++. 

			Implementations of this method MUST store (1) a ref to the raw event data in self.eventData AND 
			(2) the sampling frequency in self.Fs.

			:Parameters:
				- `icurr` :	ionic current in pA
				- `Fs` :	original sampling frequency in Hz
		"""
		pass

	@abstractmethod
	def formatsettings(self):
		"""
			.. important:: |abstractmethod|

			Return a formatted string of filter settings
		"""
		pass

	@mosaic_property
	def filteredData(self):
		"""
			Return filtered data
		"""
		# return util.decimate(self.eventData, self.decimate)
		return self.eventData[::self.decimate]

	@mosaic_property
	def filterFs(self):
		"""
			Return the sampling frequency of filtered data.
		"""
		return self.Fs/self.decimate


