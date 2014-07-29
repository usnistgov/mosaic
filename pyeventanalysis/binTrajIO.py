"""
Binary file implementation of metaTrajIO. Read raw binary files with specified record sizes

	Author: Arvind Balijepalli
	Created: 4/22/2013

	ChangeLog:
		7/27/14		AB 	Update interface to specify python PythonStructCode instead of 
						RecordSize. This will allow any binary file to be decoded
						The AmplifierScale and AmplifierOffset are set to 1 and 0
						respectively if PythonStructCode is an integer or short.
		4/22/13		AB	Initial version
"""
import struct

import metaTrajIO

import numpy as np

class InvalidPythonStructCodeError(Exception):
	pass

class binTrajIO(metaTrajIO.metaTrajIO):
	"""
		Read a binary file that contains single channel ionic current data and calculate the current in pA 
		after scaling by the amplifier scale factor and removing any offsets.
	"""
	def _init(self, **kwargs):
		"""
			Args:
				In addition to metaTrajIO.__init__ args,
					AmplifierScale		full scale of amplifier (in pA) that varies with the gain
					AmplifierOffset		current offset in the recorded data
					SamplingFrequency	sampling rate of data in the file in Hz
					HeaderOffset		ignore first 'n' bytes of the file for header (default: 0 bytes).
					PythonStructCode	Single character code for a python struct (see Python struct docs).
			Returns:
				None
			Errors:
				InsufficientArgumentsError if the mandatory arguments Rfb and Cfb are not set
		"""
		if not hasattr(self, 'SamplingFrequency'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the sampling rate in Hz to be defined.".format(type(self).__name__))
		if not hasattr(self, 'PythonStructCode'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the Python struct code to be defined.".format(type(self).__name__))

		if not hasattr(self, 'HeaderOffset'):
			self.HeaderOffset=0

		if not hasattr(self, 'AmplifierScale') and self.PythonStructCode in ['h', 'H', 'i', 'I', 'l', 'L', 'q', 'Q']:
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the amplifier scale in pA to be defined.".format(type(self).__name__))
		else:
			self.AmplifierScale=1.0
		if not hasattr(self, 'AmplifierOffset') and self.PythonStructCode in ['h', 'H', 'i', 'I', 'l', 'L', 'q', 'Q']:
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the amplifier offset in pA to be defined.".format(type(self).__name__))
		else:
			self.AmplifierOffset=0.0

		# additional meta data
		self.fileFormat='bin'

		# set the sampling frequency in Hz.
		if not hasattr(self, 'Fs'):	
			self.Fs=self.SamplingFrequency

		self.IntegerBits={'h':2, 'H':2, 'i':4, 'I':4, 'l':4, 'L':4, 'q':8, 'Q':8, 'f':4, 'd':8}

	def readdata(self, fname):
		"""
			Read one or more files and append their data to the data pipeline.
			Set a class attribute Fs with the sampling frequency in Hz.

			Args:
				fname  list of data files to read
			Returns:
				None
			Errors:
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
		fmtstr+='\t\tData type code = \'{0}\'\n'.format(self.PythonStructCode)
	
		return fmtstr

	def readBinaryFile(self, fname):
		CHUNKSIZE=4096

		if self.PythonStructCode in ['f', 'd']:
			scale=1
			offset=0
		elif self.PythonStructCode in ['h', 'H', 'i', 'I', 'l', 'L', 'q', 'Q']:
			bits=self.IntegerBits[self.PythonStructCode]*8
			scale=self.AmplifierScale/(2**bits)
			offset=self.AmplifierOffset
		else:
			raise InvalidPythonStructCodeError("Invalid Python struct code.")

		binfile=open(fname, 'rb')

		# Discard self.HeaderOffset bytes to remove the header
		binfile.read(self.HeaderOffset)

		parsedat=[]
		while True:
			bd=binfile.read(CHUNKSIZE)
			if bd=="":	#EOF
				break

			# read and parse the rest of the data
			parsedat.extend( self.parseChunk( bd, self.PythonStructCode, scale, offset ) )

		binfile.close()

		return parsedat

	def parseChunk(self, dat, structcode, scale, offset):
		pdat=struct.unpack('<' + str(int(len(dat)/float(self.IntegerBits[self.PythonStructCode]))) + structcode, dat)

		return [ dat*scale-offset for dat in pdat ]
