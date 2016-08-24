# -*- coding: utf-8 -*-
""" 
	A class that extends metaEventProcessing to implement a Gaussian filter transfer function (Colquhoun 1995).

	:Created:	8/23/2016
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		8/23/16		AB	Initial version
"""
import mosaic.commonExceptions
import metaEventProcessor
import mosaic.utilities.util as util
import mosaic.utilities.mosaicLogging as mlog
import mosaic.utilities.fit_funcs as fit_funcs
import sys
import math

import numpy as np
import scipy.optimize
from scipy.optimize import curve_fit

from lmfit import minimize, Parameters, Parameter, report_errors, Minimizer

__all__ = ["gauss"]

class gauss(metaEventProcessor.metaEventProcessor):
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

		self.mdFilterCutoff = -1

		self.mdRedChiSq = -1

		self.mdAbsEventStart = -1

		self.gaussLogger=mlog.mosaicLogging().getLogger(__name__)

		# Settings for single step event processing
		# settings for gaussian fits
		try:
			self.FitTol=float(self.settingsDict.pop("FitTol", 1.e-7))
			self.FitIters=int(self.settingsDict.pop("FitIters", 5000))
			self.FilterCutoffKHZ=int(self.settingsDict.pop("FilterCutoffKHZ", 5.))
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
					self.mdFilterCutoff,
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
					'FilterCutoff',
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
		self.gaussLogger.info( '\tEvent processing settings:' )
		self.gaussLogger.info( '\t\tAlgorithm = GAUSS' )
		
		self.gaussLogger.info( '\t\tMax. iterations  = {0}'.format(self.FitIters) )
		self.gaussLogger.info( '\t\tFit tolerance (rel. err in leastsq)  = {0}'.format(self.FitTol) )


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

			estart 	= self.__eventStartIndex( self.__threadList( edat, range(0,len(edat)) ), i0, i0sig ) - 1
			eend 	= self.__eventEndIndex( self.__threadList( edat, range(0,len(edat)) ), i0, i0sig ) - 2

			# For long events, fix the blocked current to speed up the fit
			if (eend-estart) > 1000:
				blockedCurrent=np.mean(edat[estart+50:eend-50])

			# control numpy error reporting
			np.seterr(invalid='ignore', over='ignore', under='ignore')

			ts = np.array([ t*dt for t in range(0,len(edat)) ], dtype='float64')

			params=Parameters()

			# print self.absDataStartIndex

			params.add('mu1', value=estart * dt)
			params.add('mu2', value=eend * dt)
			params.add('a', value=(i0-blockedCurrent)/2., vary=varyBlockedCurrent)
			params.add('b', value = i0)
			params.add('fc', value = self.FilterCutoffKHZ)

			optfit=Minimizer(self.__objfunc, params, fcn_args=(ts,edat,))
			optfit.prepare_fit()

			result=optfit.leastsq(xtol=self.FitTol,ftol=self.FitTol,maxfev=self.FitIters)

			if result.success:
				if result.params['mu1'].value < 0.0 or result.params['mu2'].value < 0.0:
					self.rejectEvent('eInvalidResTime')
				# The start of the event is set past the length of the data
				elif result.params['mu1'].value > ts[-1]:
					self.rejectEvent('eInvalidEventStart')
				else:
					self.mdOpenChCurrent 	= result.params['b'].value 
					self.mdBlockedCurrent	= result.params['b'].value - 2.*result.params['a'].value
					self.mdEventStart		= result.params['mu1'].value 
					self.mdEventEnd			= result.params['mu2'].value
					self.mdFilterCutoff		= result.params['fc'].value
					self.mdAbsEventStart	= self.mdEventStart + self.absDataStartIndex * dt

					self.mdBlockDepth		= self.mdBlockedCurrent/self.mdOpenChCurrent
					self.mdResTime			= self.mdEventEnd - self.mdEventStart
					
					self.mdRedChiSq			= result.chisqr/( np.var(result.residual) * (len(self.eventData) - result.nvarys -1) )
		
					if math.isnan(self.mdRedChiSq):
						self.rejectEvent('eInvalidChiSq')
					# if self.mdBlockDepth < 0 or self.mdBlockDepth > 1:
					# 	self.rejectEvent('eInvalidBlockDepth')
			else:
				self.rejectEvent('eFitConvergence')

		except KeyboardInterrupt:
			self.rejectEvent('eFitUserStop')
			raise
		except:
	 		self.rejectEvent('eFitFailure')

	def __threadList(self, l1, l2):
		""" thread two lists	"""
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
		""" single step response model parameters """
		try:
			fc = params['fc'].value
			mu1 = params['mu1'].value
			mu2 = params['mu2'].value
			a = params['a'].value
			b = params['b'].value

			model = fit_funcs.gaussResponseFunc(t, fc, mu1, mu2, a, b)

			return model - data
		except KeyboardInterrupt:
			raise
