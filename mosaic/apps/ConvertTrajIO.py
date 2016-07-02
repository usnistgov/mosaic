"""
	Top level module to convert any data file readble by TrajIO objects into a comma separated value text file.

	:Created:	10/13/2014
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT	
"""
import itertools
import string

from mosaic.trajio.metaTrajIO import EmptyDataPipeError
from mosaic.utilities.resource_path import format_path
import numpy
import pandas as pd

__all__ = ["ConvertTrajIO"]

class ConvertTrajIO(object):
	"""
		Convert data from a sub-class of metaTrajIO to either a delimited text file or binary file format.

		:Parameters:
			- `trajDataObj` : a trajIO data object
			- `outdir` : the output directory. Default is *None*, which causes the output to be saved in the same directory as the input data.
			- `extension` : 'csv' for comma separated values (default), 'tsv' for tab separated values, or 'bin' for 64-bit double precision binary. 
	"""
	def __init__(self, trajDataObj, outdir=None, extension="csv"):
		self.trajDataObj=trajDataObj
		self.datPath=trajDataObj.datPath

		# If outdir is None, save the CSV files to the same directory as the data.
		if outdir==None:
			self.outDir=self.datPath
		else:
			self.outDir=outdir
		
		self.extension=extension
		
		self.filePrefix=None
		self._creategenerator()
		
		self._outputFormat={
			"csv" : ('to_csv', {'sep': ',', 'header' : False}),
			"tsv" :	('to_csv', {'sep': '\t', 'header' : False})
		}


	def Convert(self, blockSize):
		"""
			Start converting data

			:Parameters:
				- `blockSize` : number of data points to convert.
		"""
		try:
			while(True):
				

				if self.extension=="bin":
					numpy.array(self.trajDataObj.popdata(blockSize), dtype=numpy.float64).tofile(self._filename(), sep="")
				else:
					dat=pd.DataFrame(self.trajDataObj.popdata(blockSize))
					f=self._outputFormat[self.extension]

					getattr(dat, f[0])(self._filename(), index=False, **f[1])
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

		return format_path(self.outDir+'/'+next(self.fileGenerator)+'.'+self.extension)


if __name__ == '__main__':
	import mosaic.trajio.qdfTrajIO as qdfTrajIO

	for ext in ['bin','csv','tsv']:
		q=qdfTrajIO.qdfTrajIO(dirname='data', filter='*qdf', Rfb=9.1e9, Cfb=1.07e-12)
		ConvertTrajIO(
			q,
			outdir='data',
			extension=ext
		).Convert(100000)

	print numpy.fromfile('data/SingleChan-0001_1.bin')[:5]
	print numpy.hstack(numpy.fromfile('data/SingleChan-0001_1.csv', sep='\n'))[:5]
	print numpy.hstack(numpy.fromfile('data/SingleChan-0001_1.tsv', sep='\t'))[:5]
