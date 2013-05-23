"""
	Author: 	Arvind Balijepalli
	Created:	7/16/2012

	ChangeLog:
		8/24/12 	AB 	Settings are read from a settings file and passed
						to this class as the settingsDict class attr set
						by metaEventProcessor.
		7/16/12		AB	Initial version
"""
import commonExceptions
import metaEventProcessor
import util
import sys

import numpy as np
import scipy.optimize

import uncertainties

class datblock:
	"""
		Smart data block that holds a time-series of data and keeps track
		of its mean and SD.
	"""
	def __init__(self, dat):
		self.data=dat
		self.mean=util.avg(dat)
		self.sd=util.sd(dat)


class singleStepEvent(metaEventProcessor.metaEventProcessor):
	"""
		Analyze a single-step event characteristic of PEG blockades. Two relevant pieces
		of information are measured for each event and stored as metadata:
			1. Blockade depth: the ratio of the open channel current to the blocked current
			2. Residence time: the time the molecule spends inside the pore

		When an event cannot be analyzed, the blockade depth and residence time are set to -1.

	"""
	def __init__(self, icurr, Fs, **kwargs):
		"""
			Initialize the single step analysis class.
		"""
		# call the base class initializer. This sets self.eventData and self.Fs
		super(singleStepEvent, self).__init__(icurr,Fs, **kwargs)

		# initialize the object's metadata (to -1) as class attributes
		self.mdOpenChCurrent=-1
		self.mdBlockedCurrent=-1

		self.mdEventStart=-1
		self.mdEventEnd=-1
		
		self.mdBlockDepth = -1
		self.mdResTime = -1

		self.mdTempA12=-1

		# Settings for single step event processing
		# settings for gaussian fits
		try:
			self.histBinSz=float(self.settingsDict.pop("binSize", 1.0))
			self.histPad=int(self.settingsDict.pop("histPad", 10))
			self.maxFitIters=int(self.settingsDict.pop("maxFitIters", 5000))
		
			# rejection criterion settings
			self.a12Ratio=float(self.settingsDict.pop("a12Ratio", 1.e6))	# max ratio of density between open and blocked states
			self.minEvntTime=float(self.settingsDict.pop("minEvntTime", 20.e-6))

			# data conditioning settings
			self.datPad=int(self.settingsDict.pop("minDataPad", 50))
		except ValueError as err:
			raise commonExceptions.SettingsTypeError( err )


	###########################################################################
	# Interface functions implemented starting here
	###########################################################################
	def processEvent(self):
		"""
			This function implements the core logic to analyze one single step-event.
		"""
		try:
			# Fit a sum of two gaussians to locate the open channel 
			# and blocked channel states
			self.__blockadeDepthFit()

			# If the blockade depth was calculated properly,
			# the processing status should be normal. Proceed
			# to calculate the residence time.
			self.__residenceTime()
		except:
			raise

	def mdList(self):
		"""
			Return a list of meta-data from the analysis of single step events. We explicitly
			control the order of the data to keep formatting consistent. 				
		"""
		return [
					self. mdProcessingStatus, 
					self.mdOpenChCurrent, 
					self.mdBlockedCurrent,
					self.mdEventStart,
					self.mdEventEnd,
					self.mdBlockDepth,
					self.mdResTime,
					self.mdTempA12
				]
		

	def mdHeadings(self):
		"""
			Explicity set the metadata to print out.
		"""
		return ['ProcessingStatus', 'OpenChCurrent (pA)', 'BlockedCurrent (pA)','EventStart', 'EventEnd', 'BlockDepth', 'ResTime (ms)', 'A12TempOutput' ]

	def mdAveragePropertiesList(self):
		"""
			Return a list of meta-data properties that will be averaged 
			and displayed at the end of a run. 
		"""
		return ['mdBlockDepth']

	def formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		fmtstr=""

		fmtstr+='\tEvent processing settings:\n\t\t'
		fmtstr+='Algorithm = {0}\n\n'.format(self.__class__.__name__)
		fmtstr+='\t\tData conditioning: pad data size = {0} points\n\n'.format(self.datPad)
		fmtstr+='\t\tHistogram bin size = {0} pA\n'.format(self.histBinSz)
		fmtstr+='\t\tHistogram padding = {0} points\n\n'.format(self.histPad)
		
		fmtstr+='\t\tPore current fit: max. iterations  = {0}\n\n'.format(self.maxFitIters)

		fmtstr+='\t\tPore current fit rejection: peak ratio limit (A12)  = {0}\n'.format(self.a12Ratio)
		fmtstr+='\t\tPore current fit rejection: min. event time = {0} us\n'.format(1.e6*self.minEvntTime)

		return fmtstr

	###########################################################################
	# Local functions
	###########################################################################
	def __currentEstimate(self, dat, blockSz):
		"""
			Return a current list by partitioning the data
			into blocks and concatenating data from blocks with 
			the most common mean value.

			Args:
				dat 	data to process 
				blockSz	block size in points
		"""
		if len(dat) < 2*blockSz or blockSz == 0 or len(dat) < 10 :
			self.rejectEvent('eShortEvent')
			return
		#print len(dat), blockSz
		# partition the data into sub-blocks that have a length
		# of the minimum of 50 elements or len(dat)/10, to guarantee
		# at least 10 blocks
		dblock=[ datblock(d) for d in util.partition( dat, blockSz ) ]

		# Find the sub-block with the most common mean. Assuming 
		# most of the pre and post event data is at the open channel 
		# conductance, this will filter out spurious events
		c = util.commonest( [ round(d.mean) for d in dblock ] )

		# Gather data from all the sub-blocks that match the most 
		# common mean, collect them into one list and return them
		# to the calling function
		r=[]
		[ r.extend(d.data) for d in dblock if c==round(d.mean) ]
		
		return r 

	def __blockadeDepthFit(self):
		"""
		"""
		# First get first order estimates of the open channel and blocked state currents
		# We will use these to guide the final fits.
		pre=self.__currentEstimate(self.eventData[:self.eStartEstimate-self.datPad], min(50, int(len(self.eventData[:self.eStartEstimate-self.datPad])/10.0)) )
		post=self.__currentEstimate(self.eventData[self.eEndEstimate+self.datPad:], min(50, int(len(self.eventData[self.eEndEstimate+self.datPad:])/10.0)) )
		
		bcCurrEst=self.__meanBlockedCurrent(self.eventData[self.eStartEstimate-self.datPad:self.eEndEstimate+self.datPad], 2.0)

		if self.mdProcessingStatus=='normal':
			ocCurrEst=util.flat2( [pre, post] )
			self.__fitsumgauss( ocCurrEst+bcCurrEst, util.avg(ocCurrEst), np.std(ocCurrEst), util.avg(bcCurrEst) )

	def __fitsumgauss(self, cleandat, oc, ocsd, bc):
		"""
		"""
		np.seterr(invalid='raise', over='raise')

		# keep track of the current polarity
		sign=np.sign(util.avg(cleandat))

		# use the absolute current value to simplify the calc. 
		# We put the sign back in the current when returning the results
		evntabs=np.abs(cleandat)

		# Histogram and fit
		try:
			# PDF of event data
			ehist,bins=np.histogram(
				evntabs, 
				bins=np.arange(np.min(evntabs)-self.histPad,np.max(evntabs)+self.histPad, self.histBinSz), 
				density=True
			)

			popt, pcov = scipy.optimize.curve_fit(
					self.__sumgauss, 
					[ b+(0.5*self.histBinSz) for b in bins[:-1] ], 
					ehist, 
					p0=[np.max(ehist), np.abs(bc), np.abs(ocsd), np.max(ehist), np.abs(oc), np.abs(ocsd)], 
					maxfev=self.maxFitIters
				)
		except BaseException, err:
			#print oc, ocsd, bc, len(cleandat)
			# reject event if it can't be fit
			self.rejectEvent('eBDFit')
			return
			

		try:
			# If the fit was successful, determine if the parameters are acceptable
			if np.abs(popt[3]/popt[0]) > self.a12Ratio or popt[1]/popt[4] < 0 or popt[3]/popt[0] < 0 or np.abs(popt[4]-popt[1]) < 2.75*popt[5]:
				self.rejectEvent('eBDPeak')
				return
			elif np.abs(popt[2]) > 2*np.abs(popt[5]):
				self.rejectEvent('eEvntNoise')
				return
		except:
			# unspecified fitting error
			self.rejectEvent('eBDFit')

		# One last test: make sure we have a flat region at the base of the event
		# to avoid underestimating the blockade depth.
		if len( util.selectS( 
					self.eventData[self.eStartEstimate-self.datPad:self.eEndEstimate+self.datPad],
					2,
					sign*popt[1],
					popt[2]
				) ) < int(self.minEvntTime*self.Fs):
			self.rejectEvent('eShortEvent')
			return

		# The event is good, save it.
		try:
			self.mdOpenChCurrent=uncertainties.ufloat((sign*round(popt[4],4), round(np.abs(popt[5]),4)))
			self.mdBlockedCurrent=uncertainties.ufloat((sign*round(popt[1],4), round(np.abs(popt[2]),4)))
			bd=self.mdBlockedCurrent/self.mdOpenChCurrent
			self.mdBlockDepth=uncertainties.ufloat(( round(uncertainties.nominal_value(bd),5), round(uncertainties.std_dev(bd),6) ))
			
			self.mdTempA12=uncertainties.ufloat(( popt[0], popt[3] ))
			#print 'normal\t'+str(s1)+'\t'+str(s2)+'\t'+'0.0+/-0.0'+'\t'+'0.0+/-0.0'+'\t'+str(bd1)+'\t'+'0.0+/-0.0'+'\t'+str(a12)
		except AssertionError:
			self.rejectEvent('eBDFit')

	def __sumgauss(self, x, a1, m1, s1, a2, m2, s2):
		return a1 * np.exp( (-(x-m1)**2)/(2*s1*s1) ) + a2 * np.exp( (-(x-m2)**2)/(2*s2*s2) )
		
	def __meanBlockedCurrent(self, dat, nsigma):
		"""
			Args:
				dat 	data to process 
				nsigma	number of baseline open channel conductance SD. This 
						parameter is used as the criterion to decide if a data point
						is included in the open channel mean.
		"""
		if len(dat) == 0:
			self.rejectEvent('eShortEvent')
			return

		m1=np.min([ abs(d) for d in dat ])
		
		# Find the minimum current point and first get all currents within 2*nsigma of that current
		blcurr=[ m for m in dat  if np.abs(m) < m1+(2*nsigma*self.baseSD) ]

		return blcurr
		

	def __residenceTime(self):
		"""
			Calculate the residence time of a single step event. 
		"""
		# if previous errors were detected, the 
		# event is already rejected, don't process it 
		# any further
		if self.mdProcessingStatus != 'normal':
			return

		# set numpy warning handling. 
		# raise divide by zero errors so we 
		# can catch them
		np.seterr(divide='raise')

		ocmu=np.abs(uncertainties.nominal_value(self.mdOpenChCurrent))
		ocsd=np.abs(uncertainties.std_dev(self.mdOpenChCurrent))
		
		bcmu=np.abs(uncertainties.nominal_value(self.mdBlockedCurrent))
		bcsd=np.abs(uncertainties.std_dev(self.mdBlockedCurrent))

		# refine the start estimate
		idx=self.eStartEstimate

		try:
			while np.abs((np.abs(self.eventData[idx])-ocmu)/ocsd) > 5.0:
				idx-=1
			
			# Set the start point
			self.mdEventStart=idx+1

			# Next move the count forward so we are in the blocked channel region of the pulse
			while np.abs((np.abs(self.eventData[idx])-bcmu)/bcsd) > 0.5:
				idx+=1

			# Search for the event end. 7*sigma allows us to prevent false 
			# positives
			while np.abs((np.abs(self.eventData[idx])-bcmu)/bcsd) < 7.0:
				idx+=1

			# Finally backtrack to find the true event end
			while np.abs((np.abs(self.eventData[idx])-bcmu)/bcsd) > 5.0:
				idx-=1
		except ( IndexError, FloatingPointError ):
			self.rejectEvent('eResTime')
			return

		self.mdEventEnd=idx-1

		# residence time in ms
		self.mdResTime=1000.*((self.mdEventEnd-self.mdEventStart)/float(self.Fs))

