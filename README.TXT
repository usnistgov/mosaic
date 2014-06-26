===========
pyEventAnalysis 
===========

Description::

    import sys
	import os
	import glob
	import time
	import signal
	import resource

	import pyeventanalysis.SingleChannelAnalysis

	import pyeventanalysis.eventSegment as es

	import pyeventanalysis.singleStepEvent as sse
	import pyeventanalysis.stepResponseAnalysis as sra 
	import pyeventanalysis.multiStateAnalysis as msa

	from pyeventanalysis.qdfTrajIO import *
	from pyeventanalysis.abfTrajIO import *
	from pyeventanalysis.tsvTrajIO import *
	from pyeventanalysis.binTrajIO import *

	from pyeventanalysis.besselLowpassFilter import *



	# SingleChannelAnalysis.SingleChannelAnalysis(
	# 			abfTrajIO(dirname='/Volumes/DATA/PEG1500/PEG29/',filter='*abf', nfiles=1, start=1000), 
	# 			es.eventSegment,
	# 			sra.stepResponseAnalysis
	# 		).Run()

	pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
				qdfTrajIO(dirname='/Volumes/DATA/PEG28/20140624/m70mV3/', filter='*.qdf', Rfb=2.11E+9, Cfb=1.16E-12),
				es.eventSegment,
				sra.stepResponseAnalysis
			).Run() 



Installation
=========

The code is tested under OS X and Ubuntu. Installation instructions for both platforms are below.

Dependencies
-------------
* OS X
	First install Homebrew. Next install python using brew
		brew install python

	Next install the Fortran compiler from <http://hpc.sourceforge.net/>

* Ubuntu
	Under Ubuntu in addition to gfortran, the BLAS and LAPACK libraries are required
apt-get install libblas-dev liblapack-dev gfortran libfreetype6-dev

Mathematica Scripts
-------------

To install the Mathematica analysis scripts type "make math-iface" from the root of the source directory.

Testing the Installation
-------------

Type "make tests" from the root of the source directory to test if the code was installed correctly.