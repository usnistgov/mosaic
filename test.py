import sys
import singleStepEvent as sse
from qdfTrajIO import *
from abf2TrajIO import *
from tsvTrajIO import *
from eventSegment import *


fn=['/Users/balijepalliak/Research/Experiments/PEGModelData/JoesData/2012_09_10_0016.abf']

eventSegment(
	abf2TrajIO(fnames=fn, start=175000), 
	sse.singleStepEvent
).Run()



#dat='/Users/balijepalliak/Research/Experiments/PEG29EBSRefData/GoldHeating/SteadyStateHeating/20120725/21Cr1M40mV/'

#sys.stderr.write('###############################################################\n')
#sys.stderr.write('Run 1 \n')
#eventSegment(
#	qdfTrajIO(dirname=dat, filter='*qdf', Rfb=9.1E+9, Cfb=1.07E-12), 
#	sse.singleStepEvent
#).Run()

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