# -*- coding: utf-8 -*-
"""
	QDF implementation of metaTrajIO. Uses the readqdf module from EBS to 
	read individual qdf files.

	:Created: 7/18/2012
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		9/13/15 	AB 	Updated logging to use mosaicLogFormat class
		3/28/15 	AB 	Updated file read code to match new metaTrajIO API.
		7/18/12		AB	Initial version
		2/11/14		AB 	Support qdf files that save the current in pA. This needs 
						format='pA' argument.
"""
import types

import numpy as np 

import mosaic.trajio.metaTrajIO as metaTrajIO
import mosaic.utilities.mosaicLogging as mlog
import qdf.qdf as qdf

__all__ = ["qdfTrajIO"]

class qdfTrajIO(metaTrajIO.metaTrajIO):
	"""
		Use the readqdf module from EBS to read individual QDF files.

		In addition to :class:`~mosaic.metaTrajIO.metaTrajIO` args, check if the 
		feedback resistance (``Rfb``) and feedback capacitance (``Cfb``)
		are defined to convert qdf binary data into pA.

		A typical settings section to read QDF files is shown below. Note, that
		the values for ``Rfb`` and ``Cfb`` are specific to the amplifier used.

		.. code-block:: javascript

			"qdfTrajIO": {
	                "Rfb"                           : 9.1e+12,
	                "Cfb"                           : 1.07e-12,
	                "dcOffset"                      : 0.0,
	                "filter"                        : "*.qdf",
	                "start"                         : 0.0
	        	}

		:Parameters:
			In addition to metaTrajIO.__init__ args,
				- `Rfb` :		feedback resistance of amplifier
				- `Cfb` :		feedback capacitance of amplifier
				- `format` : 	'V' for voltage or 'pA' for current. Default is 'V'
		
		:Returns:
			None
		
		:Errors:
			- `InsufficientArgumentsError` : if the mandatory arguments ``Rfb`` and ``Cfb`` are not set.
	"""	
	
	def _init(self, **kwargs):
		if not hasattr(self, 'Rfb') or not hasattr(self, 'Cfb'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the feedback resistance (Rfb) and feedback capacitance (Cfb) to be defined.".format(type(self).__name__))

		if not hasattr(self, 'format'):
			self.format='V'

		# additional meta data
		self.fileFormat='qdf'

		self.qdfLogger=mlog.mosaicLogging().getLogger(name=__name__)

	def readdata(self, fname):
		"""
			Read one or more files and append their data to the data pipeline.
			Set a class attribute Fs with the sampling frequency in Hz.

			:Parameters:

				- `fname` :  list of data files to read
			
			:Returns:

				None
			
			:Errors:

				- `SamplingRateChangedError` : if the sampling rate for any data file differs from previous
		"""
		# Read a single file or a list of files. By setting scale_data 
		# and time_scale to 0, we get back times in ms and current in pA.
		# Check if the files have current of voltage.
		qdfdat=qdf.QDF(fname, float(self.Rfb), float(self.Cfb))
		if self.format=='V':
			q=qdfdat.VoltageToCurrent()
		else:
			q=qdfdat.Current()

		fs=qdfdat.qdftree["Sampling"].data[0]
		# set the sampling frequency in Hz.
		# If the Fs attribute doesn't exist set it
		if not hasattr(self, 'Fs'):	
			self.Fs=int(1./fs)
		# else check if it s the same as before
		else:
			if self.Fs!=int(1./fs):
				raise metaTrajIO.SamplingRateChangedError("The sampling rate in the data file '{0}' has changed.".format(fname))

		return np.array(q, dtype=np.float64)

	def _formatsettings(self):
		"""
			Log settings strings
		"""
		# for qdf files, add the values of the feedback resistance and capacitance
		self.qdfLogger.info( '\t\tFeedback resistance = {0} GOhm'.format(self.Rfb*1e-9) )
		self.qdfLogger.info( '\t\tFeedback capacitance = {0} pF'.format(self.Cfb*1e12) )
	

if __name__ == '__main__':
	from mosaic.utilities.resource_path import resource_path
	import os

	b=qdfTrajIO(
			dirname='data', 
			filter='*qdf',
			Rfb=9.1e9,
			Cfb=1.07e-12
		)

	for i in range(100):
		d=b.popdata(100000)
		print i, len(d)/100000., d[0], d[-1], np.mean(d), os.path.basename(b.LastFileProcessed)



