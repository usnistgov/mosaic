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
	def _init(self, **kwargs):
		"""
			Args:
				In addition to metaTrajIO.__init__ args,
					None
			Returns:
				None
			Errors:
				None
		"""
		pass
	
	def readdata(self, fname):
		"""
			Read one or more files and append their data to the data pipeline.
			Set a class attribute Fs with the sampling frequency in Hz.

			Args:
				fname  list of data files to read
			Returns:
				None
			Errors:
				SamplingRateChangedError if the sampling rate for any data file differs from previous
		"""
		tempdata=np.array([])
		
		# Read a single file or a list of files.		
		for f in fname:
			[freq, self.fileFormat, self.bandwidth, self.gain, dat] = abf.abfload_gp(f)
	
			# set the sampling frequency in Hz. The times are in ms.
			# If the Fs attribute doesn't exist set it
			if not hasattr(self, 'Fs'):	
				self.Fs=freq
			# else check if it s the same as before
			else:
				if self.Fs!=freq:
					raise metaTrajIO.SamplingRateChangedError("The sampling rate in the data file '{0}' has changed.".format(f))

			# Add new data to the existing array
			tempdata=np.hstack((tempdata, dat))

		return tempdata

	def _formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		fmtstr+='\t\tLowpass filter = {0} kHz\n'.format(self.bandwidth*0.001)
		fmtstr+='\t\tSignal gain = {0}\n'.format(self.gain)

		return fmtstr
