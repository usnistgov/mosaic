# -*- coding: utf-8 -*-
"""
	Implementation of an 'N' order Bessel filter

	:Created: 7/1/2013
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
				11/2/16         KB      changed Bessel filter implementation to match expected rise time
		9/27/16 	AB 	Control phase delay
		9/13/15 	AB 	Updated logging to use mosaicLogFormat class
		7/1/13		AB	Initial version
"""
import numpy as np 
import scipy.signal as sig
import sys

import mosaic.filters.metaIOFilter as metaIOFilter
import mosaic.utilities.mosaicLogging as mlog

__all__ = ["besselLowpassFilter"]

class besselLowpassFilter(metaIOFilter.metaIOFilter):
	"""
		:Keyword Args:
		In addition to metaIOFilter.__init__ args,
			- `filterOrder` :		the filter order
			- `filterCutoff` :	filter cutoff frequency in Hz
	"""
	
	def _init(self, **kwargs):
		"""
		"""
		self.logger=mlog.mosaicLogging().getLogger(__name__)

		try:
			self.filterOrder=float(kwargs['filterOrder'])
			self.filterCutoff=float(kwargs['filterCutoff'])
		except KeyError:
			self.logger.error( "ERROR: Missing mandatory arguments 'filterOrder' or 'filterCutoff'" )
		try:	
			self.causal = kwargs['causal'] == "True"
		except KeyError:
			self.causal = False

		if self.causal:
			raise NotImplementedError('Causal filter has not been implemented yet')

	def filterData(self, icurr, Fs):
		"""
			Denoise an ionic current time-series and store it in self.eventData

			:Parameters:
				- `icurr` :	ionic current in pA
				- `Fs` :	original sampling frequency in Hz
		"""
		self.eventData=icurr
		self.Fs=Fs

		#pad the data with 10x the transient time at both ends to manually eliminate edge effects of the filter
		#for some reason I can't get good results using the pad method in filtfilt so manual it is
		#this means there may be some numerical artefacts but they should be well below the level of noise
		
		padding = int(10 * self.Fs/float(self.filterCutoff))
		paddedsignal = np.pad(self.eventData,pad_width=padding,mode='edge')
		
		b, a=sig.bessel(
							N=self.filterOrder, 
							Wn=(self.filterCutoff/(float(self.Fs)/2.0)), 
							btype='lowpass', 
							analog=False, 
							output='ba',
							norm='mag'
						)

		self.eventData=sig.filtfilt(b, a, paddedsignal, padtype=None, method='pad')[padding:-padding]

	def formatsettings(self):
		"""
			Populate `logObject` with settings strings for display
		"""
		self.logger.info( '\tFilter settings:' )

		self.logger.info( '\t\tFilter type = {0}'.format(self.__class__.__name__) )
		self.logger.info( '\t\tFilter order = {0}'.format(self.filterOrder) )
		self.logger.info( '\t\tFilter cutoff = {0} kHz'.format(self.filterCutoff*1e-3) )
		self.logger.info( '\t\tDecimation = {0}'.format(self.decimate) )
		
