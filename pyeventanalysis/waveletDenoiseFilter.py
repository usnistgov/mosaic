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
		# threshold=sd*np.sqrt(2*np.log2(len(icurr)))
		threshold=sd*self._thselect(icurr, self.waveletThresholdSubType)
		newcoeff = map(lambda x: thrtype(x, threshold), wcoeff)

		self.eventData = pywt.waverec( newcoeff, self.waveletType)

	def _thselect(self, dat, thtype):
		def _rigrsure(x, n):
			sx2 = np.sort(np.abs(x))**2
			risks = (n-(2*np.arange(1,n+1))+(np.cumsum(sx2)+np.arange(n-1,-1,-1)*sx2))/n
			print risks
			[risk,best] = np.min(risks)
			return np.sqrt(sx2[best])

		def _heursure(x, n):
			hthr = np.sqrt(2*np.log(n))
			eta = (np.linalg.norm(x)**2-n)/n
			crit = (np.log(n)/np.log(2))**(1.5)/np.sqrt(n)
			if eta < crit:
				thr = hthr
			else:
				thr = np.min(self._thselect(x,'rigrsure'),hthr)

			return thr

		def _sqtwolog(x, n):
			return np.sqrt(2*np.log(n));

		def _minimaxi(x, n):
			if n <= 32:
				thr = 0
			else:
				thr = 0.3936 + 0.1829*(np.log(n)/np.log(2))
			
			return thr

		try:
			thalgo={
					# 'rigrsure' 	: _rigrsure, 
					# 'heursure'	: _heursure,
					'sqtwolog'	: _sqtwolog,
					'minimaxi'	: _minimaxi
			 	}[thtype]
			return thalgo(dat, len(dat))
		except KeyError:
			# default
			return _sqtwolog(dat, len(dat))

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