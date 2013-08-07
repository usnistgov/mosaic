"""
	Author: 	Arvind Balijepalli
	Created:	4/18/2013

	ChangeLog:
		4/18/13		AB	Initial version
		6/20/13		AB 	Added an additional check to reject events 
						with blockade depths > BlockRejectRatio (default: 0.8)
"""
import commonExceptions
import metaEventProcessor
import util
import sys
import math

import numpy as np
import scipy.optimize

from lmfit import minimize, Parameters, Parameter, report_errors, Minimizer

class datblock:
	"""
		Smart data block that holds a time-series of data and keeps track
		of its mean and SD.
	"""
	def __init__(self, dat):
		self.data=dat
		self.mean=util.avg(dat)
		self.sd=util.sd(dat)


class stepResponseAnalysis(metaEventProcessor.metaEventProcessor):
	"""
		Analyze an event that is characteristic of PEG blockades. This method includes system 
		information in the analysis, specifically the filtering effects (throught the RC constant)
		of either amplifiers or the membrane/nanopore complex. The analysis generates several 
		parameters that are stored as metadata including:
			1. Blockade depth: the ratio of the open channel current to the blocked current
			2. Residence time: the time the molecule spends inside the pore
			3. Rise time: the 1/RC of the response to a step input (e.g. the entry or exit of the
				molecule into or out of the nanopore).

		When an event cannot be analyzed, the blockade depth, residence time and rise time are set to -1.
	"""
	def __init__(self, icurr, Fs, **kwargs):
		"""
			Initialize the single step analysis class.
		"""
		# call the base class initializer. This sets self.eventData and self.Fs
		super(stepResponseAnalysis, self).__init__(icurr,Fs, **kwargs)

		# initialize the object's metadata (to -1) as class attributes
		self.mdOpenChCurrent=-1
		self.mdBlockedCurrent=-1

		self.mdEventStart=-1
		self.mdEventEnd=-1
		
		self.mdBlockDepth = -1
		self.mdResTime = -1

		self.mdRiseTime=-1

		self.mdRedChiSq=-1

		# Settings for single step event processing
		# settings for gaussian fits
		try:
			self.FitTol=float(self.settingsDict.pop("FitTol", 1.e-7))
			self.FitIters=int(self.settingsDict.pop("FitIters", 5000))

			self.BlockRejectRatio=float(self.settingsDict.pop("BlockRejectRatio", 0.8))
		
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
			# Fit the system transfer function to the event data
			self.__FitEvent()

			# Call the base class function for any additional processing
			super(stepResponseAnalysis, self).processEvent()
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
					self.mdRiseTime,
					self.mdRedChiSq
				]
		

	def mdHeadings(self):
		"""
			Explicity set the metadata to print out.
		"""
		return ['ProcessingStatus', 'OpenChCurrent (pA)', 'BlockedCurrent (pA)','EventStart', 'EventEnd', 'BlockDepth', 'ResTime (ms)', 'RiseTime (ms)', 'ReducedChiSquared' ]

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
		
		fmtstr+='\t\tMax. iterations  = {0}\n'.format(self.FitIters)
		fmtstr+='\t\tFit tolerance (rel. err in leastsq)  = {0}\n'.format(self.FitTol)
		fmtstr+='\t\tBlockade Depth Rejection = {0}\n\n'.format(self.BlockRejectRatio)


		return fmtstr

	###########################################################################
	# Local functions
	###########################################################################
	def __FitEvent(self):
		try:
			i0=np.abs(self.baseMean)
			i0sig=self.baseSD
			dt = 1000./self.Fs 	# time-step in ms.
			edat=np.asarray( np.abs(self.eventData),  dtype='float64' )

			estart 	= self.__eventStartIndex( self.__threadList( edat, range(0,len(edat)) ), i0, i0sig ) - 1
			eend 	= self.__eventEndIndex( self.__threadList( edat, range(0,len(edat)) ), i0, i0sig ) - 2

			# control numpy error reporting
			np.seterr(invalid='ignore', over='ignore', under='ignore')

			ts = np.array([ t*dt for t in range(0,len(edat)) ], dtype='float64')

			params=Parameters()

			params.add('mu1', value=estart * dt)
			params.add('mu2', value=eend * dt)
			params.add('a', value=(i0-min(edat)))
			params.add('b', value = i0)
			params.add('tau', value = dt)

			optfit=Minimizer(self.__objfunc, params, fcn_args=(ts,edat,))
			optfit.prepare_fit()

			optfit.leastsq(xtol=self.FitTol,ftol=self.FitTol,maxfev=self.FitIters)

			if optfit.success:
				if optfit.params['mu1'].value < 0.0 or optfit.params['mu2'].value < 0.0:
					# print 'eInvalidFitParams', optfit.params['b'].value, optfit.params['b'].value - optfit.params['a'].value, optfit.params['mu1'].value, optfit.params['mu2'].value
					self.rejectEvent('eInvalidFitParams')
				# The start of the event is set past the length of the data
				elif optfit.params['mu1'].value > ts[-1]:
					self.rejectEvent('eInvalidFitParams')
				else:
					self.mdOpenChCurrent 	= optfit.params['b'].value 
					self.mdBlockedCurrent	= optfit.params['b'].value - optfit.params['a'].value
					self.mdEventStart		= optfit.params['mu1'].value
					self.mdEventEnd			= optfit.params['mu2'].value
					self.mdRiseTime			= optfit.params['tau'].value

					self.mdBlockDepth		= self.mdBlockedCurrent/self.mdOpenChCurrent
					self.mdResTime			= self.mdEventEnd - self.mdEventStart
					
					self.mdRedChiSq			= optfit.chisqr/( np.var(optfit.residual) * (len(self.eventData) - optfit.nvarys -1) )

					# if self.mdBlockDepth > self.BlockRejectRatio:
					# 	# print 'eBlockDepthHigh', optfit.params['b'].value, optfit.params['b'].value - optfit.params['a'].value, optfit.params['mu1'].value, optfit.params['mu2'].value
					# 	self.rejectEvent('eBlockDepthHigh')
						
					if math.isnan(self.mdRedChiSq):
						self.rejectEvent('eInvalidFitParams')

					#print i0, i0sig, [optfit.params['a'].value, optfit.params['b'].value, optfit.params['mu1'].value, optfit.params['mu2'].value, optfit.params['tau'].value]
			else:
				#print optfit.message, optfit.lmdif_message
				self.rejectEvent('eFitConvergence')
		except KeyboardInterrupt:
			self.rejectEvent('eFitUserStop')
			raise
		except:
			#print optfit.message, optfit.lmdif_message
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

	def __heaviside(self, x):
		out=np.array(x)

		out[out==0]=0.5
		out[out<0]=0
		out[out>0]=1

		return out
		
	def __eventFunc(self, t, tau, mu1, mu2, a, b):
		try:
			return a*( (np.exp((mu1-t)/tau)-1)*self.__heaviside(t-mu1)+(1-np.exp((mu2-t)/tau))*self.__heaviside(t-mu2) ) + b
		except:
			raise

	def __objfunc(self, params, t, data):
		""" model decaying sine wave, subtract data"""
		try:
			tau = params['tau'].value
			mu1 = params['mu1'].value
			mu2 = params['mu2'].value
			a = params['a'].value
			b = params['b'].value
		    
			model = self.__eventFunc(t, tau, mu1, mu2, a, b)
			return model - data
		except KeyboardInterrupt:
			raise
