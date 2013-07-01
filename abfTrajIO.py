"""
	A TrajIO class that supports ABF1 and ABF2 file formats via abf/abf.py. Currently, only
	gap-free mode and single channel recordings are supported.

	Author: Arvind Balijepalli
	Created: 5/23/2013

	ChangeLog:
		5/23/13		AB	Initial version

"""
import metaTrajIO
import abf.abf as abf

import numpy as np


class abfTrajIO(metaTrajIO.metaTrajIO):
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
				None
		"""
		# base class processing first
		super(abfTrajIO, self).__init__(**kwargs)

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
			[freq, hdr, dat] = abf.abfload_gp(f)

			# additional meta data
			self.fileFormat=hdr['fFileSignature']
	
			# set the sampling frequency in Hz. The times are in ms.
			# If the Fs attribute doesn't exist set it
			if not hasattr(self, 'FsHz'):	
				self.FsHz=freq
			# else check if it s the same as before
			else:
				if self.FsHz!=freq:
					raise metaTrajIO.SamplingRateChangedError("The sampling rate in the data file '{0}' has changed.".format(f))

			# Add new data to the existing array
			self.currDataPipe=np.hstack((self.currDataPipe, dat))

	def formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		# get base class formatting
		fmtstr=super(abfTrajIO,self).formatsettings()

		return fmtstr
