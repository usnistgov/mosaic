.. _details-page:

Extend |projname|
=================================


:py:meth:`~pyeventanalysis.metaTrajIO.metaTrajIO._init`
:py:meth:`~pyeventanalysis.metaTrajIO.metaTrajIO.readdata`

.. code-block:: python
   :emphasize-lines: 1,20,24

   def _init(self, **kwargs):
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

.. code-block:: python
   :emphasize-lines: 1

	def readdata(self, fname):
		{...}

		tempdata=np.array([])
		# Read binary data and add it to the data pipe
		for f in fname:
			tempdata=np.hstack(( tempdata, self.readBinaryFile(f) ))

		return tempdata

include:: ../doc/trajectoryIO.rst
include:: ../doc/dataFiltering.rst
include:: ../doc/eventPartition.rst
include:: ../doc/eventProcessing.rst
