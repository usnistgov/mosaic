"""
Binary file implementation of metaTrajIO. Read raw binary files with specified record sizes

	:Created: 4/22/2013
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::

		1/27/15 	AB 	Memory map files on read.
		1/26/15 	AB 	Refactored code to read interleaved binary data. 
		7/27/14		AB 	Update interface to specify python PythonStructCode instead of 
						RecordSize. This will allow any binary file to be decoded
						The AmplifierScale and AmplifierOffset are set to 1 and 0
						respectively if PythonStructCode is an integer or short.
		4/22/13		AB	Initial version
"""
import struct

import mosaic.metaTrajIO

import numpy as np

class InvalidDataColumnError(Exception):
	pass

class binTrajIO(mosaic.metaTrajIO.metaTrajIO):
	"""
		Read a file that contains interleaved binary data, ordered by column. Only a single 
		column that holds ionic current data is read. The current in pA 
		is returned after scaling by the amplifier scale factor (``AmplifierScale``) and 
		removing any offsets (``AmplifierOffset``) if provided.

		:Usage and Assumptions:

				Binary data is interleaved by column. For three columns (*a*, *b*, and *c*) and *N* rows, 
				binary data is assumed to be of the form:

					[ a_1, b_1, c_1, a_2, b_2, c_2, ... ... ..., a_N, b_N, c_N ]

				The column layout is specified with the ``ColumnTypes`` parameter, which accepts a list of tuples. 
				For the example above, if column **a** is the ionic current in a 64-bit floating point format, 
				column **b** is the ionic current representation in 16-bit integer format and column **c** is 
				an index in 16-bit integer format, the ``ColumnTypes`` paramter is a list with three 
				tuples, one for each column, as shown below:

					[('curr_pA', 'float64'), ('AD_V', 'int16'), ('index', 'int16')]

				The first element of each tuple is an arbitrary text label and the second element is 
				a valid `Numpy type <http://docs.scipy.org/doc/numpy/user/basics.types.html>`_.

				Finally, the ``IonicCurrentColumn`` parameter holds the name (text label defined above) of the 
				column that holds the ionic current time-series. Note that if an integer column is selected, 
				the ``AmplifierScale`` and ``AmplifierOffset`` parameters can be used to convert the voltage from 
				the A/D to a current.

				Assuming that we use a floating point representation of the ionic current, and
				a sampling rate of 50 kHz, a settings section that will read the binary file format 
				defined above is:

				.. code-block:: javascript

					"binTrajIO": {
						"AmplifierScale" : "1",
						"AmplifierOffset" : "0",
						"SamplingFrequency" : "50000",
						"ColumnTypes" : "[('curr_pA', 'float64'), ('AD_V', 'int16'), ('index', 'int16')]",
						"IonicCurrentColumn" : "curr_pA",
						"dcOffset": "0.0", 
						"filter": "*.bin", 
						"start": "0.0"
					} 


		:Parameters:
				In addition to :class:`~mosaic.metaTrajIO.metaTrajIO` args,
					- `AmplifierScale` :		Full scale of amplifier (pA/2^nbits) that varies with the gain (default: 1.0).
					- `AmplifierOffset` :		Current offset in the recorded data in pA  (default: 0.0).
					- `SamplingFrequency` :	Sampling rate of data in the file in Hz.
					- `HeaderOffset` :		Ignore first *n* bytes of the file for header (default: 0 bytes).
					- `ColumnTypes` :	A list of tuples with column names and types (see `Numpy types <http://docs.scipy.org/doc/numpy/user/basics.types.html>`_). Note only integer and floating point numbers are supported.
					- `IonicCurrentColumn` : Column name that holds ionic current data.
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
			if type(self.ColumnTypes) is str or type(self.ColumnTypes) is unicode: 
				self.ColumnTypes=eval(self.ColumnTypes)
		
		if not hasattr(self, 'IonicCurrentColumn'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the ionic current column to be defined.".format(type(self).__name__))
		
		if not hasattr(self, 'HeaderOffset'):
			self.HeaderOffset=0

		try:
			self.IonicCurrentType=dict(self.ColumnTypes)[self.IonicCurrentColumn]
		except KeyError, err:
			self.IonicCurrentColumn=self.ColumnTypes[0][0]
			self.IonicCurrentType=self.ColumnTypes[0][1]

			print "IonicCurrentColumn {0} not found. Defaulting to {1}.".format(err, self.IonicCurrentColumn)


		if not hasattr(self, 'AmplifierScale'):
			self.AmplifierScale=1.0
		else:
			self.AmplifierScale=float(eval(self.AmplifierScale))

		if not hasattr(self, 'AmplifierOffset'): 
			self.AmplifierOffset=0.0
		else:
			self.AmplifierOffset=float(self.AmplifierOffset)

		# additional meta data
		self.fileFormat='bin'

		# set the sampling frequency in Hz.
		if not hasattr(self, 'Fs'):	
			self.Fs=self.SamplingFrequency

	def readdata(self, fname):
		"""
			Read one or more files and append their data to the data pipeline.
			Set a class attribute Fs with the sampling frequency in Hz.

			:Parameters:
				- `fname` :  list of data files to read
			:Returns:
				None
			:Errors:
				None
		"""
		tempdata=np.array([])
		# Read binary data and add it to the data pipe
		for f in fname:
			tempdata=np.hstack(( tempdata, self.readBinaryFile(f) ))

		return tempdata
		
	def _formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		fmtstr=""
		
		fmtstr+='\n\t\tAmplifier scale = {0} pA\n'.format(self.AmplifierScale)
		fmtstr+='\t\tAmplifier offset = {0} pA\n'.format(self.AmplifierOffset)
		fmtstr+='\t\tHeader offset = {0} bytes\n'.format(self.HeaderOffset)
		fmtstr+='\t\tData type = \'{0}\'\n'.format(self.IonicCurrentType)
	
		return fmtstr

	def readBinaryFile(self, fname):
		return self.transformData(np.memmap(fname, dtype=self.ColumnTypes, mode='r', offset=self.HeaderOffset)[self.IonicCurrentColumn])
		
	def transformData(self, data):
		return np.array(data*self.AmplifierScale-self.AmplifierOffset, dtype=np.float64)

if __name__ == '__main__':
	from mosaic.utilities.resource_path import resource_path

	print binTrajIO(
			fnames=['data/SingleChan-0001_1.bin'], 
			dcOffset=0, 
			start=0, 
			ColumnTypes=[('curr', 'float64')], 
			IonicCurrentColumn='curr', 
			HeaderOffset=0, 
			SamplingFrequency=500000
		).popdata(10)



