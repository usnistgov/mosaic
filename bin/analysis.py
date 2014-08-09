import sys
import os
import glob
import time
import signal
import resource
import csv

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



pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
			qdfTrajIO(dirname='/Users/arvind/Research/Experiments/PEG29EBSRefData/20120323/singleChan',filter='*qdf', Rfb=9.1E+9, Cfb=1.07E-12), 
			es.eventSegment,
			sra.stepResponseAnalysis
		).Run()

# pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
# 			qdfTrajIO(dirname='/Volumes/DATA/PEG28/20140624/m70mV3/', filter='*.qdf', Rfb=2.11E+9, Cfb=1.16E-12),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run() 
# b=binTrajIO(fnames=['/Users/arvind/Research/Experiments/jan_doublets/AS45_2 Kopie-e239.bin'], AmplifierScale=1, AmplifierOffset=0.0, SamplingFrequency=200000, HeaderOffset=0, PythonStructCode='d')
# print b.popdata(10)
# print b.formatsettings()
# tt=pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
# 			abfTrajIO(dirname='/Users/arvind/Desktop/jan_doublets/', filter='*.abf'),
# 			es.eventSegment,
# 			msa.multiStateAnalysis
# 		)
# tt.Run(forkProcess=False)

# q=qdfTrajIO(fnames=['/Volumes/DATA/nanocluster/20140403/m120mV4/m120mV4-0205.qdf'], Rfb=2.11E+9, Cfb=1.16E-12)
# with open('/Users/arvind/Research/Publications/Journals/Neurotransmitters/Figures/m120mV4-0205.csv', 'wb') as csvfile:
#     csvwriter = csv.writer(csvfile, delimiter=',')
#     csvwriter.writerow(q.popdata(500000))