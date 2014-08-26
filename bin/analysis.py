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



q=pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
			qdfTrajIO(dirname='/Users/arvind/Research/Experiments/PEG29EBSRefData/20120323/singleChan',filter='*qdf', Rfb=9.1E+9, Cfb=1.07E-12), 
			es.eventSegment,
			sra.stepResponseAnalysis
		)
q.Run(forkProcess=True)
q.subProc.join()


# pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
# 			tsvTrajIO(dirname='/Users/arvind/Research/Experiments/AnalysisTools/Wavelet Denoising/raw data', filter='*.tsv', Fs=500000, headers=False),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
#  		).Run() 
# pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
# 			tsvTrajIO(dirname='/Users/arvind/Research/Experiments/AnalysisTools/Wavelet Denoising/Haar 5 Levels Hard Default Threshold', filter='*.csv', Fs=500000, headers=False),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
#  		).Run() 
# pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
# 			tsvTrajIO(dirname='/Users/arvind/Research/Experiments/AnalysisTools/Wavelet Denoising/Haar 5 Levels Soft Penalize High Threshold', filter='*.csv', Fs=500000, headers=False),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
#  		).Run() 
# pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
# 			tsvTrajIO(dirname='/Users/arvind/Research/Experiments/AnalysisTools/Wavelet Denoising/Haar 5 Levels Soft Default Threshold', filter='*.csv', Fs=500000, headers=False),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
#  		).Run() 
# pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
# 			tsvTrajIO(dirname='/Users/arvind/Research/Experiments/AnalysisTools/Wavelet Denoising/Haar 5 Levels Soft Heuristic Band Threshold', filter='*.csv', Fs=500000, headers=False),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
#  		).Run() 


# b=binTrajIO(fnames=['/Users/arvind/Research/Experiments/jan_doublets/AS45_2 Kopie-e239.bin'], AmplifierScale=1, AmplifierOffset=0.0, SamplingFrequency=200000, HeaderOffset=0, PythonStructCode='d')
# print b.popdata(10)
# print b.formatsettings()
# '/Users/arvind/Research/Experiments/jan_doublets/'
# tt=pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
# 			qdfTrajIO(dirname='/Users/arvind/Research/Experiments/SBSTagsColumbia/dA6TP30odd/p100mV3/', filter='*.qdf', Rfb=9.1E+9, Cfb=1.07E-12),
# 			es.eventSegment,
# 			msa.multiStateAnalysis
# 		)
# tt.Run(forkProcess=False)

# q=qdfTrajIO(fnames=['/Volumes/DATA/nanocluster/PW9O34-Serotonin/20140430/m120mV3/m120mV3-0205.qdf'], Rfb=2.11E+9, Cfb=1.16E-12)
# with open('/Users/arvind/Desktop/m120mV3-0205.csv', 'wb') as csvfile:
#     csvwriter = csv.writer(csvfile, delimiter=',')
#     csvwriter.writerow(q.popdata(500000))


