"""
	Partition a trajectory into individual events and pass each event 
	to an implementation of eventProcessor

	Author: 	Arvind Balijepalli
	Created:	7/17/2012

	ChangeLog:
		6/22/13		AB 	Use plotting hooks in metaEventPartition to plot blockade depth histogram in 
						real-time using matplotlib.
		4/22/13		AB 	Rewrote this class as an implementation of the base class metaEventPartition.
						Included event processing parallelization using ZMQ.
		9/26/12		AB  Allowed automatic open channel state calculation to be overridden.
						To do this the settings "meanOpenCurr","sdOpenCurr" and "slopeOpenCurr"
						must be set. If all three settings are absent, they are 
						atuomatically estimated.
						Added "writeEventTS" boolean setting to control whether raw
						event currents are written to file. Default is ON (1)
		8/24/12		AB 	Settings are now read from a settings file '.settings' that
						is located either with the data or in the working directory 
						that the program is run from. Each class that relies on the 
						settings file will fallback to default values if the file
						is not found.
		7/17/12		AB	Initial version
"""
import sys
import time
import datetime
import csv
import cPickle

import numpy as np 
import uncertainties
from  collections import deque
import matplotlib.pyplot as plt

import metaEventPartition
import commonExceptions
import singleStepEvent as sse 
import stepResponseAnalysis as sra 
import metaTrajIO

import util
import settings

# custom errors
class ExcessiveDriftError(Exception):
	pass

class DriftRateError(Exception):
	pass

class eventSegment(metaEventPartition.metaEventPartition):
	"""
		Segment a trajectory
	"""
	def __init__(self, trajDataObj, eventProcHnd, eventPartitionSettings, eventProcSettings):
		"""
			Implement an event partitioning algorithm by sub-classing teh metaEventPartition class
	
			Parameters from settings file (.settings in the data path or current working directory):
				blockSizeSec:	Functions that perform block processing use this value to set the size of 
								their windows in seconds. For example, open channel conductance is processed
								for windows with a size specified by this parameter. (default: 1 second)
				eventPad		Number of points to include before and after a detected event. (default: 500)
				minEventLength	Minimum number points in the blocked state to qualify as an event (default: 5)
				eventThreshold	Threshold, number of SD away from the open channel mean. If the abs(curr) is less
								than 'abs(mean)-(eventThreshold*SD)' a new event is registered (default: 6)
				driftThreshold	Trigger a drift warning when the mean open channel current deviates by 'driftThreshold'*
								SD from the baseline open channel current (default: 2)
				maxDriftRate	Trigger a warning when the open channel conductance changes at a rate faster 
								than that specified. (default: 2 pA/s)
				meanOpenCurr	Explicitly set mean open channel current. (pA) (default: -1, to 
								calculate automatically)
				sdOpenCurr		Explicitly set open channel current SD. (pA) (default: -1, to 
								calculate automatically)
				slopeOpenCurr	Explicitly set open channel current slope. (default: -1, to 
								calculate automatically)
		"""
		# First call the base class initializer. 
		super(eventSegment, self).__init__(trajDataObj, eventProcHnd, eventPartitionSettings, eventProcSettings)

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
			self.plotResults=int(self.settingsDict.pop("plotResults", 1))
		except ValueError as err:
			raise commonExceptions.SettingsTypeError( err )

		if self.plotResults:
			self.InitPlot()

	def PartitionEvents(self):
		"""			
		"""	
		outputstr="Start time: "+str(datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p'))+"\n\n"
		# write out first stage results
		sys.stdout.write(outputstr)
		outf=open(self.trajDataObj.datPath+'/eventProcessing.log','w')
		outf.write(outputstr)

		startTime=time.time()

		# At the start of a run, store baseline stats for the open channel state
		# Later, we use these values to detect drift
		# First, calculate the number of points to include using the blockSizeSec 
		# class attribute and the sampling frequency specified in trajDataObj
		self.nPoints=int(self.blockSizeSec*self.trajDataObj.FsHz)

		if self.meanOpenCurr == -1. or self.sdOpenCurr == -1. or self.slopeOpenCurr == -1.:
			[ self.meanOpenCurr, self.sdOpenCurr, self.slopeOpenCurr ] = self.__openchanstats(self.trajDataObj.previewdata(self.nPoints))
		else:
			print "Automatic open channel state calculation has been disabled."

		# Initialize a FIFO queue to keep track of open channel conductance
		#self.openchanFIFO=npfifo.npfifo(nPoints)
		
		# setup a local data store that is used by the main event partition loop
		self.currData = deque()

		#### Event Queue ####
		self.eventQueue=[]

		#### Vars for event partition ####
		self.eventstart=False
		self.eventdat=[]
		self.preeventdat=deque(maxlen=self.eventPad)
		self.eventcount=0
		self.eventprocessedcount=0

		self.thrCurr=(abs(self.meanOpenCurr)-self.eventThreshold*abs(self.sdOpenCurr))

		#### Vars for event partition stats ####
		self.minDrift=abs(self.meanOpenCurr)
		self.maxDrift=abs(self.meanOpenCurr)
		self.minDriftR=self.slopeOpenCurr
		self.maxDriftR=self.slopeOpenCurr

		try:
			while(1):	
				# with each pass obtain more data and
				d=self.trajDataObj.popdata(self.nPoints)
				# Check for excessive open channel drift
				self.__checkdrift(d)

				# store the new data into a local store
				self.currData.extend(list(d))

				#print self.meanOpenCurr, self.minDrift, self.maxDrift, self.minDriftR, self.maxDriftR

				# Process the data segment for events
				self.__eventsegment()

		except metaTrajIO.EmptyDataPipeError, err:
			segmentTime=time.time()-startTime
			outputstr='[Status]\n\tSegment trajectory: ***NORMAL***\n'
		except (ExcessiveDriftError, DriftRateError) as err:
			segmentTime=time.time()-startTime
			outputstr='[Status]\n\tSegment trajectory: ***ERROR***\n\t\t{0}\n'.format(str(err))
		except KeyboardInterrupt, err:
			segmentTime=time.time()-startTime
			outputstr='[Status]\n\tSegment trajectory: ***USER STOP***\n'
		except:
			raise


		# write out first stage results
		sys.stdout.write(outputstr)
		outf.write(outputstr)
		
		# Process individual events identified by the segmenting algorithm
		startTime=time.time()
		try:
			if self.parallelProc:
				# gather up any remaining results from the worker processes
				while self.eventprocessedcount < self.eventcount:
					recvdat=self.RecvResultsChan.zmqReceiveData()
					if recvdat != "":
						#store the processed event
						self.eventQueue.append( cPickle.loads(recvdat) )
						self.eventprocessedcount+=1

						if self.eventprocessedcount%100 == 0:
							sys.stdout.write('Finished processing %d of %d events.\r' % (self.eventprocessedcount,self.eventcount) )
	    					sys.stdout.flush()

				sys.stdout.write('                                                                    \r' )
				sys.stdout.flush()

			else:
			####################
			#	[ evnt.processEvent() for evnt in self.eventQueue ]
			####################
				pass

			outputstr='\tProcess events: ***NORMAL***\n\n\n'
			procTime=time.time()-startTime
		except BaseException, err:
			outputstr='\tProcess events: ***ERROR***\n\t\t{0}\n\n\n'.format(str(err))
			procTime=time.time()-startTime
			raise
		except KeyboardInterrupt:
			procTime=time.time()-startTime
			outputstr+='\t\Process events: ***USER STOP***\n\n\n'

		#print "event count = ", self.eventcount
		# write output files
		# 1. Event metadata
		if len(self.eventQueue) > 0:
			w1=csv.writer(open(self.trajDataObj.datPath+'/eventMD.tsv', 'wO'),delimiter='\t')
			w1.writerow(self.eventQueue[0].mdHeadings())
			[ w1.writerow(event.mdList()) for event in self.eventQueue ]
			if self.writeEventTS:
				# 2. Raw event currents as CSV
				w2=csv.writer(open(self.trajDataObj.datPath+'/eventTS.csv', 'wO'),delimiter=',')
				[ w2.writerow(event.eventData) for event in self.eventQueue ]

		outputstr+='[Summary]\n'

		# write out event segment stats
		outputstr+=self.formatstats()

		# print event processing stats. these are limited to how
		# many events were rejected
		#nEventsProc=0
		#for evnt in self.eventQueue:
		#	if evnt.mdProcessingStatus=='normal':
		#		nEventsProc+=1
		#outputstr+='\tEvent processing stats:\n'
		#outputstr+='\t\tAccepted = {0}\n'.format(nEventsProc)
		#outputstr+='\t\tRejected = {0}\n'.format(self.eventcount-nEventsProc)
		#outputstr+='\t\tRejection rate = {0}\n\n'.format(round(1-nEventsProc/float(self.eventcount),2))

		# Display averaged properties
		#for p in self.eventQueue[0].mdAveragePropertiesList():
		#	outputstr+='\t\t{0} = {1}\n'.format(p, self.__roundufloat( np.mean( [ getattr(evnt, p) for evnt in self.eventQueue if getattr(evnt, p) != -1 ] )) )

		#outputstr+="\n\n[Settings]\n\tSettings File = '{0}'\n\n".format(self.settingsDict.settingsFile)
		
		# write out trajectory IO settings
		outputstr+=self.trajDataObj.formatsettings()+'\n'
		
		# write out event segment settings/stats
		outputstr+=self.formatsettings()+'\n\n'

		# event processing settings
		outputstr+=self.eventQueue[0].formatsettings()+'\n\n'

		# Output files
		outputstr+=self.formatoutputfiles()
		outputstr+='\tLog file = eventProcessing.log\n\n'

		# Finally, timing information
		outputstr+='[Timing]\n\tSegment trajectory = {0} s\n'.format(round(segmentTime,2))
		outputstr+='\tProcess events = {0} s\n\n'.format(round(procTime,2))
		outputstr+='\tTotal = {0} s\n'.format(round(segmentTime+procTime,2))
		outputstr+='\tTime per event = {0} ms\n\n\n'.format(round(1000.*(segmentTime+procTime)/float(self.eventcount),2))
		
		# write it all out to stdout and also to a file
		# eventProcessing.log in the data location
		sys.stdout.write(outputstr)
	
		outf.write(outputstr)
		outf.close()

	def InitPlot(self):
		"""
			Initialize a plotting window to display analysis results in real-time.
		"""
		self.bvals=np.arange(0,1,0.0001)
		ehist,bins=np.histogram(
				np.array([-1]), 
				bins=self.bvals
			)

		plt.ion()

		self.fig = plt.figure()
		ax = self.fig.add_subplot(111)
		self.line1, = ax.plot(bins[:-1], ehist, 'r-') # Returns a tuple of line objects, thus the comma
		plt.ylim([0, 1])

	def UpdatePlot(self):
		"""
			Update plot data with new results as the analysis progresses.
		"""
		if len(self.eventQueue)==0:
			return

		bd=np.array([evnt.mdBlockDepth for evnt in self.eventQueue])

		ehist,bins=np.histogram(
				bd, 
				bins=self.bvals
			)

		plt.ylim([0, np.max(bd)+5])

		self.line1.set_ydata(ehist)
		self.fig.canvas.draw()

	def Stop(self):
		# other cleanup before calling the base class cleanup

		super(eventSegment, self).Stop()

	def formatsettings(self):
		"""
			Return a formatted string of settings for display
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
		fmtstr+='\tEvent characterization data = eventMD.tsv\n'
		if self.writeEventTS:
			fmtstr+='\tEvent time-series = eventTS.csv\n'
		else:
			fmtstr+='\tEvent time-series = ***disabled***\n'

		return fmtstr

	#################################################################
	# Private functions
	#################################################################
	def __openchanstats(self, curr):
		"""
			Estimate the mean, standard deviation and slope of 
			the channel's open state current using self.blockSizeSec of data. 			
			Args:
				curr:			numpy array to use for calculating statistics
			Returns:
				meanOpenCurr	mean open channel current
				sdOpenCurr		standard deviation of open channel current
				slopeOpenCurr	slope of the open channel current (measure of drift)
								in pA/s
			Errors:
				None
		"""
		n=len(curr)

		#curr=self.trajDataObj.previewdata(nPoints)
		t=1./self.trajDataObj.FsHz
		tstamp=np.arange(0, n*t, t, dtype=np.float64)[:n]

		#print "nPoints=", n, "len(tstamp)=", len(tstamp), "type(curr)", type(curr)
		

		# Fit the data to a straight line to calculate the slope
		# ft[0]: slope
		# ft[1]: y-intercept (mean current)
		ft = np.polyfit(tstamp, curr, 1)

		# Return stats
		return [ ft[1], np.std(curr), ft[0] ]
	
		
	def __checkdrift(self, curr):
		"""
			Check the open channel current for drift. This function triggers
			an error when the open channel current drifts from the baseline value
			by 'driftThreshold' standard deviations.
			Args:
				curr 	numpy array of current
			Returns:
				None
			Errors:
				ExcessiveDriftError 	raised when the open channel current deviates
										from the baseline by driftThreshold * sigma.
				DriftRateError			raised when the slope of the open channel current
										exceeds maxDriftRate
		"""
		[mu,sd,sl]=self.__openchanstats(curr)
		
		# store stats
		self.minDrift=min(abs(mu), self.minDrift)
		self.maxDrift=max(abs(mu), self.maxDrift)
		self.minDriftR=min(sl, self.minDriftR)
		self.maxDriftR=max(sl, self.maxDriftR)

		sigma=self.driftThreshold
		if (abs(mu)<(abs(self.meanOpenCurr)-sigma*abs(self.sdOpenCurr))) or abs(mu)>(abs(self.meanOpenCurr)+sigma*abs(self.sdOpenCurr)):
			raise ExcessiveDriftError("The open channel current ({0:0.2f} pA) deviates from the baseline value ({1:0.2f}) by {2} sigma.".format(mu, self.meanOpenCurr, sigma))

		if (abs(sl)) > abs(self.maxDriftRate):
			raise DriftRateError("The open channel conductance is changing faster ({0} pA/s) than the allowed rate ({1} pA/s).".format(round(abs(sl),2), abs(round(self.maxDriftRate,2))))

		# Save teh open channel conductance stats for the current window
		self.windowOpenCurrentMean=mu
		self.windowOpenCurrentSD=sd 
		self.windowOpenCurrentSlope=sl

	#@profile
	def __eventsegment(self):
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

				# store the latest point in a fixed buffer
				self.preeventdat.append(t)
				
				# Mark the start of the event
				if abs(t) < self.thrCurr: 
					#print "event",
					self.eventstart=True
					self.eventdat=[]

				if self.eventstart:
					mean=abs(util.avg(self.preeventdat))
					while(abs(t)<mean):
						t=self.currData.popleft()
						self.eventdat.append(t)

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
						#sys.stderr.write('event mean curr={0:0.2f}, len(preeventdat)={1}\n'.format(sum(self.eventdat)/len(self.eventdat),len(self.preeventdat)))
						#print list(self.preeventdat) + self.eventdat + [ self.currData[i] for i in range(self.eventPad) ]
						#print "ecount=", self.eventcount, self.eventProcHnd
						self.__processEvent(
							 self.eventProcHnd(
								list(self.preeventdat) + self.eventdat + eventpaddat, 
								self.trajDataObj.FsHz,
								eventstart=len(self.preeventdat)+1,						# event start point
								eventend=len(self.preeventdat)+len(self.eventdat)+1,	# event end point
								baselinestats=[ self.windowOpenCurrentMean, self.sdOpenCurr, self.slopeOpenCurr ],
								algosettingsdict=self.eventProcSettingsDict,
								savets=self.writeEventTS
							)
						)
	
					self.preeventdat.clear()
		except IndexError:
			return

	def __processEvent(self, eventobj):
		if self.plotResults:
			self.UpdatePlot()

		if self.parallelProc:
			# handle parallel
			
			sys.stdout.flush()
			self.SendJobsChan.zmqSendData('job', cPickle.dumps(eventobj))
			
			# check for a message 100 times. If an empty message is recevied quit immediately
			for i in range(100):	
				recvdat=self.RecvResultsChan.zmqReceiveData()
				if recvdat=="":	# bail on receiving an empty message
					return

				self.eventprocessedcount+=1
				#store the processed event
				self.eventQueue.append( cPickle.loads(recvdat) )

		else:
			# call the process event function and store
			eventobj.processEvent()
			self.eventQueue.append( eventobj )

	# def __roundufloat(self, uf):
	# 	u=uncertainties
	# 	return u.ufloat(( round( u.nominal_value(uf), 4), round( u.std_dev(uf), 4) ))
