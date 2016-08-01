# -*- coding: utf-8 -*-
"""
	Partition a trajectory into individual events and pass each event 
	to an implementation of eventProcessor

	:Created:	7/26/2016
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		7/26/16		AB	Initial version
"""
import mosaic.utilities.util as util
import mosaic.utilities.mosaicLogFormat as log
from mosaic.utilities.resource_path import format_path
import mosaic.utilities.mosaicLogging as mlog
from  collections import deque
import metaEventPartition
import numpy as np
from scipy.stats import threshold as threshold
from mosaic.utilities.mosaicLogFormat import _d

__all__ = ["blockTheshold"]

class blockThreshold(metaEventPartition.metaEventPartition):
	"""
		Implement an event partitioning algorithm by sub-classing the metaEventPartition class

		:Settings: In addition to the parameters described in :class:`~mosaic.metaEventPartition`, the following parameters from are read from the settings file (.settings in the data path or current working directory):

			- `blockSizeSec` :	Functions that perform block processing use this value to set the size of 
							their windows in seconds. For example, open channel conductance is processed
							for windows with a size specified by this parameter. (default: 1 second)
			- `eventPad` :		Number of points to include before and after a detected event. (default: 500)
			- `minEventLength` :	Minimum number points in the blocked state to qualify as an event (default: 5)
			- `eventThreshold` :	Threshold, number of SD away from the open channel mean. If the abs(curr) is less
							than 'abs(mean)-(eventThreshold*SD)' a new event is registered (default: 6)
			- `driftThreshold` :	Trigger a drift warning when the mean open channel current deviates by 'driftThreshold'*
							SD from the baseline open channel current (default: 2)
			- `maxDriftRate` :	Trigger a warning when the open channel conductance changes at a rate faster 
							than that specified. (default: 2 pA/s)
			- `meanOpenCurr` :	Explicitly set mean open channel current. (pA) (default: -1, to 
							calculate automatically)
			- `sdOpenCurr` :		Explicitly set open channel current SD. (pA) (default: -1, to 
							calculate automatically)
			- `slopeOpenCurr` :	Explicitly set open channel current slope. (default: -1, to 
							calculate automatically)
	"""
	def _init(self, trajDataObj, eventProcHnd, eventPartitionSettings, eventProcSettings):
		"""
			Segment a trajectory
		"""
		# parse algorithm specific settings from the settings dict
		try:
			self.blockSizeSec=float(self.settingsDict.pop("blockSizeSec", 1.0))
			self.eventPad=int(self.settingsDict.pop("eventPad", 500))
			self.minEventLength=int(self.settingsDict.pop("minEventLength",5))
			self.eventThreshold=float(self.settingsDict.pop("eventThreshold",6.0))
			self.driftThreshold=float(self.settingsDict.pop("driftThreshold",2.0))
			self.maxDriftRate=float(self.settingsDict.pop("maxDriftRate",2.0))
			self.meanOpenCurr=float(self.settingsDict.pop("meanOpenCurr",-1.))
			self.sdOpenCurr=float(self.settingsDict.pop("sdOpenCurr",-1.))
			self.slopeOpenCurr=float(self.settingsDict.pop("slopeOpenCurr",-1.))
		except ValueError as err:
			raise commonExceptions.SettingsTypeError( err )

		#### Vars for event partition ####
		self.logger=mlog.mosaicLogging().getLogger(name=__name__, dbHnd=self.mdioDBHnd)
		self.eventstart=False
		self.eventdat=[]
		self.preeventdat=deque(maxlen=self.eventPad)
		self.eventcount=0
		self.eventprocessedcount=0
	
	def _stop(self):
		pass

	def formatsettings(self):
		"""
			Return a formatted string of settings for display in the output log.
		"""
		self.logger.info( '\tEvent segment settings:' )
		self.logger.info( '\t\tWindow size for block operations = {0} s'.format(self.blockSizeSec) )
		self.logger.info( '\t\tEvent padding = {0} points'.format(self.eventPad) )
		self.logger.info( '\t\tMin. event rejection length = {0} points'.format(self.minEventLength) )
		self.logger.info( '\t\tEvent trigger threshold = {0:5.2f} * SD'.format(self.eventThreshold) )
		self.logger.info( '\t\tDrift error threshold = {0} * SD'.format(self.driftThreshold) )
		self.logger.info( '\t\tDrift rate error threshold = {0} pA/s'.format(self.maxDriftRate) )

	def formatstats(self):
		"""
			Return a formatted string of statistics for display in the output log.
		"""
		self.logger.info('\tBaseline open channel conductance:')
		self.logger.info('\t\tMean	= {0} pA'.format( round(self.meanOpenCurr,2) )) 
		self.logger.info('\t\tSD	= {0} pA'.format( round(self.sdOpenCurr,2) ) )
		self.logger.info('\t\tSlope 	= {0} pA/s'.format( round(self.slopeOpenCurr,2) ) )
		
		self.logger.info('\tEvent segment stats:')

		self.logger.info('\t\tOpen channel drift (max) = {0} * SD'.format(abs(round((abs(self.meanOpenCurr)-abs(self.maxDrift))/self.sdOpenCurr,2))))
		self.logger.info('\t\tOpen channel drift rate (min/max) = ({0}/{1}) pA/s'.format(round(self.minDriftR,2), round(self.maxDriftR)))

	def formatoutputfiles(self):
		self.logger.info('[Output]')
		# self.logger.info('\tOutput path = \'{0}\''.format(self.trajDataObj.datPath))
		self.logger.info('\tEvent database = \'{0}\''.format(self.mdioDBHnd.dbFilename) )
		if self.writeEventTS:
			self.logger.info('\tEvent time-series = ***enabled***')
		else:
			self.logger.info('\tEvent time-series = ***disabled***')

	#################################################################
	# Interface functions
	#################################################################
	"""#@profile"""
	@metaEventPartition.partitionTimer.FunctionTiming
	def _eventsegment(self):
		"""
			Cut up a trajectory into individual events. This algorithm uses
			simple thresholding. By working with absolute values of currents,
			we handle positive and negative potentials without switches. When the
			current drops below 'thrCurr', mark the start of the event. When the current
			returns to the baseline (obtained by averaging the open channel current
			immediately preceeding the start of the event), mark the event end. Pad 
			the event by 'eventPad' points and hand off to the event processing algorithm.
		"""
		try:
			dat=np.array([ self.currData.popleft() for i in range(len(self.currData)) ], dtype=np.float64)
			pad=self.eventPad

			events=self.segmentDataBlock(dat, -200, self.thrCurr, -999)
			
			# self.logger.debug(_d("Global time={0}, events detected={1}", self.globalDataIndex/float(self.FsHz), len(events)))
			for event in events:
				start, end = event[0]-1, event[1]+1
				if (end-start)>=self.minEventLength:
					self.eventcount+=1
					
					edat=util.selectS( 
							dat[start-pad:start],
							self.eventThreshold,
							self.meanOpenCurr, 
							self.sdOpenCurr
						)
					edat=np.append(edat, dat[start:end])
					edat=np.append(
						edat, 
						util.selectS( 
							dat[end+1:end+pad],
							self.eventThreshold,
							self.meanOpenCurr, 
							self.sdOpenCurr
						)
					)

					self._processEvent(
						 self.eventProcHnd(
							edat, 
							self.FsHz,
							eventstart=start,						# event start point
							eventend=end,	# event end point
							baselinestats=[ self.meanOpenCurr, self.sdOpenCurr, self.slopeOpenCurr ],
							algosettingsdict=self.eventProcSettingsDict.copy(),
							savets=self.writeEventTS,
							absdatidx=start-pad+self.globalDataIndex
						)
					)

			self.globalDataIndex+=self.nPoints
		except IndexError:
			return


	def segmentDataBlock(self, dat, thrmin, threshmax, thrnew):
		thr=threshold(dat, threshmin=thrmin, threshmax=threshmax, newval=thrnew)
		diffarr=np.diff(thr)
		filtarr=np.where(diffarr!=0)[0]

		start=np.array([], dtype=np.int64)
		end=np.array([], dtype=np.int64)
		for c in self.consecutive(filtarr, self.minEventLength):
		    start=np.append(start, [c[0]])
		    end=np.append(end, [c[-1]])

		return np.dstack((start, end))[0]

	def consecutive(self, data, stepsize=1):
		return np.split(data, np.where(np.diff(data) > stepsize)[0]+1)
	# def __roundufloat(self, uf):
	# 	u=uncertainties
	# 	return u.ufloat(( round( u.nominal_value(uf), 4), round( u.std_dev(uf), 4) ))
