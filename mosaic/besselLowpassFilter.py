# """
# 	Implementation of an 'N' order Bessel filter

# 	Author: Arvind Balijepalli
# 	Created: 7/1/2013

# 	ChangeLog:
# 		7/1/13		AB	Initial version
# """
import numpy as np 
import scipy.signal as sig

import metaIOFilter

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
			Return a formatted string of filter settings
		"""
		fmtstr=""

		fmtstr+='\tFilter settings: \n'
		fmtstr+='\t\tFilter type = {0}\n'.format(self.__class__.__name__)
		fmtstr+='\t\tFilter order = {0}\n'.format(self.filterOrder)
		fmtstr+='\t\tFilter cutoff = {0} kHz\n'.format(self.filterCutoff*1e-3)
		fmtstr+='\t\tDecimation = {0}\n'.format(self.decimate)

		return fmtstr