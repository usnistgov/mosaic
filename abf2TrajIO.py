"""
"""
import metaTrajIO
import abf.abf2load_gp as abf2

import numpy as np

class MultipleChannelError(Exception):
	pass

class abf2TrajIO(metaTrajIO.metaTrajIO):
	"""
	"""
	def __init__(self, **kwargs):
		"""
			Args:
				In addition to metaTrajIO.__init__ args,
					None
			Returns:
				None
			Errors:
				InsufficientArgumentsError if the mandatory arguments Rfb and Cfb are not set
		"""
		# base class processing first
		super(abf2TrajIO, self).__init__(**kwargs)

		# additional meta data
		self.fileFormat='abf'

	def appenddata(self, fname):
		"""
			Read one or more files and append their data to the data pipeline.
			Set a class attribute FsHz with the sampling frequency in Hz.

			Args:
				fname  list of data files to read
			Returns:
				None
			Errors:
				SamplingRateChangedError if the sampling rate for any data file differs from previous
		"""
		# Read a single file or a list of files.		
		for f in fname:
			[d, fs] = self.__readabf2(f)

			# set the sampling frequency in Hz. The times are in ms.
			# If the Fs attribute doesn't exist set it
			if not hasattr(self, 'FsHz'):	
				self.FsHz=fs 
			# else check if it s the same as before
			else:
				if self.FsHz!=fs:
					raise metaTrajIO.SamplingRateChangedError("The sampling rate in the data file '{0}' has changed.".format(f))

			# Add new data to the existing array
			self.currDataPipe=np.hstack((self.currDataPipe, d))

	def formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		# get base class formatting
		fmtstr=super(abf2TrajIO,self).formatsettings()

		return fmtstr

	def __readabf2(self, fname):
		"""
			Read and return the data from a single abf file with file 
			version > 2.0 as well as the sampling frequency in Hz.
		"""
		# Initialize the ABF2 reader
		a = abf2.ABF2(fname)

		# Read in the data from the file
		a.abf2load()

		if len(a.data) == 1:
			return [ a.data[0], a.samplingRateHz ]
		else:
			MultipleChannelError("Data from more than one channel is not supported.")
