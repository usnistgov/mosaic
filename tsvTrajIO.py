"""
	An implementation of metaTrajIO that reads tab separated valued (TSV) files

	Author: Arvind Balijepalli
	Created: 7/31/2012

	ChangeLog:
		7/31/12		AB	Initial version
		6/30/13		AB 	Added the 'seprator' kwarg to the class initializer to allow any delimited 
						files to be read. e.g. '\t' (default), ',', etc.
"""
import numpy as np 

import metaTrajIO
import csv

class tsvTrajIO(metaTrajIO.metaTrajIO):
	"""
	"""
	def __init__(self, **kwargs):
		"""
			Perform additional initialization checks. Check if kwarg 'timeCol' is set to a number.

			In addition to metaTrajIO.__init__ args,
			Optional Args:
				headers		If True, the first row is ignored (default: True)
				separator	set the data separator (defualt: '\t')
				
				Either:
					Fs 			Sampling frequency in Hz. If set, all other options are ignored
								and the first column in the file is assumed to be the current in pA.
				Or:
					nCols		number of columns in TSV file (default:2, first column is time 
								in ms and second is current in pA) 
					timeCol		explicitly set the time column (default: 0, first col)
					currCol		explicitly set the position of the current column (default: 1)

				If neither 'Fs' nor {'nCols', 'timeCol','currCol'} are set then the latter 
				is assumed with the listed default values.
		"""
		# Check if headers are present
		self.hasHeaders=kwargs.pop('headers', True)
		try:
			# if the sampling frequency is set explicitly, currents 
			# in pA will be in column 0.
			self.FsHz=kwargs["Fs"]
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

		# base class processing last
		super(tsvTrajIO, self).__init__(**kwargs)

		# additional meta data
		self.fileFormat='tsv'

	def appenddata(self, fname):
		"""
			Read a single TSV file and append its data to the data pipeline.
			Set/update a class attribute FsHz with the sampling frequency in Hz.

			Args:
				fname  list of data files to read
			Returns:
				None
			Errors:
				SamplingRateChangedError if the sampling rate for any data file differs from previous
		"""
		# Add new data to the existing array
		for f in fname:
			self.currDataPipe=np.hstack((self.currDataPipe, self.__readtsv(f)))

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

			if not hasattr(self, 'FsHz'):
				self.FsHz=1000./(p2[self.timeCol]-p1[self.timeCol])
			# else check if it s the same as before
			else:
				if self.FsHz!=1000./(p2[self.timeCol]-p1[self.timeCol]):
					raise metaTrajIO.SamplingRateChangedError("The sampling rate in the data file '{0}' has changed.".format(fname))
				
			# Store the ionic currents for the first two points
			dat=[p1[self.currCol], p2[self.currCol]]

			return np.array( dat.extend([ float(row[self.currCol]) for row in r1 ]), dtype=np.float64)
