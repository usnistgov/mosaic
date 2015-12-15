# -*- coding: utf-8 -*-
"""
	A meta class that quickly partitions trajectories into individual events.

	:Created:	4/22/2013
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		12/11/15 	AB 	Refactor code
		12/6/15 	AB 	Add sampling frequency to analysis info table
		8/18/14		AB 	Fixed parallel processing cleanup.
		5/17/14		AB 	Delete Plotting support
		6/22/13		AB 	Added two function hooks to allow plotting 
						results in real-time. The first InitPlot must 
						be implemented to initialize a plot. The second
						UpdatePlot is used to update the plot data in 
						real-time and refresh the graphics. 
		4/22/13		AB	Initial version
"""
from abc import ABCMeta, abstractmethod

import sys
import signal
import os
import time
import datetime
import csv
import cPickle
import multiprocessing 

import numpy as np 
import uncertainties
from  collections import deque

import metaEventPartition
import commonExceptions
import metaTrajIO
import sqlite3MDIO
from mosaic.utilities.resource_path import format_path
from mosaic.utilities.ionic_current_stats import OpenCurrentDist

# custom errors
class ExcessiveDriftError(Exception):
	pass

class DriftRateError(Exception):
	pass

class metaEventPartition(object):
	"""
		.. warning:: |metaclass|

		A class to abstract partitioning individual events. Once a single 
		molecule event is identified, it is handed off to to an event processor.
		If parallel processing is requested, detailed event processing will commence
		immediately. If not, detailed event processing is performed after the event 
		partition has completed.

		:Parameters:
				- `trajDataObj` :		properly initialized object instantiated from a sub-class 
										of metaTrajIO.
				- `eventProcHnd` :		handle to a sub-class of metaEventProcessor. Objects of 
										this class are initialized as necessary
				- `eventPartitionSettings` :	settings dictionary for the partition algorithm.
				- `eventProcSettings` :		settings dictionary for the event processing algorithm.
				- `settingsString` :			settings dictionary in JSON format 
			
		Common algorithm parameters from settings file (.settings in the data path or 
		current working directory)

			- `writeEventTS` :	Write event current data to file. (default: 1, write data to file)
			- `parallelProc` :	Process events in parallel using the pproc module. (default: 1, Yes)
			- `reserveNCPU` :		Reserve the specified number of CPUs and exclude them from the parallel pool
	"""
	__metaclass__=ABCMeta

	def __init__(self, trajDataObj, eventProcHnd, eventPartitionSettings, eventProcSettings, settingsString):
		"""
			Initialize a new event segment object
		"""
		# Required arguments
		self.trajDataObj=trajDataObj
		self.eventProcHnd=eventProcHnd

		self.settingsDict = eventPartitionSettings 
		self.eventProcSettingsDict = eventProcSettings

		try:
			self.writeEventTS=int(self.settingsDict.pop("writeEventTS",1))
			self.parallelProc=int(self.settingsDict.pop("parallelProc",1))
			self.reserveNCPU=int(self.settingsDict.pop("reserveNCPU",2))
		except ValueError as err:
			raise commonExceptions.SettingsTypeError( err )

		sys.stdout.flush()

		self.logFileHnd=open(format_path(self.trajDataObj.datPath+'/eventProcessing.log'),'w')
		
		self.tEventProcObj=self.eventProcHnd([], self.trajDataObj.FsHz, eventstart=0,eventend=0, baselinestats=[ 0,0,0 ], algosettingsdict=self.eventProcSettingsDict.copy(), savets=False, absdatidx=0, datafileHnd=None )

		self.mdioDBHnd=sqlite3MDIO.sqlite3MDIO()
		self.mdioDBHnd.initDB(
								dbPath=self.trajDataObj.datPath, 
								tableName='metadata',
								colNames=(self.tEventProcObj.mdHeadings())+['TimeSeries'],
								colNames_t=(self.tEventProcObj.mdHeadingDataType())+['REAL_LIST']
							)
		self.mdioDBHnd.writeSettings(settingsString)
		if self.trajDataObj.dataFilter:
			self.fstring=type(self.trajDataObj.dataFilterObj).__name__
		else:
			self.fstring='None'

		self._writeanalysisinfo()

		if self.parallelProc:
			self._setupparallel()


		self._init(trajDataObj, eventProcHnd, eventPartitionSettings, eventProcSettings)

	# Define enter and exit funcs so this class can be used with a context manager
	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.Stop()

	def Stop(self):
		"""
			Stop processing data.
		"""
		if self.parallelProc:
			# send a STOP message to all the processes
			for i in range(len(self.parallelProcDict)):
				self.SendJobsChan.zmqSendData('job','STOP')
			
			# wait for the processes to terminate
			for k in self.parallelProcDict.keys():
				os.kill( self.parallelProcDict[k].pid, signal.SIGINT )
				# self.parallelProcDict[k].terminate()
			for k in self.parallelProcDict.keys():
				self.parallelProcDict[k].join()

			# shutdown the zmq channels
			self.SendJobsChan.zmqShutdown()
			self.RecvResultsChan.zmqShutdown()

		self._stop()

	def PartitionEvents(self):
		"""
			Partition events within a time-series.
		"""
		self.outputString="Start time: "+str(datetime.datetime.now().strftime('%Y-%m-%d %I:%M %p'))+"\n\n"
		# write out first stage results
		sys.stdout.write(self.outputString)
		self.logFileHnd.write(self.outputString)
		# write the start time to the database
		self.mdioDBHnd.writeAnalysisLog(self.outputString)

		# Initialize segmentation
		self._setuppartition()

		try:
			startTime=time.time()
			while(1):	
				# with each pass obtain more data and
				d=self.trajDataObj.popdata(self.nPoints)
				# Check for excessive open channel drift
				self._checkdrift(d)

				# store the new data into a local store
				self.currData.extend(list(d))
				
				# update analysis info
				self._writeanalysisinfo()

				#print self.meanOpenCurr, self.minDrift, self.maxDrift, self.minDriftR, self.maxDriftR

				# Process the data segment for events
				if (self.meanOpenCurr > self.minBaseline and self.meanOpenCurr < self.maxBaseline) or self.minBaseline == -1.0 or self.maxBaseline == -1.0:
                                        self._eventsegment()
                                else: #skip over bad data, no need to abort
                                        continue


		except metaTrajIO.EmptyDataPipeError, err:
			self.segmentTime=time.time()-startTime
			self.outputString='[Status]\n\tSegment trajectory: ***NORMAL***\n'
		except (ExcessiveDriftError, DriftRateError) as err:
			self.segmentTime=time.time()-startTime
			self.outputString='[Status]\n\tSegment trajectory: ***ERROR***\n\t\t{0}\n'.format(str(err))
		except KeyboardInterrupt, err:
			self.segmentTime=time.time()-startTime
			self.outputString='[Status]\n\tSegment trajectory: ***USER STOP***\n'
		except:
			raise

		# write out first stage results
		sys.stdout.write(self.outputString)
		self.logFileHnd.write(self.outputString)

		# write the first stage output log to the database
		tstr=self.mdioDBHnd.readAnalysisLog()+self.outputString
		self.mdioDBHnd.writeAnalysisLog(tstr)
		
		# Finish processing events
		self._cleanupeventprocessing()

		# Write the output log file
		self._writeoutputlog()
	
		self.logFileHnd.write(self.outputString)
		self.logFileHnd.close()

		# write the output log to the database
		tstr=self.mdioDBHnd.readAnalysisLog()+self.outputString
		self.mdioDBHnd.writeAnalysisLog(tstr)

		self.mdioDBHnd.closeDB()

	#################################################################
	# Interface functions
	#################################################################
	@abstractmethod
	def _init(self, trajDataObj, eventProcHnd, eventPartitionSettings, eventProcSettings):
		"""
			.. important:: |abstractmethod|

			This function is called at the end of the class constructor to perform additional initialization specific to the algorithm being implemented. The arguments to this function are identical to those passed to the class constructor.
		"""
		pass

	@abstractmethod
	def _stop(self):
		"""
			.. important:: |abstractmethod|

			Stop partitioning events froma time-series
		"""
		pass

	@abstractmethod
	def formatsettings(self):
		"""
			.. important:: |abstractmethod|

			Return a formatted string of settings for display
		"""
		pass

	@abstractmethod
	def formatstats(self):
		"""
			.. important:: |abstractmethod|

			Return a formatted string of statistics for display
		"""
		pass

	@abstractmethod
	def formatoutputfiles(self):
		"""
			.. important:: |abstractmethod|

			Return a formatted string of output files.
		"""

	@abstractmethod
	def _eventsegment(self):
		"""
			.. important:: |abstractmethod|

			An implementation of this function should separate individual events of interest from a time-series of ionic current recordings. The data pertaining to each event is then passed 		to an instance of metaEventProcessor for detailed analysis. The function will collect the results of this analysis.
		"""
		pass

	@abstractmethod
	def _checkdrift(self, curr):
		"""
			.. important:: |abstractmethod|

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
		pass			

	#################################################################
	# Internal functions
	#################################################################
	def _writeanalysisinfo(self):
		self.mdioDBHnd.writeAnalysisInfo([
							self.trajDataObj.datPath,
							self.trajDataObj.fileFormat,
							type(self).__name__,
							type(self.tEventProcObj).__name__,
							self.fstring,
							self.trajDataObj.ElapsedTimeSeconds,
							self.trajDataObj.DataLengthSec,
							self.trajDataObj.FsHz
						])

	def _setupparallel(self):
		# check if parallel is available
		try:
			import zmqWorker
			import zmqIO
		except ImportError:
			print "Parallel processing is not available.\n"
			self.parallelProc=False
			return

		# setup parallel processing here
		self.parallelProcDict={}

		nworkers=multiprocessing.cpu_count() - self.reserveNCPU
		for i in range(nworkers):
			self.parallelProcDict[i] = multiprocessing.Process(
											target=zmqWorker.zmqWorker, 
											args=( 
												{ 'job' : '127.0.0.1:'+str(5500) }, 
												{ 'results' : '127.0.0.1:'+str(5600+i*10) }, 
												"processEvent",
												[ 
													"sqlite3MDIO", 
													self.mdioDBHnd.dbFilename,
													(self.tEventProcObj.mdHeadings())+['TimeSeries'],
													(self.tEventProcObj.mdHeadingDataType())+['REAL_LIST'] 
												],
											)
										)
			self.parallelProcDict[i].start()
		# allow the processes to start up
		time.sleep(1)

		tdict={}
		[ tdict.update( {'results'+str(i) : '127.0.0.1:'+str(5600+i*10) } ) for i in range(nworkers) ]
		# Parallel processing also needs zmq handles to send data to the worker processes and retrieve the results
		self.SendJobsChan=zmqIO.zmqIO(zmqIO.PUSH, { 'job' : '127.0.0.1:'+str(5500) } )
		self.RecvResultsChan=zmqIO.zmqIO(zmqIO.PULL, tdict )

	def _setuppartition(self):
		# At the start of a run, store baseline stats for the open channel state
		# Later, we use these values to detect drift
		# First, calculate the number of points to include using the blockSizeSec 
		# class attribute and the sampling frequency specified in trajDataObj
		self.nPoints=int(self.blockSizeSec*self.trajDataObj.FsHz)

		# a global counter that keeps track of the position in data pipe.
		self.globalDataIndex=0
		self.dataStart=0

		if self.meanOpenCurr == -1. or self.sdOpenCurr == -1. or self.slopeOpenCurr == -1.:
			[ self.meanOpenCurr, self.sdOpenCurr, self.slopeOpenCurr ] = self._openchanstats(self.trajDataObj.previewdata(self.nPoints))
		else:
			print "Automatic open channel state estimation has been disabled."

		# Initialize a FIFO queue to keep track of open channel conductance
		#self.openchanFIFO=npfifo.npfifo(nPoints)
		
		# setup a local data store that is used by the main event partition loop
		self.currData = deque()

		#### Event Queue ####
		# self.eventQueue=[]

		#### Vars for event partition stats ####
		self.minDrift=abs(self.meanOpenCurr)
		self.maxDrift=abs(self.meanOpenCurr)
		self.minDriftR=self.slopeOpenCurr
		self.maxDriftR=self.slopeOpenCurr

	def _cleanupeventprocessing(self):
		# Process individual events identified by the segmenting algorithm
		startTime=time.time()
		try:
			if self.parallelProc:
				# gather up any remaining results from the worker processes
				while self.eventprocessedcount < self.eventcount:
					recvdat=self.RecvResultsChan.zmqReceiveData()
					if recvdat != "":
						#store the processed event
						self.eventprocessedcount+=1

						if self.eventprocessedcount%100 == 0:
							sys.stdout.write('Processing %d of %d events.\r' % (self.eventprocessedcount,self.eventcount) )
	    					sys.stdout.flush()

			self.outputString='\tProcess events: ***NORMAL***\n\n\n'
			self.procTime=time.time()-startTime
		except KeyboardInterrupt:
			self.procTime=time.time()-startTime
			self.outputString+='\tProcess events: ***USER STOP***\n\n\n'
		except BaseException, err:
			self.outputString='\tProcess events: ***ERROR***\n\t\t{0}\n\n\n'.format(str(err))
			self.procTime=time.time()-startTime
			raise

		sys.stdout.write('                                                                    \r' )
		sys.stdout.flush()

	def _writeoutputlog(self):
		self.outputString+='[Summary]\n'

		# write out event segment stats
		self.outputString+=self.formatstats()

		self.outputString+="\n[Settings]\n"

		# write out trajectory IO settings
		self.outputString+=self.trajDataObj.formatsettings()+'\n'
		
		# write out event segment settings/stats
		self.outputString+=self.formatsettings()+'\n\n'

		# event processing settings
		self.outputString+=self.tEventProcObj.formatsettings()+'\n'

		# Output files
		self.outputString+=self.formatoutputfiles()
		self.outputString+='\t\tLog file = eventProcessing.log\n\n\n'

		# Finally, timing information
		self.outputString+='[Timing]\n\t\tSegment trajectory = {0} s\n'.format(round(self.segmentTime,2))
		self.outputString+='\t\tProcess events = {0} s\n\n'.format(round(self.procTime,2))
		self.outputString+='\t\tTotal = {0} s\n'.format(round(self.segmentTime+self.procTime,2))
		if self.eventcount > 0:
			self.outputString+='\t\tTime per event = {0} ms\n\n\n'.format(round(1000.*(self.segmentTime+self.procTime)/float(self.eventcount),2))
		
		# write it all out to stdout and also to a file
		# eventProcessing.log in the data location
		sys.stdout.write(self.outputString)
			
	def _openchanstats(self, curr):
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
		
		# Calculate the mean and standard deviation of the open state
		mu, sig=OpenCurrentDist(curr, 0.5, self.minBaseline, self.maxBaseline)

		# Fit the data to a straight line to calculate the slope
		# ft[0]: slope
		# ft[1]: y-intercept (mean current)
		ft = np.polyfit(tstamp, curr, 1)

		# Return stats
		return [ mu, sig, ft[0] ]


	def _processEvent(self, eventobj):
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
				# self.eventQueue.append( cPickle.loads(recvdat) )

		else:
			# First set the meta-data IO object in eventobj
			eventobj.dataFileHnd=self.mdioDBHnd

			# call the process event function and store
			eventobj.processEvent()
			# self.eventQueue.append( eventobj )
