"""
Binary file implementation of metaTrajIO. Read raw binary files with specified record sizes

	Author: Arvind Balijepalli
	Created: 4/22/2013

	ChangeLog:
		4/22/13		AB	Initial version
"""
import struct

import metaTrajIO

import numpy as np

class binTrajIO(metaTrajIO.metaTrajIO):
	"""
		Read a binary file that contains single channel ionic current data and calculate the current in pA 
		after scaling by the amplifier scale factor and removing any offsets.
	"""
	def __init__(self, **kwargs):
		"""
			Args:
				In addition to metaTrajIO.__init__ args,
					AmplifierScale		full scale of amplifier (in pA) that varies with the gain
					AmplifierOffset		current offset in the recorded data
					SamplingFrequency	sampling rate of data in the file in Hz
					HeaderOffset		ignore first 'n' bytes of the file for header.
					RecordSize			size in bytes of each data point (always assume unsigned). Acceptable values
										are 1, 2 or 4.
			Returns:
				None
			Errors:
				InsufficientArgumentsError if the mandatory arguments Rfb and Cfb are not set
		"""
		# base class processing first
		super(binTrajIO, self).__init__(**kwargs)

		if not hasattr(self, 'AmplifierScale'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the amplifier scale in pA to be defined.".format(type(self).__name__))
		if not hasattr(self, 'AmplifierOffset'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the amplifier offset in pA to be defined.".format(type(self).__name__))
		if not hasattr(self, 'SamplingFrequency'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the sampling rate in Hz to be defined.".format(type(self).__name__))
		if not hasattr(self, 'HeaderOffset'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the header offset in bytes to be defined.".format(type(self).__name__))
		if not hasattr(self, 'RecordSize'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the size of the data in bytes to be defined.".format(type(self).__name__))

		# additional meta data
		self.fileFormat='bin'

		# set the sampling frequency in Hz.
		if not hasattr(self, 'Fs'):	
			self.Fs=self.SamplingFrequency

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
		
	def formatsettings(self):
		"""
			Return a formatted string of settings for display
		"""
		# get base class formatting
		fmtstr=super(binTrajIO,self).formatsettings()

		# for qdf files, add the values of the feedback resistance and capacitance
		fmtstr+='\n\t\tAmplifier scale = {0} pA\n'.format(self.AmplifierScale)
		fmtstr+='\t\tAmplifier offset = {0} pA\n'.format(self.AmplifierOffset)
		fmtstr+='\t\tHeader offset = {0} bytes\n'.format(self.HeaderOffset)
		fmtstr+='\t\tRecord size = {0} bytes\n'.format(self.RecordSize)
	
		return fmtstr

	def readBinaryFile(self, fname):
		try:
			structcode = { 1 : 'B', 2 : 'H', 4 : 'I'}[self.RecordSize]
		except KeyError:
			raise IncompatibleArgumentsError('Record size must be 1, 2 or 4 bytes, got {0} bytes instead.' % self.RecordSize)
		
		CHUNKSIZE=4096

		bits=self.RecordSize*8
		scale=self.AmplifierScale/(2**bits)

		binfile=open(fname, 'rb')

		# Discard self.HeaderOffset bytes to remove the header
		binfile.read(self.HeaderOffset)

		parsedat=[]
		while True:
			bd=binfile.read(CHUNKSIZE)
			if bd=="":	#EOF
				break

			# read and parse the rest of the data
			parsedat.extend( self.parseChunk( bd, structcode, scale, self.AmplifierOffset ) )

		binfile.close()

		return parsedat

	def parseChunk(self, dat, structcode, scale, offset):
		pdat=struct.unpack('<' + str(int(len(dat)/float(self.RecordSize))) + structcode, dat)

		return [ dat*scale-offset for dat in pdat ]
