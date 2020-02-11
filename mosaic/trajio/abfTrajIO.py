# -*- coding: utf-8 -*-
"""
	A TrajIO class that supports ABF1 and ABF2 file formats via abf/abf.py. Currently, only
	gap-free mode and single channel recordings are supported.

	:Created: 5/23/2013
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		9/13/15 	AB 	Updated logging to use mosaicLogFormat class
		3/28/15 	AB 	Updated file read code to match new metaTrajIO API.
		5/23/13		AB	Initial version

"""
import mosaic.trajio.metaTrajIO as metaTrajIO
import mosaic.trajio.abf.abf as abf
import mosaic.utilities.mosaicLogging as mlog

import numpy as np

__all__ = ["abfTrajIO"]

class abfTrajIO(metaTrajIO.metaTrajIO):
	"""
		Read ABF1 and ABF2 file formats. Currently, only 
		gap-free mode and single channel recordings are supported.

		A typical settings section to read ABF files is shown below.

		.. code-block:: javascript

			"abfTrajIO" : {
	                "filter"                        : "*.abf",
	                "start"                         : 0.0,
	                "dcOffset"                      : 0.0
	        	}
        

		:Parameters:
			In addition to :class:`~mosaic.metaTrajIO.metaTrajIO` args,
				None
		"""
	def _init(self, **kwargs):
		self.abfLogger=mlog.mosaicLogging().getLogger(name=__name__)
	
	def readdata(self, fname):
		"""
			Read one or more files and append their data to the data pipeline.
			Set a class attribute Fs with the sampling frequency in Hz.

			:Parameters:
			
				- `fname` :  fileame to read
			
			:Returns:

				- An array object that holds raw (unscaled) data from `fname`
			
			:Errors:

				- `SamplingRateChangedError` : if the sampling rate for any data file differs from previous
		"""
		[freq, self.fileFormat, self.bandwidth, self.gain, dat] = abf.abfload_gp(fname)
	
		# set the sampling frequency in Hz. The times are in ms.
		# If the Fs attribute doesn't exist set it
		if not hasattr(self, 'Fs'):	
			self.Fs=freq
		# else check if it s the same as before
		else:
			if self.Fs!=freq:
				raise metaTrajIO.SamplingRateChangedError("The sampling rate in the data file '{0}' has changed.".format(f))

		return dat

	def _formatsettings(self):
		"""
			Log settings strings
		"""
		self.abfLogger.info( 'Lowpass filter = {0} kHz'.format(self.bandwidth*0.001) )
		self.abfLogger.info( 'Signal gain = {0}'.format(self.gain) )

