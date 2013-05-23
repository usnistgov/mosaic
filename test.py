import sys
import glob

import SingleChannelAnalysis

import eventSegment as es

import singleStepEvent as sse
import stepResponseAnalysis as sra 

from qdfTrajIO import *
from abf2TrajIO import *
from tsvTrajIO import *
from binTrajIO import *

import shutil


def abfrun(basedir, stlist):
	for f, st in zip([ glob.glob(basedir+'/'+d+'/*abf') for d in ['p1','p2','p3'] ], stlist):
		print "######################################\n"
		print "Start run:\n{0}, {1}".format(f,st)
	
		eventSegment(
			abf2TrajIO(fnames=f, start=st), 
			sse.singleStepEvent
		).Run()

baseJoe='/Users/balijepalliak/Research/Experiments/PEGModelData/JoesData/'
baseA='/Users/balijepalliak/Research/Experiments/PEGModelData/ArvindsData/'

# SingleChannelAnalysis.SingleChannelAnalysis(
# 			binTrajIO(fnames=['/Users/balijepalliak/Research/Experiments/StepRespData/PEG11/06o18014.abf'], AmplifierScale=400., AmplifierOffset=0, SamplingFrequency=50000, HeaderOffset=4096, RecordSize=2), 
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run()

SingleChannelAnalysis.SingleChannelAnalysis(
			binTrajIO(fnames=['/Volumes/DATA/PRL Data/PEG1000_40mV/06731014.abf','/Volumes/DATA/PRL Data/PEG1000_40mV/06731020.abf'], start=4000, AmplifierScale=400., AmplifierOffset=0, SamplingFrequency=50000, HeaderOffset=4096, RecordSize=2), 
			es.eventSegment,
			sse.singleStepEvent
		).Run()


# raw_input("Enter to continue")

# SingleChannelAnalysis.SingleChannelAnalysis(
# 			binTrajIO(fnames=['/Volumes/DATA/PRL Data/PEG1000_40mV/06731020.abf'], start=4000, AmplifierScale=400., AmplifierOffset=0, SamplingFrequency=50000, HeaderOffset=4096, RecordSize=2), 
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run()

