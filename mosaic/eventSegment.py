"""
	Partition a trajectory into individual events and pass each event 
	to an implementation of eventProcessor

	:Created:	7/17/2012
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		5/17/14		AB  Delete plotting support
		5/17/14		AB  Add metaMDIO support for meta-data and time-series storage
		2/14/14		AB 	Pass absdatidx argument to event processing to track absolute time of 
						event start for capture rate estimation.
		6/22/13		AB 	Use plotting hooks in metaEventPartition to plot blockade depth histogram in 
						real-time using matplotlib.
		4/22/13		AB 	Rewrote this class as an implementation of the base class metaEventPartition.
						Included event processing parallelization using ZMQ.
		9/26/12		AB  Allowed automatic open channel state calculation to be overridden.
						To do this the settings "meanOpenCurr","sdOpenCurr" and "slopeOpenCurr"
						must be set manually. If all three settings are absent or 
						set to 01, they are autuomatically estimated.
						Added "writeEventTS" boolean setting to control whether raw
						events are written to file. Default is ON (1)
		8/24/12		AB 	Settings are now read from a settings file that
						is located either with the data or in the working directory 
						that the program is run from. Each class that relies on the 
						settings file will fallback to default values if the file
						is not found.
		7/17/12		AB	Initial version
"""
import mosaic.utilities.util as util
from  collections import deque

import metaEventPartition

class eventSegment(metaEventPartition.metaEventPartition):
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
		fmtstr=""

		fmtstr+='\tEvent segment settings:\n\t\t'
		fmtstr+='Window size for block operations = {0} s\n'.format(self.blockSizeSec)
		fmtstr+='\t\tEvent padding = {0} points\n'.format(self.eventPad)
		fmtstr+='\t\tMin. event rejection length = {0} points\n'.format(self.minEventLength)
		fmtstr+='\t\tEvent trigger threshold = {0} * SD\n\n'.format(self.eventThreshold)
		fmtstr+='\t\tDrift error threshold = {0} * SD\n'.format(self.driftThreshold)
		fmtstr+='\t\tDrift rate error threshold = {0} pA/s\n'.format(self.maxDriftRate)

		return fmtstr	

	def formatstats(self):
		"""
			Return a formatted string of statistics for display in the output log.
		"""
		fmtstr=""

		fmtstr+='\tBaseline open channel conductance:\n'
		fmtstr+='\t\tMean	= {0} pA\n'.format( round(self.meanOpenCurr,2) ) 
		fmtstr+='\t\tSD	= {0} pA\n'.format( round(self.sdOpenCurr,2) ) 
		fmtstr+='\t\tSlope 	= {0} pA/s\n'.format( round(self.slopeOpenCurr,2) ) 
		

		fmtstr+='\n\tEvent segment stats:\n'
		fmtstr+='\t\tEvents detected = {0}\n'.format(self.eventcount)

		fmtstr+='\n\t\tOpen channel drift (max) = {0} * SD\n'.format(abs(round((abs(self.meanOpenCurr)-abs(self.maxDrift))/self.sdOpenCurr,2)))
		fmtstr+='\t\tOpen channel drift rate (min/max) = ({0}/{1}) pA/s\n\n'.format(round(self.minDriftR,2), round(self.maxDriftR))

		return fmtstr

	def formatoutputfiles(self):
		fmtstr=""

		fmtstr+='[Output]\n'
		fmtstr+='\tOutput path = {0}\n'.format(self.trajDataObj.datPath)
		fmtstr+='\tEvent characterization data = '+ self.mdioDBHnd.dbFilename +'\n'
		if self.writeEventTS:
			fmtstr+='\tEvent time-series = ***enabled***\n'
		else:
			fmtstr+='\tEvent time-series = ***disabled***\n'

		return fmtstr

	#################################################################
	# Interface functions
	#################################################################
	"""#@profile"""
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
			while(1):
				t=self.currData.popleft()
				self.globalDataIndex+=1

				# store the latest point in a fixed buffer
				if not self.eventstart:
					self.preeventdat.append(t)
				
				# Mark the start of the event
				if abs(t) < self.thrCurr: 
					#print "event",
					self.eventstart=True
					self.eventdat=[]
					self.eventdat.append(t)
					self.dataStart=self.globalDataIndex-len(self.preeventdat)-1

				if self.eventstart:
					mean=abs(util.avg(self.preeventdat))
					while(abs(t)<mean):
						t=self.currData.popleft()
						self.eventdat.append(t)
						self.globalDataIndex+=1

					# end of event. Reset the flag
					self.eventstart=False
					
					# Check if there are enough data points to pad the event. If not pop more.
					if len(self.currData) < self.eventPad:
						self.currData.extend(list(self.trajDataObj.popdata(self.nPoints)))

					# Cleanup event pad data before adding it to the event. We look for:
					# 	1. the start of a second event
					#	2. Outliers
					# The threshold for accepting a point is eventThreshold/2.0
					eventpaddat = util.selectS( 
							[ self.currData[i] for i in range(self.eventPad) ],
							self.eventThreshold/2.0,
							self.meanOpenCurr, 
							self.sdOpenCurr
						)
					 
					#print self.trajDataObj.FsHz, self.windowOpenCurrentMean, self.sdOpenCurr, self.slopeOpenCurr
					if len(self.eventdat)>=self.minEventLength:
						self.eventcount+=1
						# print "i=", self.eventcount
						#sys.stderr.write('event mean curr={0:0.2f}, len(preeventdat)={1}\n'.format(sum(self.eventdat)/len(self.eventdat),len(self.preeventdat)))
						#print list(self.preeventdat) + self.eventdat + [ self.currData[i] for i in range(self.eventPad) ]
						#print "ecount=", self.eventcount, self.eventProcHnd
						# print "eventProcSettings", self.eventProcSettingsDict
						self._processEvent(
							 self.eventProcHnd(
								list(self.preeventdat) + self.eventdat + eventpaddat, 
								self.trajDataObj.FsHz,
								eventstart=len(self.preeventdat)+1,						# event start point
								eventend=len(self.preeventdat)+len(self.eventdat)+1,	# event end point
								baselinestats=[ self.meanOpenCurr, self.sdOpenCurr, self.slopeOpenCurr ],
								algosettingsdict=self.eventProcSettingsDict.copy(),
								savets=self.writeEventTS,
								absdatidx=self.dataStart
							)
						)
	
					self.preeventdat.clear()
		except IndexError:
			return



	# def __roundufloat(self, uf):
	# 	u=uncertainties
	# 	return u.ufloat(( round( u.nominal_value(uf), 4), round( u.std_dev(uf), 4) ))
