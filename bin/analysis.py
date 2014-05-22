import sys
import os
import glob
import time
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

# for dir in ['m120mV', 'm120mV1','m120mV2','m120mV3','m120mV3a','m120mV3b', 'm120mV4', 'm120mV5', 'm120mV6', 'm120mV7','m120mV8', 'm120mV11']:
#         SingleChannelAnalysis.SingleChannelAnalysis(
#                         qdfTrajIO(dirname='/Volumes/DATA/nanocluster/20140320/'+dir+'/' ,filter='*.qdf', nfiles=10, Rfb=2.11E+9, Cfb=1.16E-12),
#                         es.eventSegment,
#                         sra.stepResponseAnalysis
#                 ).Run()


# SingleChannelAnalysis.SingleChannelAnalysis(
# 			qdfTrajIO(dirname='/Users/arvind/Desktop/POM_nobuffer_PH7_m120/',nfiles=20, filter='*.qdf', Rfb=2.126E+9, Cfb=1.13E-12),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run() 

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
pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
			qdfTrajIO(dirname='/Users/arvind/Research/Experiments/PEG29EBSRefData/20120323/singleChan/' ,filter='*.qdf', nfiles=50, Rfb=9.1E+9, Cfb=1.07E-12),
			es.eventSegment,
			sra.stepResponseAnalysis
		).Run() 

# pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis(
# 			qdfTrajIO(dirname='/Volumes/DATA/polypeptide standard/20140521/p120mV2/' ,filter='*.qdf', nfiles=400, Rfb=2.11E+9, Cfb=1.16E-12),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run() 



# SingleChannelAnalysis.SingleChannelAnalysis(
# 			abfTrajIO(fnames=['/Users/arvind/Desktop/JoeProtein/2010_09_24_0009_001.abf','/Users/arvind/Desktop/JoeProtein/2010_09_24_0009_002.abf','/Users/arvind/Desktop/JoeProtein/2010_09_24_0009_003.abf'],start=319300),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run() 

# SingleChannelAnalysis.SingleChannelAnalysis(
# 			qdfTrajIO(dirname='/Volumes/DATA/nanocluster/PW12O40-Dopamine/20140311/m80mV6/', filter='*.qdf', nfiles=300, format='pA', Rfb=2.11E+9, Cfb=1.16E-12),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run() 
# SingleChannelAnalysis.SingleChannelAnalysis(
# 			qdfTrajIO(dirname='/Volumes/DATA/PEGCaptureRate/PEG12/20140214/m80mV5/' ,filter='*.qdf', Rfb=2.11E+9, Cfb=1.16E-12),
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run() 
# print ['*-'+str(i).zfill(2)+'??.qdf' for i in range(1,15)]

# SingleChannelAnalysis.SingleChannelAnalysis(
# 			tsvTrajIO(fnames=['/Users/balijepalliak/Research/Experiments/StepRespData/KenDenoiseData/original_snippet.csv'], Fs=50000, separator=','), 
# 			es.eventSegment,
# 			sra.stepResponseAnalysis
# 		).Run()

