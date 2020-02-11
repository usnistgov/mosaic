# -*- coding: utf-8 -*-
""" 
	A class that extends metaEventProcessing to implement the step response algorithm from :cite:`Balijepalli:2014`

	:Created:	4/18/2013
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		06/28/16 	AB 	Upgrade lmfit to > 0.9 (https://lmfit.github.io/lmfit-py/whatsnew.html#whatsnew-090-label)
		03/30/16 	AB 	Change UnlinkRCConst to LinkRCConst to avoid double negatives.
		12/09/15 	KB 	Added Windows specific optimizations
		8/24/15 	AB 	Rename algorithm to ADEPT 2 State.
		7/23/15		JF  Added a new test to reject RC Constants <=0
		6/24/15 	AB 	Added an option to unlink the RC constants in stepResponseAnalysis.
		11/7/14		AB 	Error codes describing event rejection are now more specific.
		11/5/14		AB 	Fixed a bug in the event fitting logic that prevented 
						long events from being correctly analyzed.
		5/17/14		AB  Modified md interface functions for metaMDIO support
		2/16/14		AB 	Added new metadata field, 'AbsEventStart' to track 
						global time of event start to allow capture rate estimation.
		6/20/13		AB 	Added an additional check to reject events 
						with blockade depths > BlockRejectRatio (default: 0.8)
		4/18/13		AB	Initial version
"""
import mosaic.commonExceptions
from . import metaEventProcessor
import mosaic.utilities.util as util
import mosaic.utilities.mosaicLogging as mlog
import mosaic.utilities.fit_funcs as fit_funcs
import sys
import math

import numpy as np
#import pylab as pl
import scipy.optimize
from scipy.optimize import curve_fit

from lmfit import minimize, Parameters, Parameter, report_errors, Minimizer

__all__ = ["adept2State"]

class datblock:
	""" 
		Smart data block that holds time-series data and keeps track
		of its mean and SD.
	"""
	def __init__(self, dat):
		self.data=dat
		self.mean=util.avg(dat)
		self.sd=util.sd(dat)


class adept2State(metaEventProcessor.metaEventProcessor):
	""" 
		Analyze an event that is characteristic of PEG blockades. This method includes system 
		information in the analysis, specifically the filtering effects (throught the RC constant)
		of either amplifiers or the membrane/nanopore complex. The analysis generates several 
		parameters that are stored as metadata including:
			1. Blockade depth: the ratio of the open channel current to the blocked current
			2. Residence time: the time the molecule spends inside the pore
			3. Tau: the RC constant of the response to a step input (e.g. the entry or exit of the molecule into or out of the nanopore).

		:Keyword Args:
			In addition to :class:`~mosaic.metaEventProcessor.metaEventProcessor` args,
				- `FitTol` :		Tolerance value for the least squares algorithm that controls the convergence of the fit (Default: `1e-7`).
				- `FitIters` : 		Maximum number of iterations before terminating the fit (Default: `50000`).
				- `LinkRCConst` :	When True, the RC constants associated with each state in the fit function are varied together. (Default: `True`)

		:Errors:
			
			When an event cannot be analyzed, the blockade depth, residence time and rise time are set to -1.

	"""

	def _init(self, **kwargs):
		""" 
			Initialize the single step analysis class.
		"""
		# initialize the object's metadata (to -1) as class attributes
		self.mdOpenChCurrent=-1
		self.mdBlockedCurrent=-1

		self.mdEventStart=-1
		self.mdEventEnd=-1
		
		self.mdBlockDepth = -1
		self.mdResTime = -1

		self.mdRCConst1 = -1
		self.mdRCConst2 = -1

		self.mdRedChiSq = -1

		self.mdAbsEventStart = -1

		self.a2sLogger=mlog.mosaicLogging().getLogger(__name__)

		# Settings for single step event processing
		# settings for gaussian fits
		try:
			self.FitTol=float(self.settingsDict.pop("FitTol", 1.e-7))
			self.FitIters=int(self.settingsDict.pop("FitIters", 5000))

			self.BlockRejectRatio=float(self.settingsDict.pop("BlockRejectRatio", 0.8))

			self.LinkRCConst=int(self.settingsDict.pop("LinkRCConst", 1))
		except ValueError as err:
			raise mosaic.commonExceptions.SettingsTypeError( err )


	###########################################################################
	# Interface functions implemented starting here
	###########################################################################
	def _processEvent(self):
		""" 
			This function implements the core logic to analyze one single step-event.
		"""
		try:
			# Fit the system transfer function to the event data
			# if sys.platform.startswith('win'):
            # 	self.__WinFitEvent()
			# else:
			self.__FitEvent()
		except:
			raise

	def _mdList(self):
		""" 
			Return a list of meta-data from the analysis of single step events. We explicitly
			control the order of the data to keep formatting consistent. 				
		"""
		return [
					self.mdProcessingStatus, 
					self.mdOpenChCurrent, 
					self.mdBlockedCurrent,
					self.mdEventStart,
					self.mdEventEnd,
					self.mdBlockDepth,
					self.mdResTime,
					self.mdRCConst1,
					self.mdRCConst2,
					self.mdAbsEventStart,
					self.mdRedChiSq
				]

	def _mdHeadingDataType(self):
		""" 
			Return a list of meta-data tags data types.
		"""
		return [
					'TEXT', 
					'REAL', 
					'REAL',
					'REAL',
					'REAL',
					'REAL',
					'REAL',
					'REAL',
					'REAL',
					'REAL',
					'REAL'
				]

	def _mdHeadings(self):
		""" 
			Explicity set the metadata to print out.
		"""
		return [
					'ProcessingStatus', 
					'OpenChCurrent', 
					'BlockedCurrent',
					'EventStart', 
					'EventEnd', 
					'BlockDepth', 
					'ResTime', 
					'RCConstant1',
					'RCConstant2', 
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
		self.a2sLogger.info( '\tEvent processing settings:' )
		self.a2sLogger.info( '\t\tAlgorithm = ADEPT 2-State' )
		
		self.a2sLogger.info( '\t\tMax. iterations  = {0}'.format(self.FitIters) )
		self.a2sLogger.info( '\t\tFit tolerance (rel. err in leastsq)  = {0}'.format(self.FitTol) )
		self.a2sLogger.info( '\t\tLink RC constants = {0}'.format(bool(self.LinkRCConst)) )


	###########################################################################
	# Local functions
	###########################################################################
	def __FitEvent(self):
		try:
			varyBlockedCurrent=True

			i0=np.abs(self.baseMean)
			i0sig=self.baseSD
			dt = 1000./self.Fs 	# time-step in ms.
			# edat=np.asarray( np.abs(self.eventData),  dtype='float64' )
			edat=self.dataPolarity*np.asarray( self.eventData,  dtype='float64' )

			blockedCurrent=min(edat)
			tauVal=dt

			estart 	= self.__eventStartIndex( self.__threadList( edat, list(range(0,len(edat))) ), i0, i0sig ) - 1
			eend 	= self.__eventEndIndex( self.__threadList( edat, list(range(0,len(edat))) ), i0, i0sig ) - 2

			# For long events, fix the blocked current to speed up the fit
			#if (eend-estart) > 1000:
			#	blockedCurrent=np.mean(edat[estart+50:eend-50])

			# control numpy error reporting
			np.seterr(invalid='ignore', over='ignore', under='ignore')

			ts = np.array([ t*dt for t in range(0,len(edat)) ], dtype='float64')

			#pl.plot(ts,edat)
			#pl.show()

			params=Parameters()

			# print self.absDataStartIndex

			params.add('mu1', value=estart * dt)
			params.add('mu2', value=eend * dt)
			params.add('a', value=(i0-blockedCurrent), vary=varyBlockedCurrent)
			params.add('b', value = i0)
			params.add('tau1', value = tauVal)

			if self.LinkRCConst:
				params.add('tau2', value = tauVal, expr='tau1')
			else:
				params.add('tau2', value = tauVal)


			optfit=Minimizer(self.__objfunc, params, fcn_args=(ts,edat,))
			optfit.prepare_fit()

			result=optfit.leastsq(xtol=self.FitTol,ftol=self.FitTol,maxfev=self.FitIters)

			# print optfit.params['b'].value, optfit.params['b'].value - optfit.params['a'].value, optfit.params['mu1'].value, optfit.params['mu2'].value
			if result.success:
				if result.params['mu1'].value < 0.0 or result.params['mu2'].value < 0.0:
					# print 'eInvalidFitParams1', optfit.params['b'].value, optfit.params['b'].value - optfit.params['a'].value, optfit.params['mu1'].value, optfit.params['mu2'].value
					self.rejectEvent('eInvalidResTime')
				# The start of the event is set past the length of the data
				elif result.params['mu1'].value > ts[-1]:
					# print 'eInvalidFitParams2', optfit.params['b'].value, optfit.params['b'].value - optfit.params['a'].value, optfit.params['mu1'].value, optfit.params['mu2'].value
					self.rejectEvent('eInvalidEventStart')
				else:
					self.mdOpenChCurrent 	= result.params['b'].value 
					self.mdBlockedCurrent	= result.params['b'].value - result.params['a'].value
					self.mdEventStart		= result.params['mu1'].value 
					self.mdEventEnd			= result.params['mu2'].value
					self.mdRCConst1			= result.params['tau1'].value
					self.mdRCConst2			= result.params['tau2'].value
					self.mdAbsEventStart	= self.mdEventStart + self.absDataStartIndex * dt

					self.mdBlockDepth		= self.mdBlockedCurrent/self.mdOpenChCurrent
					self.mdResTime			= self.mdEventEnd - self.mdEventStart
					
					self.mdRedChiSq			= result.chisqr/( np.var(result.residual) * (len(self.eventData) - result.nvarys -1) )

					# if (eend-estart) > 1000:
					# 	print blockedCurrent, self.mdBlockedCurrent, self.mdOpenChCurrent, self.mdResTime, self.mdRiseTime, self.mdRedChiSq, optfit.chisqr
					# if self.mdBlockDepth > self.BlockRejectRatio:
					# 	# print 'eBlockDepthHigh', optfit.params['b'].value, optfit.params['b'].value - optfit.params['a'].value, optfit.params['mu1'].value, optfit.params['mu2'].value
					# 	self.rejectEvent('eBlockDepthHigh')
						
					if math.isnan(self.mdRedChiSq):
						self.rejectEvent('eInvalidChiSq')
					if self.mdBlockDepth < 0 or self.mdBlockDepth > 1:
						self.rejectEvent('eInvalidBlockDepth')
					if self.mdRCConst1 <= 0 or self.mdRCConst2 <= 0:
						self.rejectEvent('eInvalidRCConstant')

					#print i0, i0sig, [optfit.params['a'].value, optfit.params['b'].value, optfit.params['mu1'].value, optfit.params['mu2'].value, optfit.params['tau'].value]
			else:
				# print optfit.message, optfit.lmdif_message
				self.rejectEvent('eFitConvergence')

		except KeyboardInterrupt:
			self.rejectEvent('eFitUserStop')
			raise
		except:
			# print optfit.message, optfit.lmdif_message
	 		self.rejectEvent('eFitFailure')

	def __threadList(self, l1, l2):
		""" thread two lists	"""
		try:
			return list(map( lambda x,y : (x,y), l1, l2 ))
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
		""" single step response model parameters """
		try:
			tau1 = params['tau1'].value
			tau2 = params['tau2'].value
			mu1 = params['mu1'].value
			mu2 = params['mu2'].value
			a = params['a'].value
			b = params['b'].value

			model = fit_funcs.stepResponseFunc(t, tau1, tau2, mu1, mu2, a, b)

			return model - data
		except KeyboardInterrupt:
			raise
