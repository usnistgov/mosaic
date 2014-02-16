"""
	A meta class that quickly partitions trajectories into individual events.

	Author: 	Arvind Balijepalli
	Created:	4/22/2013

	ChangeLog:
		6/22/13		AB 	Added two function hooks to allow plotting 
						results in real-time. The first InitPlot must 
						be implemented to initialize a plot. The second
						UpdatePlot is used to update the plot data in 
						real-time and refresh the graphics. 
		4/22/13		AB	Initial version
"""
from abc import ABCMeta, abstractmethod
import zmqWorker
import zmqIO
import multiprocessing 
import time

class metaEventPartition(object):
	"""
		A class to abstract partitioning individual events. Once a single 
		molecule event is identified, it is handed off to to an event processor.
		If parallel processing is requested, detailed event processing will commence
		immediately. If not, detailed event processing is performed after the event 
		partition has completed.
	"""
	__metaclass__=ABCMeta

	def __init__(self, trajDataObj, eventProcHnd, eventPartitionSettings, eventProcSettings):
		"""
			Initialize a new event segment object
			Args:
				trajDataObj:			properly initialized object instantiated from a sub-class 
										of metaTrajIO.
				eventProcHnd:			handle to a sub-class of metaEventProcessor. Objects of 
										this class are initialized as necessary
				eventPartitionSettings	settings dictionary for the partition algorithm.
				eventProcSettings 		settings dictionary for the event processing algorithm.
			Returns:
				None
			
			Errors:
				None

			Common algorithm parameters from settings file (.settings in the data path or 
			current working directory):
				writeEventTS	Write event current data to file. (default: 1, write data to file)
				parallelProc	Process events in parallel using the pproc module. (default: 1, Yes)
				reserveNCPU		Reserve the specified number of CPUs and exclude them from the parallel pool
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

		if self.parallelProc:
			# setup parallel processing here
			self.parallelProcDict={}

			nworkers=multiprocessing.cpu_count() - self.reserveNCPU
			for i in range(nworkers):
				self.parallelProcDict[i] = multiprocessing.Process(
												target=zmqWorker.zmqWorker, 
												args=( { 'job' : '127.0.0.1:'+str(5500) }, { 'results' : '127.0.0.1:'+str(5600+i*10) }, "processEvent",)
											)
				self.parallelProcDict[i].start()
			# allow the processes to start up
			time.sleep(1)

			tdict={}
			[ tdict.update( {'results'+str(i) : '127.0.0.1:'+str(5600+i*10) } ) for i in range(nworkers) ]
			# Parallel processing also needs zmq handles to send data to the worker processes and retrieve the results
			self.SendJobsChan=zmqIO.zmqIO(zmqIO.PUSH, { 'job' : '127.0.0.1:'+str(5500) } )
			self.RecvResultsChan=zmqIO.zmqIO(zmqIO.PULL, tdict )

	# Define enter and exit funcs so this class can be used with a context manager
	def __enter__(self):
		return self

	def __exit__(self, type, value, traceback):
		self.Stop()

	@abstractmethod
	def PartitionEvents(self):
		"""
			This is the equivalent of a pure virtual function in C++. Specific event processing
			algorithms must implement this method. 

			An implementation of this function should separate individual events of interest from 
			a time-series of ionic current recordings. The data pertaining to each event is then passed
			to an instance of metaEventProcessor for detailed analysis. The function will collect the 
			results of this analysis.
		"""
		pass

	@abstractmethod
	def Stop(self):
		if self.parallelProc:
			# send a STOP message to all the processes
			for i in range(len(self.parallelProcDict)):
				self.SendJobsChan.zmqSendData('job','STOP')

			# wait for the processes to terminate
			for k in self.parallelProcDict.keys():
				self.parallelProcDict[k].join()

			# shutdown the zmq channels
			self.SendJobsChan.zmqShutdown()
			self.RecvResultsChan.zmqShutdown()

	@abstractmethod
	def InitPlot(self):
		"""
			Initialize a plotting window to display analysis results in real-time.
		"""
		pass

	@abstractmethod
	def UpdatePlot(self):
		"""
			Update plot data with new results as the analysis progresses.
		"""
		pass

	@abstractmethod
	def formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		pass

	@abstractmethod
	def formatstats(self):
		"""
			Return a formatted string of statistics for display
		"""
		pass

	@abstractmethod
	def formatoutputfiles(self):
		"""
			Return a formatted string of output files.
		"""
