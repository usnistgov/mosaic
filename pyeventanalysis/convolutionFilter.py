"""
	Implementation of a weighted moving average (tap delay line) filter


	Author: Arvind Balijepalli
	Created: 8/16/2013

	ChangeLog:
		8/16/13		AB	Initial version
"""
import numpy as np 
import scipy.signal as sig

import metaIOFilter

class convolutionFilter(metaIOFilter.metaIOFilter):
	"""
	"""
	def __init__(self, **kwargs):
		"""
			Keyword Args:
			In addition to metaIOFilter.__init__ args,
				filterCoeff		filter coefficients (default is a 10 point uniform moving average)
		"""
		# base class processing last
		super(convolutionFilter, self).__init__(**kwargs)

		try:
			self.filterCoeff=eval(kwargs['filterCoeff'])
		except KeyError:
			self.filterCoeff=[1.0/10.0]*10

		self.filtBuf=np.array([])

	def filterData(self, icurr, Fs):
		"""
			Filter self.eventData
		"""
		self.filtBuf=np.hstack( (self.filtBuf, icurr) )
		self.eventData=np.correlate(self.filtBuf, self.filterCoeff, 'valid')
		self.filtBuf=self.filtBuf[len(self.filterCoeff)-1:]


	def formatsettings(self):
		"""
			Return a formatted string of filter settings
		"""
		fmtstr=""

		fmtstr+='\tFilter settings: \n'
		fmtstr+='\t\tFilter type = {0}\n'.format(self.__class__.__name__)
		fmtstr+='\t\tFilter coefficients = {0}\n'.format(self.filterCoeff)
		fmtstr+='\t\tDecimation = {0}\n'.format(self.decimate)

		return fmtstr