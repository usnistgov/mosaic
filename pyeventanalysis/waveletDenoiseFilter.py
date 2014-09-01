"""
	Implementation of a wavelet based denoising filter

	Author: Arvind Balijepalli
	Created: 8/31/2014

	ChangeLog:
		8/31/14		AB	Initial version
"""
import numpy as np 
import scipy.signal as sig
import pywt

import metaIOFilter

class waveletDenoiseFilter(metaIOFilter.metaIOFilter):
	"""
	"""
	def _init(self, **kwargs):
		"""
			Keyword Args:
			In addition to metaIOFilter.__init__ args,
				wavelet		the type of wavelet
				level		wavelet level
				threshold	threshold type
				sdOpenCurr	signal noise standard deviation (can be the same as sdOpenCurr in eventSegment)
		"""
		try:
			self.waveletType=str(kwargs['wavelet'])
			self.waveletLevel=int(kwargs['level'])
			self.waveletThresholdType=str(kwargs['thresholdType'])
			self.waveletThresholdSubType=str(kwargs['thresholdSubType'])
			self.sdOpenCurr=float(kwargs['sdOpenCurr'])
		except KeyError:
			print "Missing mandatory arguments 'wavelet', 'level' or 'threshold'"

		self.thrtypedict=	{
								'soft' 		: pywt.thresholding.soft,
								'hard' 		: pywt.thresholding.hard,
								'greater' 	: pywt.thresholding.greater,
								'less'		: pywt.thresholding.less
							}

	def filterData(self, icurr, Fs):
		"""
			Denoise self.eventData
		"""
		# self.eventData=icurr
		self.Fs=Fs

		if self.sdOpenCurr==-1:
			sd=np.std(icurr)
		else:
			sd=self.sdOpenCurr

		thrtype=self.thrtypedict[self.waveletThresholdType]

		wcoeff = pywt.wavedec(icurr, self.waveletType, level=self.waveletLevel)
		threshold=sd*np.sqrt(2*np.log2(len(icurr)))
		newcoeff = map(lambda x: thrtype(x, threshold), wcoeff)

		self.eventData = pywt.waverec( newcoeff, self.waveletType)

	def formatsettings(self):
		"""
			Return a formatted string of filter settings
		"""
		fmtstr=""

		fmtstr+='\tFilter settings: \n'
		fmtstr+='\t\tFilter type = {0}\n'.format(self.__class__.__name__)
		fmtstr+='\t\tWavelet type = {0}\n'.format(self.waveletType)
		fmtstr+='\t\tWavelet level = {0}\n'.format(self.waveletLevel)
		fmtstr+='\t\tWavelet threshold type = {0}\n'.format(self.waveletThresholdType)
		fmtstr+='\t\tWavelet threshold sub-type = {0}\n'.format(self.waveletThresholdSubType)
		fmtstr+='\t\tDecimation = {0}\n'.format(self.decimate)

		return fmtstr