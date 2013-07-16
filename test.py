import sys
import os
import glob
import resource

import SingleChannelAnalysis

import eventSegment as es

import singleStepEvent as sse
import stepResponseAnalysis as sra 

from qdfTrajIO import *
from abfTrajIO import *
from tsvTrajIO import *
from binTrajIO import *

from besselLowpassFilter import *


# resource.setrlimit(resource.RLIMIT_AS, (0.6*(2**30), 0.7*(2**30)))
# print resource.getrlimit(resource.RLIMIT_AS)


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
# 			abfTrajIO(fnames=['/Volumes/DATA/tetheredPEG/13712018_peg2k.abf']), 
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run()

#'set3','set4','set5',
# [ SingleChannelAnalysis.SingleChannelAnalysis(
# 			qdfTrajIO(dirname='/Volumes/DATA/PRL Data/EBSPEG600/20130627/m40mV/'+d, filter='*qdf', Rfb=9.1E+9, Cfb=1.07E-12, datafilter=besselLowpassFilter),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run() for d in ['set7','set8'] ]




# datafilter=besselLowpassFilter
def analysisiter(dir, filt, i):
	try:
		print filt 

		SingleChannelAnalysis.SingleChannelAnalysis(
				qdfTrajIO(dirname=dir, filter=filt, Rfb=9.1E+9, Cfb=1.07E-12),
				es.eventSegment,
				sra.stepResponseAnalysis
			).Run() 

		os.rename(dir+'/eventMD.tsv', dir+'/eventMD_'+str(i).zfill(2)+'.tsv')
		#os.rename(dir+'/eventTS.csv', dir+'/eventTS_'+str(i).zfill(2)+'.csv')
		os.rename(dir+'/eventProcessing.log', dir+'/eventProcessing'+str(i).zfill(2)+'.log')
	except MemoryError, e:
		print "memory exceeded: ", e
		pass



#[ analysisiter('/Volumes/DATA/PRL Data/EBSPEG600/20130627/m40mV2/', '*-'+str(i).zfill(2)+'??.qdf', i)	for i in range(10, 11) ]

SingleChannelAnalysis.SingleChannelAnalysis(
			qdfTrajIO(dirname='/Volumes/DATA/PRL Data/EBSPEG600/20130715/m40mV/', filter='*qdf', nfiles=150, Rfb=9.1E+9, Cfb=1.07E-12),
			es.eventSegment,
			sra.stepResponseAnalysis
		).Run() 

# print ['*-'+str(i).zfill(2)+'??.qdf' for i in range(1,15)]

# SingleChannelAnalysis.SingleChannelAnalysis(
# 			tsvTrajIO(fnames=['/Users/balijepalliak/Research/Experiments/StepRespData/KenDenoiseData/original_snippet.csv'], Fs=50000, separator=','), 
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run()

