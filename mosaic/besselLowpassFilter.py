# -*- coding: utf-8 -*-
"""
	Implementation of an 'N' order Bessel filter

	:Created: 7/1/2013
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		9/13/15 	AB 	Updated logging to use mosaicLog class
		7/1/13		AB	Initial version
"""
import numpy as np 
import scipy.signal as sig

import mosaic.metaIOFilter
import mosaic.utilities.mosaicLog as log

__all__ = ["besselLowpassFilter"]

class besselLowpassFilter(mosaic.metaIOFilter.metaIOFilter):
	"""
		:Keyword Args:
		In addition to metaIOFilter.__init__ args,
			- `filterOrder` :		the filter order
			- `filterCutoff` :	filter cutoff frequency in Hz
	"""
	
	def _init(self, **kwargs):
		"""
		"""
		try:
			self.filterOrder=float(kwargs['filterOrder'])
			self.filterCutoff=float(kwargs['filterCutoff'])
		except KeyError:
			print "Missing mandatory arguments 'filterOrder' or 'filterCutoff'"


	def filterData(self, icurr, Fs):
		"""
			Denoise an ionic current time-series and store it in self.eventData

			:Parameters:
				- `icurr` :	ionic current in pA
				- `Fs` :	original sampling frequency in Hz
		"""
		self.eventData=icurr
		self.Fs=Fs

		self.filterModel=sig.filter_design.bessel(
							N=self.filterOrder, 
							Wn=(self.filterCutoff/(self.Fs/2)), 
							btype='lowpass', 
							analog=False, 
							output='ba'
						)

		# calculate the initial state of the filter and scale it with the first data point
		# so there is no sharp transient at the start of the data
		zi=sig.lfilter_zi(b=self.filterModel[0], a=self.filterModel[1])*self.eventData[0]

		[self.eventData, zf]=sig.lfilter(
								b=self.filterModel[0],
								a=self.filterModel[1],
								x=self.eventData,
								zi=zi
							)

	def formatsettings(self):
		"""
			Populate `logObject` with settings strings for display
		"""
		logObj=log.mosaicLog()


		logObj.addLogHeader( 'Filter settings:' )

		logObj.addLogText( 'Filter type = {0}'.format(self.__class__.__name__) )
		logObj.addLogText( 'Filter order = {0}'.format(self.filterOrder) )
		logObj.addLogText( 'Filter cutoff = {0} kHz'.format(self.filterCutoff*1e-3) )
		logObj.addLogText( 'Decimation = {0}'.format(self.decimate) )
		
		
		return str(logObj)
