#
#	Top level module to convert any data file readble by TrajIO objects into a comma separated value text file.
#
#	:Author: 	Arvind Balijepalli
#	:Created:	10/13/2014
#
__docformat__ = 'restructuredtext'

import itertools
import string

from mosaic.metaTrajIO import EmptyDataPipeError
import numpy

class ConvertToCSV(object):
	"""
		Convert data read from a sub-class of metaTrajIO to a comma separated text file

		:Parameters:
			- `trajDataObj` : a trajIO data object
			- `outdir` : the output directory. Default is *None*, which causes the output to be saved in the same directory as the input data.
	"""
	def __init__(self, trajDataObj, outdir=None):
		self.trajDataObj=trajDataObj
		self.datPath=trajDataObj.datPath

		# If outdir is None, save the CSV files to the same directory as the data.
		if outdir==None:
			self.outDir=self.datPath
		else:
			self.outDir=outdir
		
		self.filePrefix=None
		self._creategenerator()

	def Convert(self, blockSize):
		"""
			Start converting data

			:Parameters:
				- `blockSize` : number of data points to convert.
		"""
		try:
			while(True):
				(self.trajDataObj.popdata(blockSize)).tofile(self._filename(), sep=',')
		except EmptyDataPipeError:
			pass

	def _creategenerator(self):
		"""
			Create a new filename generator if the file prefix has changed. 
			The generator returns a filename incremented by a counter each time 
			its next() function is called.
		"""
		f=self._fileprefix()
		if f != self.filePrefix:
			self.filePrefix=f

			self.fileGenerator=itertools.imap( 
							lambda n : self.filePrefix+"_"+str(n), 
							itertools.count(1)
						)

	def _fileprefix(self):
		return string.split(string.split(self.trajDataObj.LastFileProcessed,'/')[-1],'.')[0]

	def _filename(self):
		"""
			Return a output filename that contains the data file prefix and and the block index.
		"""
		self._creategenerator()

		return self.outDir+'/'+next(self.fileGenerator)+'.csv'

		