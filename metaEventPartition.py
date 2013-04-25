from abc import ABCMeta, abstractmethod
import zmqWorker
import zmqIO
import multiprocessing 
import time

class metaEventPartition(object):
	"""
		An class to abstract partitioning individual events. Once a single 
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
			self.reserveNCPU=int(self.settingsDict.pop("reserveNCPU",1))
		except ValueError as err:
			raise commonExceptions.SettingsTypeError( err )

		# Shared variables 
		# Set the counters to be type Value so they can be shared if parallel is enabled
		self.eventcount=multiprocessing.Value('i', 0)
		self.eventprocessedcount=multiprocessing.Value('i', 0)

		# Event Queue. Use multiprocessing.Queue in case paralle is used
		self.eventQueue=multiprocessing.Queue()

		if self.parallelProc:
			# setup parallel processing here
			self.parallelProcDict={}

			nworkers=multiprocessing.cpu_count() - self.reserveNCPU
			
			# in parallel mode, we want at least 2 processes: one to do the work and the second
			# to poll for results
			if nworkers >= 2:
				# Parallel processing also needs zmq handles to send data to the worker processes and retrieve the results
				self.SendJobsChan=zmqIO.zmqIO(zmqIO.PUSH, { 'job' : '127.0.0.1:'+str(5500) } )
				
				tdict={}
				[ tdict.update( {'results'+str(i) : '127.0.0.1:'+str(5600+i*10) } ) for i in range(nworkers-1) ]

				# Setup a process for the polling thread
				self.pollingProc = multiprocessing.Process( target=self.PollResults, args=(tdict, self.eventcount, self.eventprocessedcount,self.eventQueue,) )
				self.pollingProc.start()
								
				for i in range(nworkers-1):
					self.parallelProcDict[i] = multiprocessing.Process(
													target=zmqWorker.zmqWorker, 
													args=( { 'job' : '127.0.0.1:'+str(5500) }, { 'results' : '127.0.0.1:'+str(5600+i*10) }, "processEvent",)
												)
					self.parallelProcDict[i].start()
				# allow the processes to start up
				time.sleep(1)

			else:
				print "At least two available CPUs are required for parallel. Reserving %d CPUs leaves only %d available processor(s) on this system.\nReverting to single CPU processing.\n\n" % (self.reserveNCPU, nworkers) 
				self.parallelProc=False

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
	def PollResults(self, portmap, eventcount, eventprocessedcount, eventQueue):
		"""
			Poll the reuslts of a parallel calculation. This must be implemented
			by the spcefic algorithm.
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

			#self.pollingProc.join()

			# shutdown the zmq channels
			self.SendJobsChan.zmqShutdown()

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
