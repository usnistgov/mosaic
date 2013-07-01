import sys
import glob

import SingleChannelAnalysis

import eventSegment as es

import singleStepEvent as sse
import stepResponseAnalysis as sra 

from qdfTrajIO import *
from abfTrajIO import *
from tsvTrajIO import *
from binTrajIO import *

# SingleChannelAnalysis.SingleChannelAnalysis(
# 			abfTrajIO(dirname='/Volumes/DATA/PEG1500/PEG29/',filter='*abf', nfiles=1, start=1000), 
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run()


# SingleChannelAnalysis.SingleChannelAnalysis(
# 			binTrajIO(fnames=['/Volumes/DATA/PRL Data/PEG1000_40mV/06731014.abf','/Volumes/DATA/PRL Data/PEG1000_40mV/06731020.abf'], start=4000, AmplifierScale=400., AmplifierOffset=0, SamplingFrequency=50000, HeaderOffset=4096, RecordSize=2), 
# 			es.eventSegment,
# 			sse.singleStepEvent
# 		).Run()


# raw_input("Enter to continue")

# SingleChannelAnalysis.SingleChannelAnalysis(
# 			abfTrajIO(fnames=['/Volumes/DATA/PRL Data/Jessica_PEG600/06252013/13625004.abf'], start=600000), 
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run()

SingleChannelAnalysis.SingleChannelAnalysis(
			tsvTrajIO(fnames=['/Users/balijepalliak/Research/Experiments/StepRespData/KenDenoiseData/original_snippet.csv'], Fs=50000, separator=','), 
			es.eventSegment,
			sra.stepResponseAnalysis
		).Run()

