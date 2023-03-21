# -*- coding: utf-8 -*-
"""
	A TrajIO class that supports ABF1 and ABF2 file formats via abf/abf.py. Currently, only
	gap-free mode and single channel recordings are supported.

	:Created: 5/23/2013
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		03/20/23 	AB  Use pyabf to read ABF files.
		9/13/15 	AB 	Updated logging to use mosaicLogFormat class
		3/28/15 	AB 	Updated file read code to match new metaTrajIO API.
		5/23/13		AB	Initial version

"""
import pyabf
import mosaic.trajio.metaTrajIO as metaTrajIO
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
	                "dcOffset"                      : 0.0,
	                "sweepNumber"					: 0,
	                "channel"						: 0
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
		if not hasattr(self, 'sweepNumber') or not hasattr(self, 'channel'):
			self.sweepNumber=0
			self.channel=0

		# additional meta data
		self.fileFormat='abf'

		abf=pyabf.ABF(fname)
		abf.setSweep(sweepNumber=self.sweepNumber, channel=self.channel)
		scale=self._currentScale(abf)

		# If the Fs attribute doesn't exist set it
		if not hasattr(self, 'Fs'):	
			self.Fs=abf.dataRate
		# else check if it s the same as before
		else:
			if self.Fs!=abf.dataRate:
				raise metaTrajIO.SamplingRateChangedError("The sampling rate in the data file '{0}' has changed.".format(f))

		return abf.sweepY*scale

	def _formatsettings(self):
		"""
			Log settings strings
		"""
		self.abfLogger.info( 'Sweep number = {0}'.format(self.sweepNumber) )
		self.abfLogger.info( 'Channel = {0}'.format(self.channel) )

	def _currentScale(self, abf):
		if "pA" in abf.sweepLabelY or "pA" in abf.sweepUnitsY: return 1
		if "nA" in abf.sweepLabelY or "nA" in abf.sweepUnitsY: return 1000

