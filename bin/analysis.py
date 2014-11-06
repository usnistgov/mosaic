import sys
import os
import glob
import time
import signal
import resource
import csv

import mosaic.SingleChannelAnalysis

import mosaic.eventSegment as es

import mosaic.singleStepEvent as sse
import mosaic.stepResponseAnalysis as sra 
import mosaic.multiStateAnalysis as msa

from mosaic.qdfTrajIO import *
from mosaic.abfTrajIO import *
from mosaic.tsvTrajIO import *
from mosaic.binTrajIO import *

from mosaic.besselLowpassFilter import *
from mosaic.waveletDenoiseFilter import *

# '/Users/arvind/Research/Experiments/PEG29EBSRefData/20120323/singleChan' Rfb=9.1E+9, Cfb=1.07E-12, datafilter=waveletDenoiseFilter
# qdfTrajIO(dirname='/Users/arvind/Research/Experiments/AnalysisTools/ReferenceData/POM ph5.45 m120_6',filter='*qdf', start=5, nfiles=10, Rfb=2.126E+9, Cfb=1.13E-12), 
mosaic.SingleChannelAnalysis.SingleChannelAnalysis(
			'/Users/arvind/Research/Experiments/AnalysisTools/ReferenceData/POM ph5.45 m120_6',
			qdfTrajIO, 
			None,
			es.eventSegment,
			sra.stepResponseAnalysis
		).Run()

# mosaic.SingleChannelAnalysis.SingleChannelAnalysis(
#			'/Users/arvind/Research/Experiments/AnalysisTools/Wavelet Denoising/raw data',
# 			tsvTrajIO,
#			None,
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
#  		).Run() 


# b=binTrajIO(fnames=['/Users/arvind/Research/Experiments/jan_doublets/AS45_2 Kopie-e239.bin'], AmplifierScale=1, AmplifierOffset=0.0, SamplingFrequency=200000, HeaderOffset=0, PythonStructCode='d')
# print b.popdata(10)
# print b.formatsettings()
# '/Users/arvind/Research/Experiments/jan_doublets/'
# tt=mosaic.SingleChannelAnalysis.SingleChannelAnalysis(
# 			qdfTrajIO(dirname='/Users/arvind/Research/Experiments/SBSTagsColumbia/dA6TP30odd/p100mV3/', filter='*.qdf', Rfb=9.1E+9, Cfb=1.07E-12),
# 			es.eventSegment,
# 			msa.multiStateAnalysis
# 		)
# tt.Run(forkProcess=False)

# q=qdfTrajIO(fnames=['/Users/arvind/Desktop/m120mV/m120mV-0001.qdf'], Rfb=2.11E+9, Cfb=1.16E-12)
# with open('/Users/arvind/Desktop/m120mV/m120mV-0001.csv', 'wb') as csvfile:
#     csvwriter = csv.writer(csvfile, delimiter=',')
#     csvwriter.writerow(q.popdata(500000))


