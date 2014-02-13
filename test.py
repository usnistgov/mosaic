import sys
import os
import glob
import resource

import SingleChannelAnalysis

import eventSegment as es

import singleStepEvent as sse
import stepResponseAnalysis as sra 
import multiStateAnalysis as msa

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
# dirname='/Volumes/DATA/tetheredPEG/20130716/',filter='*abf'
# SingleChannelAnalysis.SingleChannelAnalysis(
#  			abfTrajIO(dirname='/Users/balijepalliak/Desktop/peg2k/selected m60', filter='*abf'),
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
		os.rename(dir+'/eventTS.csv', dir+'/eventTS_'+str(i).zfill(2)+'.csv')
		os.rename(dir+'/eventProcessing.log', dir+'/eventProcessing'+str(i).zfill(2)+'.log')
	except MemoryError, e:
		print "memory exceeded: ", e
		pass



#[ analysisiter('/Volumes/DATA/PRL Data/EBSPEG600/20130722/m40mV8/', '*-'+str(i).zfill(2)+'??.qdf', i)	for i in range(100, 101) ]
# [ analysisiter('/Volumes/DATA/PRL Data/EBSPEG600/20130723/m40mV2/', '*-'+str(i).zfill(2)+'??.qdf', i)	for i in range(10, 11) ]

# qdfTrajIO(dirname='/Volumes/DATA/PRL Data/EBSPEG600/20130717/m40mV2/', filter='*qdf', nfiles=325, Rfb=9.1E+9, Cfb=1.07E-12),
# , datafilter=besselLowpassFilter
# SingleChannelAnalysis.SingleChannelAnalysis(
# 			qdfTrajIO(dirname='/Volumes/DATA/SBSTags/d6TPCy3T25/20130930/p80mV6',filter='*.qdf', nfiles=10, Rfb=9.1E+9, Cfb=1.07E-12),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run() 

# /Volumes/DATA/JacobPEG29/m40mV_2
#/Volumes/DATA/SBSTags/d6TPCy3T25/20130930/p120mV6

# '/Volumes/DATA/SBSTags/dA6TP30odd/20130925/p120mV'
SingleChannelAnalysis.SingleChannelAnalysis(
			qdfTrajIO(dirname='/Volumes/DATA/PolysialicAcid_KR/20140212/p100mV7/' ,filter='*.qdf', Rfb=2.11E+9, Cfb=1.16E-12, format='V'),
			es.eventSegment,
			sra.stepResponseAnalysis
		).Run() 
# print ['*-'+str(i).zfill(2)+'??.qdf' for i in range(1,15)]

# SingleChannelAnalysis.SingleChannelAnalysis(
# 			tsvTrajIO(fnames=['/Users/balijepalliak/Research/Experiments/StepRespData/KenDenoiseData/original_snippet.csv'], Fs=50000, separator=','), 
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run()

