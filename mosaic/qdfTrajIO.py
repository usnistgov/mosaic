# -*- coding: utf-8 -*-
"""
	QDF implementation of metaTrajIO. Uses the readqdf module from EBS to 
	read individual qdf files.

	:Created: 7/18/2012
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		9/13/15 	AB 	Updated logging to use mosaicLog class
		3/28/15 	AB 	Updated file read code to match new metaTrajIO API.
		7/18/12		AB	Initial version
		2/11/14		AB 	Support qdf files that save the current in pA. This needs 
						format='pA' argument.
"""
import types

import numpy as np 

import mosaic.metaTrajIO
import mosaic.utilities.mosaicLog as log
import qdf.readqdf as qdf

__all__ = ["qdfTrajIO"]

class qdfTrajIO(mosaic.metaTrajIO.metaTrajIO):
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
		if self.format=='V':
			q=qdf.qdf_V2I([fname], float(self.Cfb), float(self.Rfb), scale_data=0, time_scale=0)
		else:
			q=qdf.qdf_I([fname], float(self.Cfb), float(self.Rfb), scale_data=0, time_scale=0)

		# set the sampling frequency in Hz. The times are in ms.
		# If the Fs attribute doesn't exist set it
		if not hasattr(self, 'Fs'):	
			self.Fs=1000./(q[1][0]-q[0][0])
		# else check if it s the same as before
		else:
			if self.Fs!=1000./(q[1][0]-q[0][0]):
				raise metaTrajIO.SamplingRateChangedError("The sampling rate in the data file '{0}' has changed.".format(fname))

		# Slice the data to remove the time-stamps to conserve memory		
		# and add new data to the existing array
		#print "last raw current val in file ", fname, " = ", q[-1]
		return np.array(q[ : , 1], dtype=np.float64)

	def _formatsettings(self, logObject):
		"""
			Populate `logObject` with settings strings for display

			:Parameters:

				- `logObject` : 	a object that holds logging text (see :class:`~mosaic.utilities.mosaicLog.mosaicLog`)				
		"""
		# for qdf files, add the values of the feedback resistance and capacitance
		logObject.addLogText( 'Feedback resistance = {0} GOhm'.format(self.Rfb*1e-9) )
		logObject.addLogText( 'Feedback capacitance = {0} pF'.format(self.Cfb*1e12) )
	

if __name__ == '__main__':
	from mosaic.utilities.resource_path import resource_path
	import os

	b=qdfTrajIO(
			dirname='data', 
			filter='*qdf',
			Rfb=9.16e9,
			Cfb=1.07e-12
		)

	for i in range(100):
		d=b.popdata(100000)
		print i, len(d)/100000., d[0], d[-1], np.mean(d), os.path.basename(b.LastFileProcessed)



