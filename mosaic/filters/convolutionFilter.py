# -*- coding: utf-8 -*-
"""
	Implementation of a weighted moving average (tap delay line) filter

	:Created: 	8/16/2013
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		9/13/15 	AB 	Updated logging to use mosaicLogFormat class
		8/16/13		AB	Initial version
"""
import numpy as np 
import scipy.signal as sig

import mosaic.filters.metaIOFilter as metaIOFilter
import mosaic.utilities.mosaicLogging as mlog
from mosaic.utilities.util import eval_

__all__ = ["convolutionFilter"]

class convolutionFilter(metaIOFilter.metaIOFilter):
	"""
		:Keyword Args:
		In addition to metaIOFilter.__init__ args,
			- `filterCoeff` :		filter coefficients (default is a 10 point uniform moving average)
	"""

	def _init(self, **kwargs):
		"""
		"""		
		try:
			self.filterCoeff=ast.eval_(kwargs['filterCoeff'])
		except KeyError:
			self.filterCoeff=[1.0/10.0]*10

		self.filtBuf=np.array([])

		self.logger=mlog.mosaicLogging().getLogger(__name__)

	def filterData(self, icurr, Fs):
		"""
			Denoise an ionic current time-series and store it in self.eventData

			:Parameters:
				- `icurr` :	ionic current in pA
				- `Fs` :	original sampling frequency in Hz
		"""
		self.filtBuf=np.hstack( (self.filtBuf, icurr) )
		self.eventData=np.correlate(self.filtBuf, self.filterCoeff, 'valid')
		self.filtBuf=self.filtBuf[len(self.filterCoeff)-1:]


	def formatsettings(self):
		"""
			Return a formatted string of filter settings
		"""
		self.logger.info( '\tFilter settings:' )

		self.logger.info( '\t\tFilter type = {0}'.format(self.__class__.__name__) )
		self.logger.info( '\t\tFilter coefficients = {0}'.format(self.filterCoeff) )
		self.logger.info( '\t\tDecimation = {0}'.format(self.decimate) )
		
	def _filterCutoffFrequency(self):
		return self.Fs
		