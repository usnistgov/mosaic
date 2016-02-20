.. _extend-page:


Extend |projname|
=================================

|projname| was designed from the start using object oriented tools, which makes it easy to extend. :ref:`api-metaclass-page` define interfaces to five key parts of |projname|: time-series IO (:py:class:`~mosaic.metaTrajIO.metaTrajIO`), time-series filtering (:py:class:`~mosaic.metaIOFilter.metaIOFilter`), analysis output (:py:class:`~mosaic.metaMDIO.metaMDIO`), event partition and segmenting (:py:class:`~mosaic.metaEventPartition.metaEventPartition`), and event processing (:py:class:`~mosaic.metaEventProcessor.metaEventProcessor`). Sub-classing any of these meta classes and implementing their  interface functions allows one to extend |projname| while maintaining compatibility with other parts of the program. We highlight these capabilities via two examples. In the first example, we show how one can extend :py:class:`~mosaic.metaTrajIO.metaTrajIO` to read arbitrary binary files. In the second example, we implement a new top-level class that converts files to the comma separated value (CSV) format.


Read Arbitrary Binary Data Files
---------------------------------

In this first example, we implement a class that can read an arbitrary binary data file and make its data available via the interface functions in :py:class:`~mosaic.metaTrajIO.metaTrajIO`. This allows the newly implemented binary data to be used across |projname|. A complete listing of the code used in this example (:class:`~mosaic.binTrajIO.binTrajIO`) is available in the API documentation.

The new binary IO class is implemented by sub-classing :py:class:`~mosaic.metaTrajIO.metaTrajIO` as shown in the listing below. 

.. code-block:: python

	class binTrajIO(metaTrajIO.metaTrajIO):

Next, we must fully implement the :py:class:`~mosaic.metaTrajIO.metaTrajIO` interface functions (:py:meth:`~mosaic.metaTrajIO.metaTrajIO._init`, :py:meth:`~mosaic.metaTrajIO.metaTrajIO.readdata` and :py:meth:`~mosaic.metaTrajIO.metaTrajIO._formatsettings`). Note that the arguments of each function must match their corresponding base-class versions. For example the :py:meth:`~mosaic.metaTrajIO.metaTrajIO._init` function only accepts keyword arguments and is defined as shown below.

.. code-block:: python
   
   def _init(self, **kwargs):

The :py:meth:`~mosaic.metaTrajIO.metaTrajIO._init` function checks the arguments passed to *kwargs* and raises an exception if they are not defined. 

.. code-block:: python
	:emphasize-lines: 2,4 

		if not hasattr(self, 'SamplingFrequency'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the sampling rate in Hz to be defined.".format(type(self).__name__))
		if not hasattr(self, 'PythonStructCode'):
			raise metaTrajIO.InsufficientArgumentsError("{0} requires the Python struct code to be defined.".format(type(self).__name__))

Next we define the :py:meth:`~mosaic.metaTrajIO.metaTrajIO.readdata` function that reads in the data and stores the results in a numpy array. This array is then passed back to the calling function.

.. code-block:: python
   :emphasize-lines: 6

	def readdata(self, fname):

		tempdata=np.array([])
		# Read binary data and add it to the data pipe
		for f in fname:
			tempdata=np.hstack(( tempdata, self.readBinaryFile(f) ))

		return tempdata


Finally, we implement the :py:meth:`~mosaic.metaTrajIO.metaTrajIO._formatsettings` that returns a formatted string of the settings used to read in binary data.

.. code-block:: python

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


The newly defined :class:`~mosaic.binTrajIO.binTrajIO` class can then be used as shown below and in :ref:`scripting-page`. 

.. sourcecode:: python

    # Process all binary files in a directory
    mosaic.SingleChannelAnalysis.SingleChannelAnalysis(
    		"~/RefData/binSet1/",
                bin.binTrajIO,
                None, 
                es.eventSegment,
                mosaic.adept2State.adept2State
            ).Run()

Similar to other `TrajIO` objects, parameters for :class:`~mosaic.binTrajIO.binTrajIO` are obtained from the settings file when used with :class:`~mosaic.SingleChannelAnalysis.SingleChannelAnalysis`. Example settings for :class:`~mosaic.binTrajIO.binTrajIO` that read 16-bit intgers from a binary data file, assuming 50 `kHz` sampling, are shown below.

.. sourcecode:: javascript
	
	"binTrajIO" : {
		"filter"		: "*bin", 
		"AmplifierScale"	: "1.0", 
		"AmplifierOffset"	: "0.0", 
		"SamplingFrequency"	: "50000", 
		"HeaderOffset"		: "0", 
		"PythonStructCode"	: "'h'"
	}
	

Define Top-Level Functionality
---------------------------------

New functionality can be added to |projname| by combining other parts of the code. One way of accomplishing this is by defining new top-level functionality as shown in the following example. We define a new class that converts data from one of the supported data formats to comma separated text files (CSV). A complete listing of the :py:class:`~mosaic.ConvertToCSV.ConvertToCSV` class in this example is available in the API documentation.

The *__init__* function of :py:class:`~mosaic.ConvertToCSV.ConvertToCSV` class accepts two arguments: a trajIO object and the location to save the converted files. If the output directory is not specified, the data is saved in the same folder as the input data. The data conversion is performed by the :py:meth:`~mosaic.ConvertToCSV.ConvertToCSV.Convert` function, which saves the data in blocks controlled by the *blockSize* parameter. :py:meth:`~mosaic.ConvertToCSV.ConvertToCSV.Convert` saves each block to a new CSV file, named with the filename of the input data followed by an integer number (see the API documentation for :py:meth:`~mosaic.ConvertToCSV.ConvertToCSV._filename` for additional details). 

.. code-block:: python
	:emphasize-lines: 21,24

	class ConvertToCSV(object):
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
			data=numpy.array([], dtype=numpy.float64)

			try:
				while(True):
					(self.trajDataObj.popdata(blockSize)).tofile(
							self._filename(), 
							sep=','
						)
			except EmptyDataPipeError:
				pass


The :py:class:`~mosaic.ConvertToCSV.ConvertToCSV` class can now be used with any trajIO object as seen below.

.. code-block:: python
	:emphasize-lines: 2

	ConvertToCSV( abfTrajIO(dirname="~/RefData/abfSet1/", filter="*abf") ).Convert(
				blockSize=50000)

	ConvertToCSV( qdfTrajIO(dirname="~/RefData/qdfSet1/", filter="*qdf", Rfb="2.1E+9", 
				Cfb="1.16E-12") ).Convert(blockSize=50000)

	ConvertToCSV( binTrajIO(dirname="~/RefData/binSet1/", filter="*bin", AmplifierScale=1.0, 
				AmplifierOffset=0.0, SamplingFrequency=50000, HeaderOffset=0, 
				PythonStructCode='h') ).Convert(blockSize=50000)

Since :py:class:`~mosaic.ConvertToCSV.ConvertToCSV` accepts a trajIO object, we can apply a lowpass filter to the data before converting it to the CSV format. This is accomplished by passing the *datafilter* option to the trajIO object as described in the :ref:`scripting-filter-sec` section. In the example below, we convert ABF files to the CSV format after applying a lowpass Bessel filter to the data.

.. code-block:: python
	:emphasize-lines: 2

	ConvertToCSV( abfTrajIO(dirname="~/RefData/abfSet1/", filter="*abf",
			datafilter=mosaic.besselFilter
		) ).Convert(blockSize=50000)


Finally, the :py:class:`~mosaic.ConvertToCSV.ConvertToCSV` class can be further extended to output arbitrary binary files in place of CSV by the simple extension shown below.

.. only:: html

	.. gist:: https://gist.github.com/abalijepalli/975148996058ee10d4d7

.. only:: latex 

	.. sourcecode:: python

		"""
			Extend the MOSAIC ConvertToCSV class to export arbitrary binary files.
			
			:Created:	02/25/2015
		 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
			:ChangeLog:
			.. line-block::
				02/25/15	AB	Initial version
		"""
		import mosaic.ConvertToCSV as conv
		import mosaic.binTrajIO as bin
		import mosaic.settings as sett
		import numpy as np

		from mosaic.metaTrajIO import EmptyDataPipeError

		class ConvertToBin(conv.ConvertToCSV):
			def Convert(self, blockSize, binType):
				"""
					Start converting data

					:Parameters:
						- `blockSize` 	: number of data points to convert.
						- `binType` 	: Numpy binary type.
				"""
				try:
					while(True):
						np.array( self.trajDataObj.popdata(blockSize), dtype=binType ).tofile(self._filename())
				except EmptyDataPipeError:
					pass


		if __name__ == '__main__':
			s={
		        "AmplifierOffset": 0.0,
		        "SamplingFrequency": 250000,
		        "AmplifierScale": "1.0",
		        "ColumnTypes": "[('curr_pA', '>f8'), ('volts', '>f8')]",
		        "dcOffset": 0.0,
		        "filter": "*.bin",
		        "start": 0.0,
		        "HeaderOffset": 0,
		        "IonicCurrentColumn": "curr_pA"
		    }
			ConvertToBin( 
					bin.binTrajIO(dirname=".", **s ), 
					outdir="convert", 
					extension="bin" 
					).Convert(blockSize=10000000, binType='f4')
