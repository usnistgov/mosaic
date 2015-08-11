"""
	Implementation of a wavelet based denoising filter

	:Created: 8/31/2014
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:Author: Arvind Balijepalli
	:ChangeLog:
	.. line-block::
		8/31/14		AB	Initial version
"""
import numpy as np 
import scipy.signal as sig
import pywt

import metaIOFilter

class waveletDenoiseFilter(metaIOFilter.metaIOFilter):
	"""
		:Keyword Args:
			In addition to metaIOFilter args,
				- `wavelet` :		the type of wavelet
				- `level` :		wavelet level
				- `threshold` :	threshold type
	"""

	def _init(self, **kwargs):
		"""
		"""	
		try:
			self.waveletType=str(kwargs['wavelet'])
			self.waveletLevel=int(kwargs['level'])
			self.waveletThresholdType=str(kwargs['thresholdType'])
			self.waveletThresholdSubType=str(kwargs['thresholdSubType'])

			self.maxWaveletLevel=self.waveletLevel
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
			Denoise an ionic current time-series and store it in self.eventData

			:Parameters:
				- `icurr` :	ionic current in pA
				- `Fs` :	original sampling frequency in Hz
		"""
		# self.eventData=icurr
		self.Fs=Fs

		# Set up the wavelet
		w=pywt.Wavelet(self.waveletType)

		# Calculate the maximum wavelet level for the data length
		self.maxWaveletLevel=pywt.dwt_max_level(len(icurr), filter_len=w.dec_len)

		# Perform a wavelet decomposition to the specified level
		wcoeff = pywt.wavedec(icurr, w, mode='sym', level=self.waveletLevel)

		# Perform a simple threshold by setting all the detailed coefficients
		# up to level n-1 to zero
		thresh=np.std(wcoeff[-1])*self._thselect(wcoeff, self.waveletThresholdSubType)
		thrfunc=self.thrtypedict[self.waveletThresholdType]

		# print thresh, np.std(wcoeff[-1])
		wcoeff[1:] = [ thrfunc(wc, thresh) for wc in wcoeff[1:] ]
		# for i in range(1, self.waveletLevel):
		# 	wcoeff[-i]=np.zeros(len(wcoeff[-i]))

		# Reconstruct the signal with the thresholded wavelet coefficients
		self.eventData = pywt.waverec(wcoeff, self.waveletType, mode='sym')

	def _thselect(self, dat, thtype):
		"""
			A python port of Matlab thselect.m
		"""
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
		except KeyError, err:
			print "Thresholding algorithm '" + thtype + "' is not available. Using default threshold (sqtwolog).\n"
			# default
			self.waveletThresholdSubType='sqtwolog'
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

if __name__ == '__main__':
	import csv
	from os.path import expanduser

	root=expanduser('~')+'/Research/Experiments/AnalysisTools/Wavelet Denoising/waveletsteps/'
	rawfile=root+'DenoisedSym5Long/testEventPartition1.csv'
	rawdat=[]
	with open(rawfile, 'rb') as eventfile:
		eventreader = csv.reader(eventfile, delimiter=',')
		for row in eventreader:
			# rawdat+=[float(row[1])]
			rawdat+=[float(row[0])]

	
	wavefilter=waveletDenoiseFilter(
				wavelet='sym5', 
				level=5, 
				thresholdType='soft', 
				thresholdSubType='minimaxi', 
				sdOpenCurr='-1'
			)
	wavefilter.filterData(rawdat, 1000)
	print wavefilter.formatsettings()
	np.savetxt(root+'DenoisedSym5Long/testEventPartition1_denoised.csv', np.asarray(wavefilter.filteredData), delimiter=",")
	




	# rawdatpad=np.lib.pad(rawdat, (0,1024-len(rawdat)), 'constant')
	# print len(rawdatpad)
	# sym5 = pywt.Wavelet('sym5')
	# print sym5
	# ca1, cd5, cd4, cd3, cd2, cd1 = pywt.wavedec(rawdat, 'sym5', mode='sym', level=5)
	# coeff = pywt.wavedec(rawdat, 'sym5', mode='sym', level=5)
	# print np.array(coeff).shape

	# np.savetxt(root+'cd1.csv', np.asarray(cd1), delimiter=",")
	# np.savetxt(root+'cd2.csv', np.asarray(cd1), delimiter=",")
	# np.savetxt(root+'cd3.csv', np.asarray(cd1), delimiter=",")
	# np.savetxt(root+'cd4.csv', np.asarray(cd1), delimiter=",")
	# np.savetxt(root+'cd5.csv', np.asarray(cd1), delimiter=",")
	# np.savetxt(root+'ca1.csv', np.asarray(cd1), delimiter=",")

	# mcd1=np.zeros(len(cd1))
	# mcd2=np.zeros(len(cd2))
	# mcd3=np.zeros(len(cd3))
	# mcd4=np.zeros(len(cd4))

	# for i in range(1,5):
	# 	coeff[-i]=np.zeros(len(coeff[-i]))

	# print coeff
	# # rec=pywt.waverec([ca1, cd5, mcd4, mcd3, mcd2, mcd1], sym5, mode='sym')
	# rec=pywt.waverec(coeff, sym5, mode='sym')
	# np.savetxt(root+'rec_event.csv', np.asarray(rec), delimiter=",")

