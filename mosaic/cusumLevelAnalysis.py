"""
	Analyze a multi-step event with the CUSUM algorithm

	:Created:	4/18/2013
 	:Author: 	Kyle Briggs (kbrig035@uottawa.ca) borrowing heavily from Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		1/7/14		AB  Save the number of states in an event to the DB using the mdNStates column
		12/31/14 	AB 	Changed multi-state function to include a separate tau for 
						each state following Balijepalli et al, ACS Nano 2014.
		12/30/14	JF	Removed min/max constraint on tau
		11/7/14 	AB 	Error codes describing event rejection are now more specific.
		11/6/14 	AB 	Fixed a bug in the event fitting logic that prevents the
						analysis of long states.
		8/21/14		AB 	Added AbsEventStart and BlockDepth (constructed from mdCurrentStep
						and mdOpenChCurrent) metadata.
		5/17/14		AB  Modified md interface functions for metaMDIO support
		9/26/13		AB	Initial version
"""
import commonExceptions
import metaEventProcessor
import mosaic.utilities.util as util
import mosaic.utilities.fit_funcs as fit_funcs
import sys
import math

import numpy as np
import scipy.optimize

from lmfit import minimize, Parameters, Parameter, report_errors, Minimizer

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
		Analyze a multi-step event that contains two or more states using the CUSUM algorithm. This method includes system 
		information in the analysis, specifically the filtering effects (throught the RC constant)
		of either amplifiers or the membrane/nanopore complex. The analysis generates several 
		parameters that are stored as metadata including:
			1. Blockade depth: the ratio of the open channel current to the blocked current
			2. Residence time: the time the molecule spends inside the pore
			3. Tau: the 1/RC of the response to a step input (e.g. the entry or exit of the
				molecule into or out of the nanopore).

		When an event cannot be analyzed, the blockade depth, residence time and rise time are set to -1.
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

		self.mdRCConst=[-1]

		self.mdAbsEventStart = -1

		self.mdRedChiSq=-1

		self.nStates=-1

		# Settings for single step event processing
		# settings for gaussian fits
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
			# Fit the system transfer function to the event data
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
			cpos = np.array([0. for i in range(0,len(edat))], dtype='float64') #cumulative log-likelihood function for positive jumps
			cneg = np.array([0. for i in range(0,len(edat))], dtype='float64') #cumulative log-likelihood function for negative jumps
			gpos = np.array([0. for i in range(0,len(edat))], dtype='float64') #decision function for positive jumps
			gneg = np.array([0. for i in range(0,len(edat))], dtype='float64') #decision function for negative jumps
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
                                self.RejectEvent('eInvalidStates')
                        else:
                                cusum['CurrentLevels'] = [np.average(edat[edges[i]:edges[i+1]]) for i in range(self.nStates)]
                                cusum['EventDelay'] = edges * dt
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
			self.mdCurrentStep		= cusum['CurrentLevels'] #these are absolute current levels, not changes with respect to baseline
			
			self.mdNStates			= self.nStates #this counts both paddings as separate states. Note also that states can be triggered inside the padding

			self.mdBlockDepth 		= 1. - self.mdCurrentStep/self.mdOpenChCurrent #percentage blockage of each state

			self.mdEventDelay		= cusum['EventDelay'] # 0 and the last sample in the padding are included in this list

			self.mdEventStart		= cusum['EventDelay'][1] #the first nonzero event
			self.mdEventEnd			= cusum['EventDelay'][self.nStates-1] #the second last event, this assumes no events triggered in the padding

			self.mdResTime			= self.mdEventEnd - self.mdEventStart 

			self.mdAbsEventStart	= self.mdEventStart + self.absDataStartIndex * dt

