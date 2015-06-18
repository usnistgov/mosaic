"""
	Read binary ionic current data into numpy arrays

	:Created:	7/17/2012
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT	
	:ChangeLog:
	.. line-block::
		4/1/15 		AB 	Added a new property (DataLengthSec) to estimate the length of a data set.
		3/28/15 	AB 	Optimized file read interface for improved large file support.
		8/22/14 	AB 	Setup a new property ('LastDataFile') that tracks the current
						data file being processed.
		5/27/14		AB 	Added dcOffset kwarg to initialization to allow 
						for offset correction in the ionic current data.
		2/13/14		AB 	Fixed a potential infinite recursion bug in the
						initialization. 
		7/17/12		AB	Initial version
"""
from abc import ABCMeta, abstractmethod
import glob
import numpy as np

import settings
from mosaic.utilities.resource_path import format_path, path_separator

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
class FileNotFoundError(Exception):
	pass

class metaTrajIO(object):
	"""
			.. warning:: |metaclass|

			Initialize a TrajIO object. The object can load all the data in a directory,
			N files from a directory or from an explicit list of filenames. In addition 
			to the arguments defined below, implementations of this meta class may require 
			the definition of additional arguments. See the documentation of those classes
			for what those may be. For example, the qdfTrajIO implementation of metaTrajIO also requires
			the feedback resistance (Rfb) and feedback capacitance (Cfb) to be passed at initialization.

			:Parameters:

				- `dirname` :		all files from a directory ('<full path to data directory>')
				- `nfiles` :		if requesting N files (in addition to dirname) from a specified directory
				- `fnames` : 		explicit list of filenames ([file1, file2,...]). This argument cannot be used in conjuction with dirname/nfiles. The filter argument is ignored when used in combination with fnames. 
				- `filter` :		'<wildcard filter>' (optional, filter is '*' if not specified)
				- `start` : 		Data start point in seconds.
				- `end` : 			Data end point in seconds.
				- `datafilter` :	Handle to the algorithm to use to filter the data. If no algorithm is specified, datafilter	is None and no filtering is performed.
				- `dcOffset` :		Subtract a DC offset from the ionic current data.
		

			:Properties:

				- `FsHz` :					sampling frequency in Hz. If the data was decimated, this property will hold the sampling frequency after decimation.
				- `LastFileProcessed` :		return the data file that was last processed.
				- `ElapsedTimeSeconds` : 	return the analysis time in sec.
			

			:Errors:

				- `IncompatibleArgumentsError` : 	when conflicting arguments are used.
				- `EmptyDataPipeError` : 			when out of data.
				- `FileNotFoundError` : 			when data files do not exist in the specified path.
				- `InsufficientArgumentsError` : 	when incompatible arguments are passed
	"""
	__metaclass__=ABCMeta

	def __init__(self, **kwargs):
		"""
		"""
		self.CHUNKSIZE=10000
		self.dataGenerator=None

		# start by setting all passed keyword arguments as class attributes
		for (k,v) in kwargs.iteritems():
			setattr(self, k, v)

		# Check if the passed arguments are sane	
		if hasattr(self, 'dirname') and hasattr(self, 'fnames'):
			raise IncompatibleArgumentsError("Incompatible arguments: expect either 'dirname' or 'fnames' when initializing class {0}.".format(type(self).__name__))

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
					self.dataFiles=glob.glob(format_path(str(self.dirname)+"/"+str(self.filter)))[:int(self.nfiles)]
					delattr(self, 'dirname')
					delattr(self, 'nfiles')
				elif hasattr(self, 'dirname'):
					# all files from a directory
					self.dataFiles=glob.glob(format_path(str(self.dirname)+"/"+str(self.filter)))
					delattr(self, 'dirname')
				else:
					raise IncompatibleArgumentsError("Missing arguments: 'dirname' or 'fnames' must be supplied to initialize {0}".format(type(self).__name__))
			except AttributeError, err:
				raise IncompatibleArgumentsError(err)

		# set additional meta-data
		self.nFiles = len(self.dataFiles)
		self.fileFormat='N/A'
		try:
			sep=path_separator()
			self.datPath=format_path(sep.join((self.dataFiles[0].split( sep ))[:-1]))
		except IndexError, err:
			raise FileNotFoundError("Files not found.")

		# setup data filtering
		if hasattr(self, 'datafilter'):
			self.dataFilter=True
			self.dataFilterObj=self._setupDataFilter()
		else:
			self.dataFilter=False

		if not hasattr(self, 'dcOffset'):
			self.dcOffset=0.0
		else:
			self.dcOffset=float(self.dcOffset)

		# set start to 0 if it doesn't exist
		if not hasattr(self, 'start'):
			self.start=0.

		# Track current filename
		self.currentFilename=self.dataFiles[0]

		# initialize an empty data pipeline
		self.currDataPipe=np.array([])
		# Track the start point of the queue. This var is used to manage
		# deletion more effectively, by not deleting elements every time 
		# popdata is called. Instead, data is actually deleted when the index
		# exceeds 1 million data points.
		self.currDataIdx=0

		# a var that determines if the end of the data stream is imminent.
		self.nearEndOfData=0

		# A global index that tracks the number of data points retrieved.
		self.globalDataIndex=0

		self.datLenSec=0

		self.initPipe=False

		# Call sub-class init
		self._init(**kwargs)

	#################################################################
	# Public API: functions
	#################################################################
	@property
	def FsHz(self):
		"""
			.. important:: |property|

			Return the sampling frequency in Hz.
		"""
		if not self.initPipe:
			self._initPipe()

		if not self.dataFilter:
			return self.Fs
		else:
			return self.dataFilterObj.filterFs

	@property
	def ElapsedTimeSeconds(self):
		"""
			.. important:: |property|

			Return the elapsed time in the time-series in seconds.
		"""
		if not self.initPipe:
			self._initPipe()

		return (self.globalDataIndex - self.startIndex)/float(self.FsHz) 

	@property 
	def LastFileProcessed(self):
		"""
			.. important:: |property|
			
			Return the last data file that was processed
		"""
		return self.currentFilename

	@property 
	def DataLengthSec(self):
		"""
			.. important:: |property|

			Return the approximate length of data that will be processed. If the data are in multiple files,
			this property assumes that each file contains an equal amount of data.
		"""
		if not self.initPipe:
			self._initPipe()

		return self.datLenSec


	def popdata(self, n):
		"""
			Pop data points from self.currDataPipe. This function uses recursion 
			to automatically read data files when the queue length is shorter
			than the requested data points. When all data files are read, an
			EmptyDataPipeError is thrown.

			:Parameters:

				- `n` : number of requested data points
			
			:Returns:
			
				- Numpy array with requested data

			:Errors:
				
				- `EmptyDataPipeError` : if the queue has fewer data points than requested.
		"""
		if not self.initPipe:
			self._initPipe()

		if self.nearEndOfData>1:
			raise EmptyDataPipeError("End of data.")

		# If the global index exceeds the specied end point, raise an EmptyDataPipError
		if hasattr(self, "end"):
			if self.globalDataIndex > self.endIndex:
				raise EmptyDataPipeError("End of data.")

		try:
			# Get the elements to return: index to (index+n)
			t=self.currDataPipe[self.currDataIdx:self.currDataIdx+n]-self.dcOffset
			
			if len(t) < n: raise IndexError

			# If the required data points were obtained, update the queue and global indices
			self.currDataIdx+=n
			self.globalDataIndex+=n
			
			# delete them from the pipe if the index exceeds 1 million
			if self.currDataIdx>1000000:
				self.currDataPipe=np.delete(self.currDataPipe, np.s_[:self.currDataIdx:], axis=0)
				# reset the index
				self.currDataIdx=0

			# return the popped data
			return t
		except IndexError, err:
			if self.nearEndOfData>0:
				self.currDataIdx+=n
				self.globalDataIndex+=n
				
				self.nearEndOfData+=1

				return t
			else:
				self._appenddata()
				return self.popdata(n)
				
	def previewdata(self, n):
		"""
			Preview data points in self.currDataPipe. This function is identical in 
			behavior to popdata, except it does not remove data point from the queue.
			Like popdata, it uses recursion to automatically read data files 
			when the queue length is shorter than the requested data points. When all 
			data files are read, an	EmptyDataPipeError is thrown.

			:Parameters:

				`n` : number of requested data points

			:Returns:

				- Numpy array with requested data

			:Errors:

				- `EmptyDataPipeError` : if the queue has fewer data points than requested.
		"""
		if not self.initPipe:
			self._initPipe()

		try:
			# Get the elements to return
			t=self.currDataPipe[self.currDataIdx:self.currDataIdx+n]-self.dcOffset
			if len(t) < n: raise IndexError
				
			return t
		except IndexError, err:
			self._appenddata()
			return self.previewdata(n)


	def formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		fmtstr=""

		# add the filter settings
		if self.dataFilter:
			fmtstr+=self.dataFilterObj.formatsettings()

		fmtstr+='\n\tTrajectory I/O settings: \n'
		fmtstr+='\t\tFiles processed = {0}\n'.format(self.nFiles-len(self.dataFiles))
		fmtstr+='\t\tData path = {0}\n'.format(self.datPath)
		fmtstr+='\t\tFile format = {0}\n'.format(self.fileFormat)
		fmtstr+='\t\tSampling frequency = {0} kHz\n'.format(self.FsHz*1e-3)

		# Sub-class formatted settings
		fmtstr+=self._formatsettings()

		return fmtstr

	#################################################################
	# Private API: Interface functions, implemented by sub-classes.
	# Should not be called from external classes
	#################################################################
	def _appenddata(self):
		"""
			Read the specified data file(s) and append its data to the data pipeline. Set 
			a class property FsHz with the sampling frequency in Hz.

			:Parameters:

				- None
			
			.. seealso:: See implementations of metaTrajIO for specfic documentation.
		"""
		try:			
			data=self.scaleData(self.dataGenerator.next())

			if self.dataFilter:
				self.dataFilterObj.filterData(data, self.Fs)
				self.currDataPipe=np.hstack((self.currDataPipe, self.dataFilterObj.filteredData ))
			else:
				self.currDataPipe=np.hstack((self.currDataPipe, data ))

		except (StopIteration, AttributeError):
			# Read a new data file to get more data
			fname=self.popfnames()
			if fname:
				self.rawData=self.readdata( fname )
				self.dataGenerator=self._createGenerator()
				self._appenddata()
		
	def scaleData(self, data):
		"""
			.. note:: |interfacemethod|

			Scale the raw data loaded with :func:`~mosaic.metaTrajIO.metaTrajIO.readdata`. Note this function will not necessarily receive the entire data array loaded with :func:`~mosaic.metaTrajIO.metaTrajIO.readdata`. Transformations must be able to process partial data chunks.

			:Parameters:
			
				- `data` : partial chunk of raw data loaded using :func:`~mosaic.metaTrajIO.metaTrajIO.readdata`.

			:Returns:

				- Array containing scaled data.

			:Default Behavior:

				- If not implemented by a sub-class, the default behavior is to return ``data`` to the calling function without modifications.

			:Example:

				Assuming the amplifier scale and offset values are stored in the class variables ``AmplifierScale`` and ``AmplifierOffset``, the raw data read using :func:`~mosaic.metaTrajIO.metaTrajIO.readdata` can be transformed by :func:`~mosaic.metaTrajIO.metaTrajIO.scaleData`. We can also use this function to change the array data type.

			.. code-block:: python

				def scaleData(self, data):
					return np.array(data*self.AmplifierScale-self.AmplifierOffset, dtype='f8')
		"""
		return data

	@abstractmethod
	def _formatsettings(self):
		"""
			.. important:: |abstractmethod|

			Return a formatted string of settings for display 
		"""
		pass
		
	@abstractmethod
	def _init(self, **kwargs):
		"""
			.. important:: |abstractmethod|

			This function is called at the end of the class constructor to perform additional initialization specific to the algorithm being implemented. The arguments to this function are identical to those passed to the class constructor.
		"""
		pass

	@abstractmethod
	def readdata(self, fname):
		"""
			.. important:: |abstractmethod|

			Return raw data from a single data file. Set a class 
			attribute Fs with the sampling frequency in Hz.

			:Parameters:

				- `fname` :  fileame to read
			
			:Returns:
			
				An array object that holds raw (unscaled) data from `fname`
			
			:Errors:
			
				None
		"""
		pass

	def popfnames(self):
		"""
			Pop a single filename from the start of ``self.dataFiles``. If ``self.dataFiles`` is empty,
			raise an ``EmptyDataPipeError`` error. 

			:Parameters:
			
				- None
			
			:Returns:
			
				A single filename if successful.

			:Errors:

				- `EmptyDataPipeError` : when the filename list is empty.

		"""
		try:
			return self.dataFiles.pop(0)
		except IndexError:
			if self.nearEndOfData:
				raise EmptyDataPipeError("End of data.")
			else:
				self.nearEndOfData+=1

	#################################################################
	# Internal Functions
	#################################################################
	def _initPipe(self):
		# Last, on startup load a single data file to force
		# the sampling frequency FsHz to be set on startup
		self._appenddata()
		
		self.initPipe=True

		# Set the end point
		if hasattr(self, 'end'):
			self.endIndex=int((self.end-1)*self.Fs)
			self.datLenSec=self.end-self.start
		else:
			self.datLenSec=(len(self.rawData)/float(self.Fs)*(len(self.dataFiles)+1))
			
		# Drop the first 'n' points specified by the start keyword
		if hasattr(self, 'start'):
			self.startIndex=int(self.start*self.Fs)
			if self.startIndex > 0:
				nBlks=int((self.startIndex-1)/self.CHUNKSIZE)
				for i in range(nBlks):
					self.popdata(self.CHUNKSIZE)

				self.popdata( int((self.startIndex-1)%self.CHUNKSIZE) )

	def _setupDataFilter(self):
		filtsettings=settings.settings( self.datPath ).getSettings(self.datafilter.__name__)
		if filtsettings=={}:
			print "No settings found for '{0}'. Data filtering is disabled".format(str(self.datafilter.__name__))
			self.dataFilter=False
			return

		return self.datafilter(**filtsettings)

	def _createGenerator(self):
		i=0
		while i<len(self.rawData):
			yield self.rawData[i:i+self.CHUNKSIZE]
			i+=self.CHUNKSIZE

