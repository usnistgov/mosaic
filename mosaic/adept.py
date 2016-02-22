# -*- coding: utf-8 -*-
"""
	Analyze a multi-step event 

	:Created:	4/18/2013
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		2/20/16 	AB 	Format settings log.
		12/09/15 	KB 	Added Windows specific optimizations
		8/24/15 	AB 	Rename algorithm to ADEPT.
		8/02/15		JF	Added a new test to reject RC Constants <=0
		4/12/15 	AB 	Refactored code to improve reusability.
		3/20/15 	AB 	Added a maximum event length setting (MaxEventLength) that automatically rejects events longer than the specified value.
		3/20/15 	AB 	Added a new metadata column (mdStateResTime) that saves the residence time of each state to the database.
		3/6/15 		AB 	Added a new test for negative event delays
		3/6/15 		JF	Added MinStateLength to output log
		3/5/15 		AB 	Updated initial state determination to include a minumum state length parameter (MinStateLength).
						Initial state estimates now utilize gradient information for improved state identification.
		1/7/15		AB  Save the number of states in an event to the DB using the mdNStates column
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
import mosaic.utilities.mosaicLog as log
import mosaic.utilities.fit_funcs as fit_funcs
import mosaic.cusumPlus as cusum
import mosaic.settings

import sys
import math

import numpy as np
import scipy.optimize
from scipy.optimize import curve_fit

from lmfit import minimize, Parameters, Parameter, report_errors, Minimizer

class InvalidEvent(Exception):
	pass

class datblock:
	"""
		Smart data block that holds time-series data and keeps track
		of its mean and SD.
	"""
	def __init__(self, dat):
		self.data=dat
		self.mean=util.avg(dat)
		self.sd=util.sd(dat)


class adept(metaEventProcessor.metaEventProcessor):
	"""
		Analyze a multi-step event that contains two or more states. This method includes system 
		information in the analysis, specifically the filtering effects (through the RC constant)
		of either amplifiers or the membrane/nanopore complex. The analysis generates several 
		parameters that are stored as metadata including:
			
		1. Blockade depth: the ratio of the open channel current to the blocked current
		2. Residence time: the time the molecule spends inside the pore
		3. Tau: the RC constant  of the response to a step input (e.g. the entry or exit of the molecule into or out of the nanopore).

		:Keyword Args:
			In addition to :class:`~mosaic.metaEventProcessor.metaEventProcessor` args,
				- `InitThreshold` : 	internal threshold for initial state determination (default: 5.0)
				- `MinStateLength` : 	minimum number of data points required to assign a state within an event (default: 4)
				- `MaxEventLength` :	maximum length (in data points) of events that will be processed (default: 10000)
				- `FitTol` :			fit tolerance for convergence (default: 1.e-7)
				- `FitIters` :			maximum fit iterations (default: 5000)
				- `UnlinkRCConst` :			When True, unlinks the RC constants in the fit function to vary independently of each other. (Default: `True`)

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

		self.mdRCConst=[-1]

		self.mdAbsEventStart = -1

		self.mdRedChiSq=-1

		self.nStates=-1

		# Settings for single step event processing
		# settings for gaussian fits
		try:
			self.FitTol=float(self.settingsDict.pop("FitTol", 1.e-7))
			self.FitIters=int(self.settingsDict.pop("FitIters", 5000))
			self.InitThreshold=float(self.settingsDict.pop("InitThreshold", 5.0))
			self.MinStateLength=float(self.settingsDict.pop("MinStateLength", 4))
			self.MaxEventLength=int(self.settingsDict.pop("MaxEventLength", 10000))
			self.UnlinkRCConst=int(self.settingsDict.pop("UnlinkRCConst", 1))
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
			if (self.eEndEstimate-self.eStartEstimate) > self.MaxEventLength:
				self.rejectEvent("eMaxLength")
			else:
				# Correct the time-series data for polarity
				edat=self.dataPolarity*np.asarray( self.eventData,  dtype='float64' )

				# estimate initial guess for events
				if (self.eEndEstimate-self.eStartEstimate) < 10000:
					initguess=self._characterizeevent(edat, np.abs(util.avg(edat[:10])), self.baseSD, self.InitThreshold, 6.)
				else:
					print (self.eEndEstimate-self.eStartEstimate),
					initguess=self._cusumInitGuess(edat)
	

				# Fit the system transfer function to the event data
				if sys.platform.startswith('win'):
					self.winfitevent(edat,initguess)
				else:
					self.fitevent(edat, initguess)
		except InvalidEvent:
			self.rejectEvent('eInvalidEvent')
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
					self.mdRCConst,
					self.mdAbsEventStart,
					self.mdRedChiSq
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
					'StateResTime', 
					'ResTime', 
					'RCConstant', 
					'AbsEventStart',
					'ReducedChiSquared' 
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
		logObj.addLogText( 'Algorithm = ADEPT' )
		
		logObj.addLogText( 'Max. iterations  = {0}'.format(self.FitIters) )
		logObj.addLogText( 'Fit tolerance (rel. err in leastsq)  = {0}'.format(self.FitTol) )
		logObj.addLogText( 'Unlink RC constants = {0}'.format(bool(self.UnlinkRCConst)) )
		logObj.addLogText( 'Initial partition threshold  = {0} sigma'.format(self.InitThreshold) )
		logObj.addLogText( 'Min. State Length = {0} samples'.format(self.MinStateLength) )
		logObj.addLogText( 'Max. Event Length = {0} samples'.format(self.MaxEventLength))

		return str(logObj)

	###########################################################################
	# Local functions
	###########################################################################
        def winfitevent(self, edat, initguess):
                try:
                        dt = 1000./self.Fs 	# time-step in ms.


                        # control numpy error reporting
                        np.seterr(invalid='ignore', over='ignore', under='ignore')

                        ts = np.array([ t*dt for t in range(0,len(edat)) ], dtype='float64')

                        self.nStates=len(initguess)-1

                        # setup fit params
                        #clumsy way to build a list but the usual list concatenation using list1+list2 was for some reason adding the lists elementwise...
                        params_0 = [5*dt for i in range(1,len(initguess))]
                        for i in range(1,len(initguess)):
                                params_0.append(initguess[i][1]*dt)
                        for i in range(1,len(initguess)):
                                params_0.append(initguess[i][0]-initguess[i-1][0])
                        params_0.append(initguess[0][0])
                        

                        #lambda function here is necessary in order to fix the value of N, otherwise curve_fit treats that as an optimization parameter
                        popt, pcov = curve_fit(lambda ts, *params_0: fit_funcs.curve_fit_wrapper(ts, self.nStates, params_0), ts, edat, p0=params_0)
                        
                        tau, mu, a = list(popt[:self.nStates]), list(popt[self.nStates:2*self.nStates]), list(popt[2*self.nStates:3*self.nStates])
                        b = popt[-1]

                        self.__winrecordevent(tau, mu, a, b)
                except KeyboardInterrupt:
			self.rejectEvent('eFitUserStop')
			raise
		except InvalidEvent:
			self.rejectEvent('eInvalidEvent')
		except:
	 		self.rejectEvent('eFitFailure')
                        
	
	def fitevent(self, edat, initguess):
		try:
			dt = 1000./self.Fs 	# time-step in ms.

			# control numpy error reporting
			np.seterr(invalid='ignore', over='ignore', under='ignore')

			ts = np.array([ t*dt for t in range(0,len(edat)) ], dtype='float64')

			self.nStates=len(initguess)-1

			# setup fit params
			params=Parameters()

			for i in range(1, len(initguess)):
				params.add('a'+str(i-1), value=initguess[i][0]-initguess[i-1][0]) 
				params.add('mu'+str(i-1), value=initguess[i][1]*dt) 
				if self.UnlinkRCConst:
					params.add('tau'+str(i-1), value=dt*5.)
				else:
					if i-1==0:
						params.add('tau'+str(i-1), value=dt*5.)
					else:
						params.add('tau'+str(i-1), value=dt*5., expr='tau0')

			params.add('b', value=initguess[0][0])
			

			optfit=Minimizer(self.__objfunc, params, fcn_args=(ts,edat,))
			optfit.prepare_fit()

	
			optfit.leastsq(xtol=self.FitTol,ftol=self.FitTol,maxfev=self.FitIters)

			if optfit.success:
				self.__recordevent(optfit)
			else:
				#print optfit.message, optfit.lmdif_message
				self.rejectEvent('eFitConvergence')
		except KeyboardInterrupt:
			self.rejectEvent('eFitUserStop')
			raise
		except InvalidEvent:
			self.rejectEvent('eInvalidEvent')
		except:
	 		self.rejectEvent('eFitFailure')

	def __threadList(self, l1, l2):
		"""thread two lists	"""
		try:
			return map( lambda x,y : (x,y), l1, l2 )
		except KeyboardInterrupt:
			raise

	def __eventEndIndex(self, dat, mu, sigma):
		try:
			return ([ d for d in dat if d[0] < (mu-2*sigma) ][-1][1]+1)
		except IndexError:
			return -1

	def __eventStartIndex(self, dat, mu, sigma):
		try:
			return ([ d for d in dat if d[0] < (mu-2.75*sigma) ][0][1]+1)
		except IndexError:
			return -1

	def __objfunc(self, params, t, data):
		""" model parameters for multistate blockade """
		try:
			b = params['b'].value
			tau = [params['tau'+str(i)].value for i in range(self.nStates)]
			a=[params['a'+str(i)].value for i in range(self.nStates)]
			mu=[params['mu'+str(i)].value for i in range(self.nStates)]

			model = fit_funcs.multiStateFunc(t, tau, mu, a, b, self.nStates)
			return model - data
		except KeyboardInterrupt:
			raise

        def __winrecordevent(self, tau, mu, a, b):
                dt = 1000./self.Fs 	# time-step in ms.
                try:
			if self.nStates<2:
				self.rejectEvent('eInvalidStates')
			elif mu[0] < 0.0 or mu[self.nStates-1] < 0.0:
				self.rejectEvent('eInvalidResTime')
			# The start of the event is set past the length of the data
			elif mu[self.nStates-1] > (1000./self.Fs)*(len(self.eventData)-1):
				self.rejectEvent('eInvalidStartTime')
			else:
				self.mdOpenChCurrent 	= b 
				self.mdCurrentStep		= a
				
				self.mdNStates			= self.nStates

				self.mdBlockDepth 		= np.cumsum( self.mdCurrentStep[:-1] )/self.mdOpenChCurrent + 1

				self.mdEventDelay		= mu

				self.mdStateResTime 	= np.diff(self.mdEventDelay)

				self.mdEventStart		= mu[0]
				self.mdEventEnd			= mu[self.nStates-1]
				self.mdRCConst			= tau

				self.mdResTime			= self.mdEventEnd - self.mdEventStart

				self.mdAbsEventStart	= self.mdEventStart + self.absDataStartIndex * dt
				
				self.mdRedChiSq			= 0 #not returned by curve_fit afaik
					
				if math.isnan(self.mdRedChiSq):
					self.rejectEvent('eInvalidRedChiSq')	
				if not (np.array(self.mdStateResTime)>0).all():
					self.rejectEvent('eNegativeEventDelay')
				if not (np.array(self.mdRCConst)>0).all():
					self.rejectEvent('eInvalidRCConst')
		except:
			self.rejectEvent('eInvalidEvent')

			
	def __recordevent(self, optfit):
		dt = 1000./self.Fs 	# time-step in ms.

		try:
			if self.nStates<2:
				self.rejectEvent('eInvalidStates')
			elif optfit.params['mu0'].value < 0.0 or optfit.params['mu'+str(self.nStates-1)].value < 0.0:
				self.rejectEvent('eInvalidResTime')
			# The start of the event is set past the length of the data
			elif optfit.params['mu'+str(self.nStates-1)].value > (1000./self.Fs)*(len(self.eventData)-1):
				self.rejectEvent('eInvalidStartTime')
			else:
				self.mdOpenChCurrent 	= optfit.params['b'].value 
				self.mdCurrentStep		= [ optfit.params['a'+str(i)].value for i in range(self.nStates) ]
				
				self.mdNStates			= self.nStates

				self.mdBlockDepth 		= np.cumsum( self.mdCurrentStep[:-1] )/self.mdOpenChCurrent + 1

				self.mdEventDelay		= [ optfit.params['mu'+str(i)].value for i in range(self.nStates) ]

				self.mdStateResTime 	= np.diff(self.mdEventDelay)

				self.mdEventStart		= optfit.params['mu0'].value
				self.mdEventEnd			= optfit.params['mu'+str(self.nStates-1)].value
				self.mdRCConst			= [ optfit.params['tau'+str(i)].value for i in range(self.nStates) ]

				self.mdResTime			= self.mdEventEnd - self.mdEventStart

				self.mdAbsEventStart	= self.mdEventStart + self.absDataStartIndex * dt
				
				self.mdRedChiSq			= sum(np.array(optfit.residual)**2/self.baseSD**2)/optfit.nfree
					
				if math.isnan(self.mdRedChiSq):
					self.rejectEvent('eInvalidRedChiSq')	
				if not (np.array(self.mdStateResTime)>0).all():
					self.rejectEvent('eNegativeEventDelay')
				if not (np.array(self.mdRCConst)>0).all():
					self.rejectEvent('eInvalidRCConst')
		except:
			self.rejectEvent('eInvalidEvent')

	def _levelchange(self, dat, sMean, sSD, nSD, blksz):
		start_i=None
		start_slope=None
		for i in range(int(blksz/2.0), len(dat)-int(blksz/2.0)):
			p1, p2= i-int(blksz/2.0), i+int(blksz/2.0)
			if abs(util.avg(dat[p1:p2])-sMean) > nSD * sSD:
				if not start_i:	
					start_i=i
					start_slope=dat[p2]-dat[p1]
				elif np.sign(start_slope) != np.sign(dat[p2]-dat[p1]):
					if start_slope < 0:
						avgCurr=np.min(dat[start_i:p2])
					else:
						avgCurr=np.max(dat[start_i:p2])
					return [start_i, avgCurr]

		raise InvalidEvent()

	def _characterizeevent(self, dat, mean, sd, nSD, blksz):
		tdat=dat
		tt=[0, mean]
		mu=[0]
		a=[mean]
		t1=0
		while (1):
			tt=self._levelchange( tdat[t1:], tt[1], sd, nSD, blksz )
			t1+=tt[0]
			mu.append(t1)
			a.append(tt[1])
			if abs(tt[1]) > (mean-nSD*sd):
				break

		delIdx=[]
		for i in range(2, len(mu)-1):
			if mu[i]-mu[i-1] < self.MinStateLength:
				delIdx.extend([i])

		for idx in sorted(delIdx, reverse=True):
			del a[idx]
			del mu[idx]

		return zip(a,mu)

	def _cusumInitGuess(self, edat):
		settingsDict=mosaic.settings.settings("/", defaultwarn=False )

		cusumSettings=settingsDict.getSettings("cusumPlus")
		cusumSettings["MinThreshold"]=0.1
		cusumSettings["MaxThreshold"]=0.1
		cusumSettings["StepSize"]=18.0 #self.InitThreshold

		print cusumSettings
		cusumObj=cusum.cusumPlus(
				edat, 
				self.Fs,
				eventstart=self.eStartEstimate,						# event start point
				eventend=self.eEndEstimate,							# event end point
				baselinestats=[ self.baseMean, self.baseSD, self.baseSlope ],
				algosettingsdict=cusumSettings.copy(),
				savets=False,
				absdatidx=self.absDataStartIndex,
				datafilehnd=None
			)
		cusumObj.processEvent()

		if cusumObj.mdProcessingStatus != "normal":
			raise InvalidEvent
		else:
			return zip(cusumObj.CurrentLevels, cusumObj.mdEventDelay)


