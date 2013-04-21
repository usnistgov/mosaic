import sys
import glob

import singleStepEvent as sse
import stepResponseAnalysis as sra 
from qdfTrajIO import *
from abf2TrajIO import *
from tsvTrajIO import *
from eventSegment import *



def abfrun(basedir, stlist):
	for f, st in zip([ glob.glob(basedir+'/'+d+'/*abf') for d in ['p1','p2','p3'] ], stlist):
		print "######################################\n"
		print "Start run:\n{0}, {1}".format(f,st)
	
		eventSegment(
			abf2TrajIO(fnames=f, start=st), 
			sse.singleStepEvent
		).Run()

#base='/Users/balijepalliak/Research/Experiments/PEGModelData/JoesData/'
#abfrun(base+'3.5M/m40mV', [170000,5000,180000])
#abfrun(base+'3.5M/m60mV', [650000,290000,230000])
#abfrun(base+'3.5M/m80mV', [350000,290000,1120000])

#eventSegment(
#			abf2TrajIO(fnames=[base+'4M/40mV/2012_09_13_0010.abf'], start=780000), 
#			sse.singleStepEvent
#		).Run()

#eventSegment(
#			abf2TrajIO(fnames=[base+'4M/60mV/2012_09_13_0009.abf'], start=500000), 
#			sse.singleStepEvent
#		).Run()

#eventSegment(
#			abf2TrajIO(fnames=[base+'4M/80mV/2012_09_13_0011.abf'], start=900000), 
#			sse.singleStepEvent
#		).Run()


#fnames=[baseJ+'7-6&7-2010_4M/40mV/40mV004.abf']
#baseJ='/Users/balijepalliak/Research/Experiments/PEGModelData/JuliannesData/'
baseJoe='/Users/balijepalliak/Research/Experiments/PEGModelData/JoesData/'
baseA='/Users/balijepalliak/Research/Experiments/PEGModelData/ArvindsData/'

#eventSegment(
#	qdfTrajIO(dirname=baseA+'PEGMixture/3M_20121219/m40mV12/', nfiles=110, filter='*qdf', Rfb=9.1E+9, Cfb=1.07E-12), 
#	sse.singleStepEvent
#).Run()
#eventSegment(
#	qdfTrajIO(dirname=baseA+'PEGMixture/200us rejection/3M_20130116/m40mV6/', filter='*qdf', Rfb=9.1E+9, Cfb=1.07E-12), 
#	sse.singleStepEvent
#).Run()

#eventSegment(
#			abf2TrajIO(fnames=['/Users/balijepalliak/Google Drive/13102009.abf'],start=2750000), 
#			sse.singleStepEvent
#		).Run()
#eventSegment(
#			abf2TrajIO(fnames=[baseJoe+'PEGMixture/3.44M_1413/m40mv_long/set1/2013_01_04_0002.abf'], start=70000), 
#			sse.singleStepEvent
#		).Run()
#eventSegment(
#			abf2TrajIO(fnames=[baseJoe+'PEGMixture/3.44M_1413/m40mv_long/set2/2013_01_04_0003.abf'], start=80000), 
#			sse.singleStepEvent
#		).Run()
#eventSegment(
#			abf2TrajIO(fnames=[baseJoe+'PEGMixture/3.44M_1413/m40mv_long/set3/2013_01_04_0004.abf'], start=105000), 
#			sse.singleStepEvent
#		).Run()

#eventSegment(
#			abf2TrajIO(fnames=[baseJoe+'PEGMixture/3.5M_121712/m40mV/2012_12_17_0009.abf'], start=375000), 
#			sse.singleStepEvent
#		).Run()
eventSegment(
			abf2TrajIO(fnames=[baseJoe+'PEGMixture/3.5M_121712/m40mV/2012_12_17_0009.abf'], start=375000), 
			sra.stepResponseAnalysis
		).Run()

#,
#	maxDriftRate=5.0,
#	eventPad=250,
#	minEventLength=10

#sys.stderr.write('###############################################################\n')
#sys.stderr.write('Run 2 \n')
#eventSegment(
#	tsvTrajIO(filter='*_low*txt',dirname='/Users/balijepalliak/Research/Experiments/PEG29EBSRefData/GoldHeating/Take2LongerDataPNAS/', Fs=50000), 
#	sse.singleStepEvent,
#	driftThreshold=3,
#	maxDriftRate=10.0
#).Run()

#raw_input("Press Enter to continue...")

#sys.stderr.write('###############################################################\n')
#sys.stderr.write('Run 3 \n')
#eventSegment(
#	tsvTrajIO(filter='*_high*',dirname='/Users/balijepalliak/Research/Experiments/PEG29EBSRefData/GoldHeating/Take2LongerDataPNAS/', Fs=50000), 
#	sse.singleStepEvent,
#	driftThreshold=3,
#	maxDriftRate=10.0
#).Run()
#tsvTrajIO(fnames=['/Users/balijepalliak/Research/Experiments/PEG29EBSRefData/GoldHeating/Take2LongerDataPNAS/i_low.txt'], Fs=50000), 