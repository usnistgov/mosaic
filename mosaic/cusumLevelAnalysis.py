"""
	Analyze a multi-step event with the CUSUM algorithm

	:Created:	2/10/2015
 	:Author: 	Kyle Briggs <kbrig035@uottawa.ca>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
				2/12/15 		AB 	Updated metadata representation to be consistent 
									with stepResponseAnalysis and multiStateAnalysis
                2/10/15         KB  Initial version
"""
import commonExceptions
import metaEventProcessor
import mosaic.utilities.util as util
import mosaic.utilities.fit_funcs as fit_funcs
import sys
import math

import numpy as np


class InvalidEvent(Exception):
	pass


class datblock:
	"""
		Smart data block that holds a time-series of data and keeps track
		of its mean and SD.
	"""
	def __init__(self, dat):
		self.data=dat
		self.mean=util.avg(dat)
		self.sd=util.sd(dat)


class cusumLevelAnalysis(metaEventProcessor.metaEventProcessor):
	"""
		Implements the CUSUM algorithm (used by OpenNanopore for example) in MOSAIC. This approach sacrifices including system information in the analysis in favor of much faster fitting of single- and multi-level events.

                Some known issues with CUSUM:

                1. If the duration of a sub-event is shorter than a few RC rise times, the averaging will underestimate the extent of the current change. I have not yet found a satisfactory solution for this issue, but for longer events CUSUM should achieve very similar output to the fitting employed elsewhere in MOSAIC.
                2. CUSUM assumes an instantaneous transition between current states. As a result, if the RC rise time of the system is large, CUSUM can trigger and detect intermediate states during the change time. This can usually be mitigated by playing with the algorithm sensitivity settings.
                3. If the event is very long, CUSUM will eventually trigger even if there is no real change, leading to artificially high nStates values for an event. This is a consequence of using a statistical t-test which can have false positives, and can in some cases be mitigated by reducing the sensitivity.

                To use it requires two settings:

                .. code-block:: javascript

	                "cusumLevelAnalysis": {
						"StepSize": 3.0, 
						"Threshold": 3.0
                        }

                StepSize is the number of baseline standard deviations are considered significant (3 is usually a good starting point). Threshold is the sensitivity of the algorithm, (lower is more sensitive, a good starting point is to set it equal to StepSize). CUSUM will detect jumps that are smaller than StepSize, but they will have to be sustained longer. Threshold can be thought of, very roughly, as roughly proportional to the length of time a subevent must be sustained for it to be detected.

                You can read about the algorithm here: http://pubs.rsc.org/en/Content/ArticleLanding/2012/NR/c2nr30951c#!divAbstract
	"""
	def _init(self, **kwargs):
		"""
			Initialize the single step analysis class.
		"""
		# initialize the object's metadata (to -1) as class attributes
		self.mdOpenChCurrent=-1
		self.mdCurrentStep=[-1]

		self.mdNStates=-1

		self.mdBlockDepth=[-1]

		self.mdEventDelay=[-1]

		self.mdEventStart=-1
		self.mdEventEnd=-1
		
		self.mdResTime = -1

		self.mdAbsEventStart = -1

		self.nStates=-1

		# Settings for detection of changed in current level
		try:
			self.StepSize=float(self.settingsDict.pop("StepSize", 3.0))
			self.Threshold=int(self.settingsDict.pop("Threshold", 3.0))
		except ValueError as err:
			raise commonExceptions.SettingsTypeError( err )


	###########################################################################
	# Interface functions implemented starting here
	###########################################################################
	def _processEvent(self):
		"""
			This function implements the core logic to analyze one single step-event.
		"""
		try:
			# Run CUSUM to detect changed in level
			self.__FitEvent()
		except:
			raise

	def mdList(self):
		"""
			Return a list of meta-data from the analysis of single step events. We explicitly
			control the order of the data to keep formatting consistent. 				
		"""
		return [
					self.mdProcessingStatus, 
					self.mdOpenChCurrent,
					self.mdNStates, 
					self.mdCurrentStep,
					self.mdBlockDepth,
					self.mdEventStart,
					self.mdEventEnd,
					self.mdEventDelay,
					self.mdResTime,
					self.mdAbsEventStart
				]
		
	def mdHeadingDataType(self):
		"""
			Return a list of meta-data tags data types.
		"""
		return [
					'TEXT', 
					'REAL', 
					'INTEGER',
					'REAL_LIST',
					'REAL_LIST',
					'REAL',
					'REAL',
					'REAL_LIST',
					'REAL',
					'REAL'
				]

	def mdHeadings(self):
		"""
			Explicity set the metadata to print out.
		"""
		return [
					'ProcessingStatus', 
					'OpenChCurrent', 
					'NStates',
					'CurrentStep',
					'BlockDepth',
					'EventStart', 
					'EventEnd', 
					'EventDelay', 
					'ResTime', 
					'AbsEventStart'
				]

	def mdAveragePropertiesList(self):
		"""
			Return a list of meta-data properties that will be averaged 
			and displayed at the end of a run. 
		"""
		pass

	def formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		fmtstr=""

		fmtstr+='\tEvent processing settings:\n\t\t'
		fmtstr+='Algorithm = {0}\n\n'.format(self.__class__.__name__)
		
		fmtstr+='\t\tJump Size  = {0}\n'.format(self.StepSize)
		fmtstr+='\t\tCUSUM Threshold (rel. err in leastsq)  = {0}\n'.format(self.Threshold)

		return fmtstr

	###########################################################################
	# Local functions
	###########################################################################
	def __FitEvent(self):
		try:
			dt = 1000./self.Fs 	# time-step in ms.
			edat=self.dataPolarity*np.asarray( self.eventData,  dtype='float64' ) #make data into an array and make it abs val
			

			# control numpy error reporting
			np.seterr(invalid='ignore', over='ignore', under='ignore')

                        #set up variables for the main CUSUM loop
			
			logp = 0 #instantaneous log-likelihood for positive jumps
			logn = 0 #instantaneous log-likelihood for negative jumps
			cpos = np.zeros(len(edat), dtype='float64') #cumulative log-likelihood function for positive jumps
			cneg = np.zeros(len(edat), dtype='float64') #cumulative log-likelihood function for negative jumps
			gpos = np.zeros(len(edat), dtype='float64') #decision function for positive jumps
			gneg = np.zeros(len(edat), dtype='float64') #decision function for negative jumps
			edges = np.array([0], dtype='int64') #initialize an array with the position of the first subevent - the start of the event
			anchor = 0 #the last detected change
			length = len(edat)
			k = 0
			self.nStates = 0
                        while k < length-1: 
                                k += 1
                                mean = np.average(edat[anchor:k+1]) #get local mean value since last current change
                                variance = np.var(edat[anchor:k+1]) #get local variance since last current change
                                if (variance == 0):                 # with low-precision data sets it is possible that two adjacent values are equal, in which case there is zero variance for the two-vector of sample if this occurs next to a detected jump. This is very, very rare, but it does happen.
                                        variance = self.baseSD*self.baseSD # in that case, we default to the local baseline variance, which is a good an estimate as any.
                                logp = self.StepSize*self.baseSD/variance * (edat[k] - mean - self.StepSize*self.baseSD/2.) #instantaneous log-likelihood for current sample assuming local baseline has jumped in the positive direction
                                logn = -self.StepSize*self.baseSD/variance * (edat[k] - mean + self.StepSize*self.baseSD/2.) #instantaneous log-likelihood for current sample assuming local baseline has jumped in the negative direction
                                cpos[k] = cpos[k-1] + logp #accumulate positive log-likelihoods
                                cneg[k] = cneg[k-1] + logn #accumulate negative log-likelihoods
                                gpos[k] = max(gpos[k-1] + logp, 0) #accumulate or reset positive decision function 
                                gneg[k] = max(gneg[k-1] + logn, 0) #accumulate or reset negative decision function
                                if (gpos[k] > self.Threshold or gneg[k] > self.Threshold):
                                        if (gpos[k] > self.Threshold): #significant positive jump detected
                                                jump = anchor + np.argmin(cpos[anchor:k+1]) #find the location of the start of the jump
                                                edges = np.append(edges, jump)
                                                self.nStates += 1
                                        if (gneg[k] > self.Threshold): #significant negative jump detected
                                                jump = anchor + np.argmin(cneg[anchor:k+1])
                                                edges = np.append(edges, jump)
                                                self.nStates += 1
                                        anchor = k
                                        cpos[0:len(cpos)] = 0 #reset all decision arrays
                                        cneg[0:len(cpos)] = 0
                                        gpos[0:len(cpos)] = 0
                                        cneg[0:len(cpos)] = 0
                        edges = np.append(edges, len(edat)) #mark the end of the event as an edge
                        self.nStates += 1
			cusum = dict()
			if (self.nStates < 3):
                                self.rejectEvent('eInvalidStates')
                        else:
                                cusum['CurrentLevels'] = [np.average(edat[edges[i]:edges[i+1]]) for i in range(self.nStates)] #detect current levels during detected sub-events
                                cusum['EventDelay'] = edges * dt #locations of sub-events in the data
                                self.__recordevent(cusum)

		except KeyboardInterrupt:
			self.rejectEvent('eFitUserStop')
			raise
		except InvalidEvent:
			self.rejectEvent('eInvalidEvent')
		except:
	 		self.rejectEvent('eFitFailure')
	 		raise


	def __recordevent(self, cusum):
		dt = 1000./self.Fs 	# time-step in ms.

		if self.nStates<3:
			self.rejectEvent('eInvalidStates')
		else:
			self.mdOpenChCurrent 	        = 0.5*(cusum['CurrentLevels'][0] + cusum['CurrentLevels'][self.nStates-1]) #this assumes that the event returns to baseline after
			self.mdCurrentStep		= np.diff(np.hstack(([self.mdOpenChCurrent], cusum['CurrentLevels'])))[1:] #these current levels are relative to the open state
			
			self.mdNStates			= self.nStates - 1 #this does not count padding as separate states. Note also that states can be triggered inside the padding

			self.mdBlockDepth 		= 1. - self.mdCurrentStep/self.mdOpenChCurrent #percentage blockage of each state

			self.mdEventDelay		= cusum['EventDelay'][1:-1] # first and last states (or baseline) are removed

			self.mdEventStart		= self.mdEventDelay[0] #the first nonzero event
			self.mdEventEnd			= self.mdEventDelay[-1] #the last non zero event, this assumes no events triggered in the padding

			self.mdResTime			= self.mdEventEnd - self.mdEventStart 

			self.mdAbsEventStart	= self.mdEventStart + self.absDataStartIndex * dt


			if math.isnan(self.mdOpenChCurrent):
				self.rejectEvent('eInvalidOpenChCurr')
