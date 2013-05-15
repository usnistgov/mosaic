"""
	Read binary ionic current data into numpy arrays

	Author: Arvind Balijepalli
	Created:	7/17/2012

	ChangeLog:
		7/17/12		AB	Initial version
"""
from abc import ABCMeta, abstractmethod
import glob
import numpy as np

# define custom exceptions
class IncompatibleArgumentsError(Exception):
	pass
class InsufficientArgumentsError(Exception):
	pass
class IncorrectDataFormat(Exception):
	pass
class EndOfFileError(Exception):
	pass
class SamplingRateChangedError(Exception):
	pass
class EmptyDataPipeError(Exception):
	pass

class metaTrajIO(object):
	__metaclass__=ABCMeta

	def __init__(self, **kwargs):
		"""
			Initialize a TrajIO object. The object can load all the data in a directory,
			N files from a directory or from an explicit list of filenames. In addition 
			to the arguments defined below, implementations of this meta class may require 
			the definition of additional arguments. See the documentation of those classes
			for what those may be. For example, the qdfTrajIO implementation of metaTrajIO also requires
			the feedback resistance (Rfb) and feedback capacitance (Cfb) to be passed at initialization.

			Args: The arguments	passed to init change based on the method of file IO selected:
				dirname		all files from a directory ('<full path to data directory>')
				nfiles		if requesting N files (in addition to dirname) from a specified directory
				
				fnames 		explicit list of filenames ([file1, file2,...]). This argument 
							cannot be used in conjuction with dirname/nfiles. The filter 
							argument is ignored when used in combination with fnames. 

				filter='<wildcard filter>' (optional, filter is '*'' if not specified)
				start 		Data start point. This allows the first 'n' specified to be skipped
							and excluded from any data analysis
			Returns:
				None
			Errors:
				IncompatibleArgumentsError when arguments defined above are not used properly
		"""
		# start by setting all passed keyword arguments as class attributes
		for (k,v) in kwargs.iteritems():
			setattr(self, k, v)

		# Check if the passed arguments are sane	
		if hasattr(self, 'dirname') and hasattr(self, 'fnames'):
			raise IncompatibleArgumentsError("Cannot specify both directory name and explicit list of files when initializing class {0}.".format(type(self).__name__))

		# Check for the filter arg
		if not hasattr(self, 'filter'):
			self.filter='*'

		if hasattr(self, 'fnames'):
			# set fnames here.
			self.dataFiles=self.fnames
			delattr(self, 'fnames')
		else:
			try:
				if hasattr(self, 'dirname') and hasattr(self,'nfiles'):
					# N files from a directory
					self.dataFiles=glob.glob(str(self.dirname)+"/"+str(self.filter))[:int(self.nfiles)]
					delattr(self, 'dirname')
					delattr(self, 'nfiles')
				elif hasattr(self, 'dirname'):
					# all files from a directory
					self.dataFiles=glob.glob(str(self.dirname)+"/"+str(self.filter))
					delattr(self, 'dirname')
				else:
					raise IncompatibleArgumentsError("Arguments 'dirname' or 'fnames' must be supplied to initialize {0}".format(type(self).__name__))
			except AttributeError, err:
				raise IncompatibleArgumentsError(err)

		# set additional meta-data
		self.nFiles = len(self.dataFiles)
		self.fileFormat='N/A'
		self.datPath="/".join((self.dataFiles[0].split('/'))[:-1])

		# initialize an empty data pipeline
		self.currDataPipe=np.array([])
		# Track the start point of the queue. This var is used to manage
		# deletion more effectively, by not deleting elements every time 
		# popdata is called. Instead, data is actually deleted when the index
		# exceeds 1 million data points.
		self.currDataIdx=0


		# Last, on startup preview one data point to force
		# the sampling frequency FsHz to be set on startup
		self.previewdata(1)

		# Drop the first 'n' points specified by the start keyword
		if hasattr(self, 'start'):
			n=int( getattr(self, 'start') )
			self.popdata(n-1)

	#################################################################
	# Public API: functions
	#################################################################
	def popdata(self, n):
		"""
			Pop data points from self.currDataPipe. This function uses recursion 
			to automatically read data files when the queue length is shorter
			than the requested data points. When all data files are read, an
			EmptyDataPipeError is thrown.

			Args:
				n number of requested data points
			Returns:
				numpy array with requested data
			Errors:
				EmptyDataPipeError if the queue has fewer data points than requested.
		"""
		try:
			# Get the elements to return: index to (index+n)
			t=self.currDataPipe[self.currDataIdx:self.currDataIdx+n]
			if len(t) < n:
				raise IndexError

			# If the required data points were obtained, update the queue index
			self.currDataIdx+=n
			
			# delete them from the pipe if the index exceeds 1 million
			if self.currDataIdx>1000000:
				self.currDataPipe=np.delete(self.currDataPipe, np.s_[:self.currDataIdx:], axis=0)
				# reset the index
				self.currDataIdx=0

			# return the popped data
			return t
		except IndexError, err:
			fnames=self.popfnames(1)
			if len(fnames) > 0:
				self.appenddata(fnames)
				return self.popdata(n)
			else:
				if len(self.currDataPipe)-self.currDataIdx > 0:
					t=self.currDataPipe[self.currDataIdx:self.currDataIdx+n]
					self.currDataIdx=len(self.currDataPipe)

					return t
				else:
					raise EmptyDataPipeError("End of data.")
	
	def previewdata(self, n):
		"""
			Preview data points in self.currDataPipe. This function is identical in 
			behavior to popdata, except it does not remove data point from the queue.
			Like popdata, it uses recursion to automatically read data files 
			when the queue length is shorter than the requested data points. When all 
			data files are read, an	EmptyDataPipeError is thrown.

			Args:
				n number of requested data points
			Returns:
				numpy array with requested data
			Errors:
				EmptyDataPipeError if the queue has fewer data points than requested.
		"""
		try:
			# Get the elements to return
			t=self.currDataPipe[self.currDataIdx:self.currDataIdx+n]
			if len(t) < n:
				raise IndexError
			return t
		except IndexError, err:
			fnames=self.popfnames(1)
			if len(fnames) > 0:
				self.appenddata(fnames)
				return self.previewdata(n)
			else:
				if len(self.currDataPipe)-self.currDataIdx > 0:
					t=self.currDataPipe[self.currDataIdx:self.currDataIdx+n]
					self.currDataIdx=len(self.currDataPipe)

					return t
				else:
					raise EmptyDataPipeError("End of data.")

	def formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		fmtstr=""

		fmtstr+='\tTrajectory I/O settings: \n'
		fmtstr+='\t\tFiles processed = {0}\n'.format(self.nFiles-len(self.dataFiles))
		fmtstr+='\t\tData path = {0}\n'.format(self.datPath)
		fmtstr+='\t\tFile format = {0}\n'.format(self.fileFormat)
		fmtstr+='\t\tSampling frequency = {0} kHz\n'.format(self.FsHz*1e-3)

		return fmtstr

	#################################################################
	# Private API: Interface functions, implemented by sub-classes.
	# Should not be called from external classes
	#################################################################
	@abstractmethod
	def appenddata(self, fname):
		"""
			Read the specified data file(s) and append its data to the data pipeline. Set 
			a class attribute FsHz with the sampling frequency in Hz.

			Args:
				fname	list of filenames

			
			See implementations of metaTrajIO for specfic documentation.
		"""
		pass

	def popfnames(self, n):
		"""
			Pop n filenames from the start of self.dataFiles. If filenames run out, 
			simply return the available names. 
			Args:
				n 	number of requested filenames
			Returns:
				List of filenames if successful, empty list if not files remain
			Errors:
				None
		"""
		poplist=[]
		try:
			[ poplist.append(self.dataFiles.pop(0)) for i in range(n) ]
		except IndexError:
			pass
		return poplist


