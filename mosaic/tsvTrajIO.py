# -*- coding: utf-8 -*-
"""
	An implementation of metaTrajIO that reads tab separated valued (TSV) files

	:Created: 	7/31/2012
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		3/28/15 	AB 	Updated file read code to match new metaTrajIO API.
		6/30/13		AB 	Added the 'seprator' kwarg to the class initializer to allow any delimited 
						files to be read. e.g. '"\\"t' (default), ',', etc.
		7/31/12		AB	Initial version

"""
import numpy as np 

import metaTrajIO
import csv

class tsvTrajIO(metaTrajIO.metaTrajIO):
	"""
		Read tab separated valued (TSV) files. 

		:Parameters:
			In addition to :class:`~mosaic.metaTrajIO.metaTrajIO` args,
				- `headers` : 		If True, the first row is ignored (default: True)
				- `separator` :	set the data separator (defualt: '"\\"t')
			
				Either:
					- `Fs` : 			Sampling frequency in Hz. If set, all other options are ignored and the first column in the file is assumed to be the current in pA.
				Or:
					- `nCols` :		number of columns in TSV file (default:2, first column is time in ms and second is current in pA) 
					- `timeCol` :		explicitly set the time column (default: 0, first col)
					- `currCol` :		explicitly set the position of the current column (default: 1)

			If neither ``Fs`` nor {``nCols``, ``timeCol``, ``currCol``} are set then the latter 
			is assumed with the listed default values.
		"""
	def _init(self, **kwargs):
		# Check if headers are present
		self.hasHeaders=bool(kwargs.pop('headers', True))
		try:
			# if the sampling frequency is set explicitly, currents 
			# in pA will be in column 0.
			self.Fs=float(kwargs["Fs"])
			self.currCol=0

			self.userSetFs=True
		except KeyError:
			# If Fs is not set explicitly assume by default two columns,
			# with time in sec in col 0 and current in pA in column 1, unless
			# specified otherwise by the user
			self.nCols=kwargs.pop('nCols', 2)
			self.timeCol=kwargs.pop('timeCol', 0)
			self.currCol=kwargs.pop('currCol', 1)

			self.userSetFs=True

		# The default data separator is a tab.
		self.separator=kwargs.pop('separator', '\t')

		# additional meta data
		self.fileFormat='tsv'

	def readdata(self, fname):
		"""
			Read a single TSV file and return raw (unscaled) data contained within it.
			Set/update a class attribute Fs with the sampling frequency in Hz.

			:Parameters:

				- `fname` :  fileame to read

			:Returns:

				- An array object that holds raw (unscaled) data from `fname`
				
			:Errors:
			
				- `SamplingRateChangedError` : if the sampling rate for any data file differs from previous
		"""
		return self.__readtsv(fname)

	def _formatsettings(self, logObject):
		"""
			Populate `logObject` with settings strings for display

			:Parameters:

				- `logObject` : 	a object that holds logging text (see :class:`~mosaic.utilities.mosaicLog.mosaicLog`)				
		"""
		return ""

	def __readtsv(self, fname):
		"""
		"""
		r1=csv.reader(open(fname,'rU'), delimiter=self.separator)

		# remove the file headers
		if self.hasHeaders: r1.next()

		# If the user explicitly set the sampling frequency,
		# self.currCol is set to 0 (current in pA). Stuff data 
		# into a numpy array
		if self.userSetFs:
			return np.array( [ float(row[self.currCol]) for row in r1 ], dtype=np.float64)
		else:
			# Calculate the sampling frequency from the first two points
			p1=r1.next()
			p2=r1.next()

			if not hasattr(self, 'Fs'):
				self.Fs=1000./(p2[self.timeCol]-p1[self.timeCol])
			# else check if it s the same as before
			else:
				if self.Fs!=1000./(p2[self.timeCol]-p1[self.timeCol]):
					raise metaTrajIO.SamplingRateChangedError("The sampling rate in the data file '{0}' has changed.".format(fname))
				
			# Store the ionic currents for the first two points
			dat=[p1[self.currCol], p2[self.currCol]]

			return np.array( dat.extend([ float(row[self.currCol]) for row in r1 ]), dtype=np.float64)
