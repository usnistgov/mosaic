# -*- coding: utf-8 -*-
"""
	Analyze a multi-step event with the CUSUM+ algorithm

	:Created:	2/10/2015
 	:Author: 	Kyle Briggs <kbrig035@uottawa.ca>
	:License:	See LICENSE.TXT
	:ChangeLog:             
	.. line-block::      
				8/24/15 	AB 	Rename algorithm to CUSUM+   
				3/20/15 	AB 	Added a new metadata column (mdStateResTime) that saves the residence time of each state to the database.
				3/18/15		KB	Implemented rise time skipping
				3/17/15		KB	Implemented adaptive threshold
				2/12/15		AB	Updated metadata representation to be consistent with stepResponseAnalysis and multiStateAnalysis
				2/10/15		KB	Initial version
"""
import commonExceptions
import metaEventProcessor
import mosaic.utilities.util as util
import mosaic.utilities.mosaicLog as log
import mosaic.utilities.fit_funcs as fit_funcs
import sys
import math
from scipy.optimize import minimize, fsolve
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


class cusumPlus(metaEventProcessor.metaEventProcessor):
	"""
		Implements a modified version of the CUSUM algorithm (used by OpenNanopore for example) in MOSAIC. This approach sacrifices including system information in the analysis in favor of much faster fitting of single- and multi-level events.

		CUSUM+ will detect jumps that are smaller than `StepSize`, but they will have to be sustained longer. Threshold can be thought of, very roughly, as proportional to the length of time a subevent must be sustained for it to be detected. The algorithm will adjust the actual threshold used on a per-event basis in order to minimize false positive detection of current jumps This algorithm is based on code used in OpenNanopore, which you can read about here: http://pubs.rsc.org/en/Content/ArticleLanding/2012/NR/c2nr30951c#!divAbstract


                Some known issues with CUSUM+:

                1. If the duration of a sub-event is shorter than than the MinLength parameter, CUSUM+ will be unable to detect it. CUSUM+ will not detect events within MinLength of a previous event.
                2. CUSUM assumes an instantaneous transition between current states. As a result, if the RC rise time of the system is large, CUSUM+ can trigger and detect intermediate states during the change time. This can be avoided by choosing a number of samples to skip equal to about 2-5RC.
                3. As a consequence of using a statistical t-test, CUSUM can have false positives. The algorithm has an adaptive threshold that tries to minimize the chances of this happening while maintaining good sensitivity (expected number of false positives within an event is less than 1).

                To use it requires four settings:


				.. code-block:: javascript

					"cusumPlus": {
						"StepSize": 3.0, 
						"MinThreshold": 3.0,
						"MaxThreshold": 10.0,
						"MinLength" : 10,
					}

				:Keyword Args:
					In addition to :class:`~mosaic.metaEventProcessor.metaEventProcessor` args,
						- `StepSize` :			The number of baseline standard deviations are considered significant (3 is usually a good starting point).
						- `MinThreshold` :		One of two sensitivity parameters (lower is more sensitive). A good starting point is to set `MinThreshold` equal to `StepSize`.
						- `MaxThreshold` : 		One of two sensitivity parameters (lower is more sensitive). Set `MaxThreshold` about 3x higher than `MinThreshold`.
						- `MinLength` : 		The number of samples to skip after detecting a jump, in order to avoid triggering during the rise time and returning an artificially high number of states. This number of points is also skipped when averaging levels. About 4 times the RC constant of the system is a good starting value.

				:Errors:

					When an event cannot be analyzed, all metadata are set to -1.
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
		self.mdStateResTime=[-1]

		self.mdEventStart=-1
		self.mdEventEnd=-1
		
		self.mdResTime = -1

		self.mdAbsEventStart = -1

		self.mdThreshold=-1

		self.nStates=-1

		# Settings for detection of changed in current level
		try:
			self.StepSize=float(self.settingsDict.pop("StepSize", 3.0))
			self.MinThreshold=float(self.settingsDict.pop("MinThreshold", 2.0))
			self.MaxThreshold=float(self.settingsDict.pop("MaxThreshold", 10.0))
			self.MinLength=float(self.settingsDict.pop("MinLength", 10))
		except ValueError as err:
			raise commonExceptions.SettingsTypeError( err )

                self.mdThreshold = self.MinThreshold

	###########################################################################
	# Interface functions implemented starting here
	###########################################################################
	def _processEvent(self):
		"""
			This function implements the core logic to analyze one single step-event.
		"""
		try:
			# Run CUSUM+ to detect changes in level
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
					self.mdStateResTime,
					self.mdResTime,
					self.mdAbsEventStart,
					self.mdThreshold
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
					'REAL_LIST',
					'REAL',
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
					'StateResTime',
					'ResTime', 
					'AbsEventStart',
					'Threshold'
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
		logObj=log.mosaicLog()


		logObj.addLogHeader( 'Event processing settings:' )
		logObj.addLogText( 'Algorithm = CUSUM+' )
		
		logObj.addLogText( 'Jump Size  = {0}'.format(self.StepSize) )
		logObj.addLogText( 'Min. State Length  = {0}'.format(self.MinLength) )
		logObj.addLogText( 'CUSUM+ Min. Threshold  = {0}'.format(self.MinThreshold) )
		logObj.addLogText( 'CUSUM+ Max. Threshold  = {0}'.format(self.MaxThreshold) )

		return str(logObj)

	###########################################################################
	# Local functions
	###########################################################################
        def __GetThreshold(self, ARL, sigma, mun):
                ARL = 2*ARL #double since we are doing two-sided CUSUM
                f = lambda h: (np.exp(-2.0*mun*(h/sigma+1.166))-1.0+2.0*mun*(h/sigma+1.166))/(2.0*mun*mun)-ARL
                
                if f(self.MinThreshold)*f(self.MaxThreshold) < 0: #if a root exists in the specified range
                        opth, info, ier, mesg = fsolve(f,self.MaxThreshold,full_output=True)
                        if ier==1: #fit success, return the root
                                Threshold = opth[0]
                        else: #fit failure, default to min
                                Threshold = self.MinThreshold
                else: #if no root exists, we use the min value
                        f = lambda h: np.abs((np.exp(-2.0*mun*(h/sigma+1.166))-1.0+2.0*mun*(h/sigma+1.166))/(2.0*mun*mun)-ARL) #absolute value to minimize
                        opth = minimize(f,self.MaxThreshold,bounds=((self.MinThreshold,self.MaxThreshold),)) #Find the min within the requested range
                        if opth.success==False:
                                Threshold = self.MinThreshold #Default to more sensitive
                        else:
                                Threshold = opth.x[0]
                return Threshold

                        
                                
                
	def __FitEvent(self):
		try:
			dt = 1000./self.Fs 	# time-step in ms.
			edat=self.dataPolarity*np.asarray( self.eventData,  dtype='float64' ) #make data into an array and make it abs val

			Threshold = self.__GetThreshold(len(edat),self.StepSize,-self.StepSize/2.0)
                        
			# control numpy error reporting
			np.seterr(invalid='ignore', over='ignore', under='ignore')

                        #set up variables for the main CUSUM+ loop
			
			logp = 0 #instantaneous log-likelihood for positive jumps
			logn = 0 #instantaneous log-likelihood for negative jumps
			cpos = np.zeros(len(edat), dtype='float64') #cumulative log-likelihood function for positive jumps
			cneg = np.zeros(len(edat), dtype='float64') #cumulative log-likelihood function for negative jumps
			gpos = np.zeros(len(edat), dtype='float64') #decision function for positive jumps
			gneg = np.zeros(len(edat), dtype='float64') #decision function for negative jumps
			edges = np.array([0], dtype='int64') #initialize an array with the position of the first subevent - the start of the event
			anchor = 0 #the last detected change
			length = len(edat)
			mean = edat[0]
			variance = self.baseSD * self.baseSD
			k = 0
			self.nStates = 0
			varM = edat[0]
			varS = 0
			mean = edat[0]
                        while k < length-1: 
                                k += 1
                                varOldM = varM #algorithm to calculate running variance, details here: http://www.johndcook.com/blog/standard_deviation/
                                varM = varM + (edat[k] - varM)/float(k+1-anchor)
                                varS = varS + (edat[k] - varOldM) * (edat[k] - varM)
                                variance = varS / float(k+1-anchor)
                                mean = ((k-anchor) * mean + edat[k])/float(k+1-anchor)
                                if (variance == 0):                 # with low-precision data sets it is possible that two adjacent values are equal, in which case there is zero variance for the two-vector of sample if this occurs next to a detected jump. This is very, very rare, but it does happen.
                                        variance = self.baseSD*self.baseSD # in that case, we default to the local baseline variance, which is a good an estimate as any.
                                logp = self.StepSize*self.baseSD/variance * (edat[k] - mean - self.StepSize*self.baseSD/2.) #instantaneous log-likelihood for current sample assuming local baseline has jumped in the positive direction
                                logn = -self.StepSize*self.baseSD/variance * (edat[k] - mean + self.StepSize*self.baseSD/2.) #instantaneous log-likelihood for current sample assuming local baseline has jumped in the negative direction
                                cpos[k] = cpos[k-1] + logp #accumulate positive log-likelihoods
                                cneg[k] = cneg[k-1] + logn #accumulate negative log-likelihoods
                                gpos[k] = max(gpos[k-1] + logp, 0) #accumulate or reset positive decision function 
                                gneg[k] = max(gneg[k-1] + logn, 0) #accumulate or reset negative decision function
                                if (gpos[k] > Threshold or gneg[k] > Threshold):
                                        if (gpos[k] > Threshold): #significant positive jump detected
                                                jump = anchor + np.argmin(cpos[anchor:k+1]) #find the location of the start of the jump
                                                if jump - edges[self.nStates] > self.MinLength:
                                                        edges = np.append(edges, jump)
                                                        self.nStates += 1
                                        if (gneg[k] > Threshold): #significant negative jump detected
                                                jump = anchor + np.argmin(cneg[anchor:k+1])
                                                if jump - edges[self.nStates] > self.MinLength:
                                                        edges = np.append(edges, jump)
                                                        self.nStates += 1
                                        anchor = k
                                        cpos[0:len(cpos)] = 0 #reset all decision arrays
                                        cneg[0:len(cneg)] = 0
                                        gpos[0:len(gpos)] = 0
                                        gneg[0:len(gneg)] = 0
                                        mean = edat[anchor]
                                        varM = edat[anchor]
                                        varS = 0
                        edges = np.append(edges, len(edat)) #mark the end of the event as an edge
                        self.nStates += 1
			cusum = dict()
			if (self.nStates < 3):
                                self.rejectEvent('eInvalidStates')
                        else:
                                minstepflag = 0
                                while minstepflag == 0:
                                        minstepflag = 1
                                        currentlevels = [np.average(edat[edges[i]+self.MinLength:edges[i+1]]) for i in range(self.nStates)] #detect current levels during detected sub-events
                                        toosmall = np.absolute(np.diff(currentlevels)) < self.StepSize*self.baseSD/2
                                        for i in range(len(toosmall)):
                                                if toosmall[i] == True:
                                                        edges = np.delete(edges,i+1)
                                                        minstepflag = 0
                                                        self.nStates -= 1
                                                        break
                        if (self.nStates < 3):
                                self.rejectEvent('eInvalidStates')
                        else:
                                cusum['CurrentLevels'] = currentlevels
                                cusum['EventDelay'] = edges * dt #locations of sub-events in the data
                                cusum['Threshold'] = Threshold #record the threshold used
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
			self.mdCurrentStep		= np.diff(np.hstack(([self.mdOpenChCurrent], cusum['CurrentLevels'][1:]))) #these current levels are relative to the open state
			
			self.mdNStates			= self.nStates - 1 #this does not count padding as separate states. Note also that states can be triggered inside the padding

			self.mdBlockDepth 		= cusum['CurrentLevels'][1:-1]/self.mdOpenChCurrent #percentage blockage of each state

			self.mdEventDelay		= cusum['EventDelay'][1:-1] # first and last states (or baseline) are removed

			self.mdStateResTime 	= np.diff(self.mdEventDelay)

			self.mdEventStart		= self.mdEventDelay[0] #the first nonzero event
			self.mdEventEnd			= self.mdEventDelay[-1] #the last non zero event, this assumes no events triggered in the padding

			self.mdResTime			= self.mdEventEnd - self.mdEventStart 

			self.mdAbsEventStart	= self.mdEventStart + self.absDataStartIndex * dt

			self.mdThreshold = cusum['Threshold']


			if math.isnan(self.mdOpenChCurrent):
				self.rejectEvent('eInvalidOpenChCurr')
