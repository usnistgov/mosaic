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
