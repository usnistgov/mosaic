# -*- coding: utf-8 -*-
"""
Chimera VC100 concatenated file format implementation of metaTrajIO. Read concatenated chimera files with specified amplifier settings. 

	:Created: 7/11/2016
	:Author: 	Kyle Briggs <kbrig035@uottawa.ca>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		7/29/16         KB      Miscelleneous bugfixes
		7/11/16		KB	Initial version
"""
import struct

import mosaic.trajio.metaTrajIO as metaTrajIO
import mosaic.utilities.mosaicLogging as mlog
from mosaic.utilities.util import eval_

import numpy as np

__all__ = ["chimeraTrajIO", "InvalidDataColumnError"]

class InvalidDataColumnError(Exception):
	pass

class chimeraTrajIO(metaTrajIO.metaTrajIO):
	"""
		Read a file generated by the Chimera VC100. The current in pA 
		is returned after scaling by the amplifier scale factors.

		:Usage and Assumptions:

				Binary data is in a single column. As of 7/11/16 can only be unsigned 16 bit integers and has only one column:

				The column layout is specified with the ``ColumnTypes`` parameter, which accepts a list of tuples. 

					[('curr_pA', '<u2')]

				The option is left in in case of future changes to the platform, but can be left alone in the settings file for now.
				The first element of each tuple is an arbitrary text label and the second element is 
				a valid `Numpy type <http://docs.scipy.org/doc/numpy/user/basics.types.html>`_.

				Chimera gain settings are used to convert the integers stored by the ADC to current values.
				The following block provides an example. Parameters can be found in the .mat files output by the VC100.

				IMPORTANT: This setup assumes that all files that match `filter` have the same ADC settings.
				Future versions could imlement reading of the matching .mat files to remove the necessity
				to enter these parameters. 
				

				.. code-block:: javascript

					"chimeraTrajIO": {
						"TIAgain" : "100000000",
						"preADCgain" : "1.305",
						"SamplingFrequency" : "4166666.66667",
						"ColumnTypes" : "[('curr_pA', '<u2')]",
						"IonicCurrentColumn" : "curr_pA",
						"mVoffset": "-0.2776",
						"pAoffset": "2.0e-10",
						"ADCvref": "2.5",
						"ADCbits": "14",
						"filter": "*.log", 
						"start": "0.0",
						"HeaderOffset": "0"
					}
		
		:Parameters:
				In addition to :class:`~mosaic.metaTrajIO.metaTrajIO` args,
					
					- `SamplingFrequency` :	Sampling rate of data in the file in Hz.
					- `ColumnTypes` :	A list of tuples with column names and types (see `Numpy types <http://docs.scipy.org/doc/numpy/user/basics.types.html>`_). Note only integer and floating point numbers are supported.
					- `IonicCurrentColumn`: Column name that holds ionic current data.
					- `mVoffset` :		voltage offset of ADC
					- `ADCvref` :           voltage reference point for ADC
					- `ADCbits` :           amplifier scale precision in bits
					- `TIAgain` :		Feedback resistor value.
					- `preADCgain` :	analog gain before ADC
					- `HeaderOffset` :	Ignore first *n* bytes of the file for header (currently fixed at: 0 bytes).
		:Returns:
				None
		:Errors:
				None
	"""
	def _init(self, **kwargs):
		if not hasattr(self, 'SamplingFrequency'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the sampling rate in Hz to be defined.".format(type(self).__name__))

		if not hasattr(self, 'ColumnTypes'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the column types to be defined.".format(type(self).__name__))
		else:
			if type(self.ColumnTypes) is str or type(self.ColumnTypes) is str: 
				self.ColumnTypes=eval_(self.ColumnTypes)
		
		if not hasattr(self, 'IonicCurrentColumn'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the ionic current column to be defined.".format(type(self).__name__))
		
		if not hasattr(self, 'HeaderOffset'):
			self.HeaderOffset=0

		try:
			self.IonicCurrentType=dict(self.ColumnTypes)[self.IonicCurrentColumn]
		except KeyError as err:
			self.IonicCurrentColumn=self.ColumnTypes[0][0]
			self.IonicCurrentType=self.ColumnTypes[0][1]

			print("IonicCurrentColumn {0} not found. Defaulting to {1}.".format(err, self.IonicCurrentColumn))


		if not hasattr(self, 'TIAgain'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the TIAgain be specified as found in the appropriate .mat file.".format(type(self).__name__))
		else:
			self.TIAgain=float(self.TIAgain)

		if not hasattr(self, 'preADCgain'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the preADCgain be specified as found in the appropriate .mat file.".format(type(self).__name__))
		else:
			self.preADCgain=float(self.preADCgain)


		if not hasattr(self, 'mVoffset'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the mVoffset be specified as found in the appropriate .mat file.".format(type(self).__name__))
		else:
			self.mVoffset=float(self.mVoffset)

		if not hasattr(self, 'pAoffset'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the pAoffset be specified as found in the appropriate .mat file.".format(type(self).__name__))
		else:
			self.pAoffset=float(self.pAoffset)

		if not hasattr(self, 'ADCvref'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the ADCvref be specified as found in the appropriate .mat file.".format(type(self).__name__))
		else:
			self.ADCvref=float(self.ADCvref)

		if not hasattr(self, 'ADCbits'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the ADCbits be specified as found in the appropriate .mat file.".format(type(self).__name__))
		else:
			self.ADCbits=float(self.ADCbits)

		# additional meta data
		self.fileFormat='bin'

		# set the sampling frequency in Hz.
		if not hasattr(self, 'Fs'):	
			self.Fs=self.SamplingFrequency

		self.chimeraLogger=mlog.mosaicLogging().getLogger(name=__name__)

	def readdata(self, fname):
		"""
			Return raw data from a single data file. Set a class 
			attribute Fs with the sampling frequency in Hz.

			:Parameters:

				- `fname` :  fileame to read
			
			:Returns:
			
				- An array object that holds raw (unscaled) data from `fname`
			
			:Errors:

				None
		"""
		return self.readBinaryFile(fname)
		
	def _formatsettings(self):
		"""
			Populate `logObject` with settings strings for display

			:Parameters:

				- `logObject` : 	a object that holds logging text (see :class:`~mosaic.utilities.mosaicLog.mosaicLog`)				
		"""
		self.chimeraLogger.info( '\t\tTIAgain = {0} Ohms'.format(self.TIAgain) )
		self.chimeraLogger.info( '\t\tpreADCgain = {0} '.format(self.preADCgain) )
		self.chimeraLogger.info( '\t\tmVoffset = \'{0}\''.format(self.mVoffset) )
		self.chimeraLogger.info( '\t\tADCvref = \'{0}\''.format(self.ADCvref) )
		self.chimeraLogger.info( '\t\tADCbits = \'{0}\''.format(self.ADCbits) )
		self.chimeraLogger.info( '\t\tpAoffset = \'{0}\''.format(self.pAoffset) )
		self.chimeraLogger.info( '\t\tHeader offset = {0} bytes'.format(self.HeaderOffset) )
		self.chimeraLogger.info( '\t\tData type = \'{0}\''.format(self.IonicCurrentType) )
		

	def readBinaryFile(self, fname):
		return np.memmap(fname, dtype=self.ColumnTypes, mode='r', offset=self.HeaderOffset)[self.IonicCurrentColumn]
		
	def scaleData(self, data):
		"""
			See :func:`mosaic.metaTrajIO.metaTrajIO.scaleData`.
		"""
		gain = self.TIAgain * self.preADCgain
		bitmask = int((2**16 - 1) - (2**(16-self.ADCbits) - 1))
		data = data & bitmask
		data = self.ADCvref - 2*self.ADCvref*data.astype(float)/float(2**16)
		data = -data/gain + self.pAoffset
		return np.array(data*1.0e12, dtype=np.float64)

if __name__ == '__main__':
	print("Main funcion not implemented for chimeraTrajIO")



