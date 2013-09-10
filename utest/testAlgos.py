import random
import unittest
import testutil
import json
import time

import settings
import stepResponseAnalysis as sra
import singleStepEvent as sse

import eventSegment as es

from qdfTrajIO import *
from abfTrajIO import *
from tsvTrajIO import *
from binTrajIO import *


class PEGAlgorithmTest(unittest.TestCase):

	def setUp(self):
		self.datapath = 'testdata'

	def runTestCase(self, datfile, prmfile, algoHnd):
		dat=testutil.readcsv(datfile)
		prm=testutil.readparams(prmfile)

		sett=json.loads( "".join((open('../.settings', 'r').readlines())) )[algoHnd.__name__]

		dt=int(1e6/dat[0])

		testobj=algoHnd(
							dat[1], 
							dat[0],
							eventstart=int(prm['tau1']/dt),			# event start point
							eventend=int(prm['tau2']/dt),    		# event end point
							baselinestats=[ 1.0, 0.01, 0.0 ],
							algosettingsdict=sett,
							savets=0
						)
		testobj.processEvent()

		self.assertEqual( testobj.mdProcessingStatus, 'normal' )
		self.assertEqual( round(testobj.mdBlockDepth,1), 1.0-abs(prm['a']) )
		self.assertEqual( round(testobj.mdResTime,1), (prm['tau2']-prm['tau1'])/1000. )

class PEGEventPartitionTest(unittest.TestCase):

	def setUp(self):
		self.datapath = 'testdata'

	def runTestCase(self, datfile, prmfile, eventPartHnd, parallel):
		prm=testutil.readparams(prmfile)
		dat=tsvTrajIO(fnames=[datfile], Fs=prm['Fs'], separator=',')

		sett=json.loads( "".join((open('../.settings', 'r').readlines())) )

		epartsettings = sett[eventPartHnd.__name__]

		epartsettings['blockSizeSec'] = 0.006
		epartsettings['meanOpenCurr'] = 1
		epartsettings['sdOpenCurr'] = 0.03 
		epartsettings['slopeOpenCurr'] = 0
		epartsettings['driftThreshold'] = 1000
		epartsettings['maxDriftRate'] = 9999.0
		epartsettings['eventThreshold'] = 5.0

		if parallel:
			epartsettings['parallelProc'] = 1

		testobj=eventPartHnd(
							dat, 
							sra.stepResponseAnalysis, 
							epartsettings,
							sett["stepResponseAnalysis"]
						)
		testobj.PartitionEvents()

		self.assertEqual( testobj.eventcount, prm['nevents'] )

		testobj.Stop()

class PEGSegmentTests(PEGEventPartitionTest):
	def test_e1seg(self):
		self.runTestCase('testdata/testEventPartition1.csv', 'testdata/testEventPartition1.prm', es.eventSegment, False)

	def test_e2seg(self):
		self.runTestCase('testdata/testEventPartition2.csv', 'testdata/testEventPartition2.prm', es.eventSegment, False)

	def test_e3seg(self):
		self.runTestCase('testdata/testEventPartition3.csv', 'testdata/testEventPartition3.prm', es.eventSegment, False)

	def test_e4seg(self):
		self.runTestCase('testdata/testEventPartition4.csv', 'testdata/testEventPartition4.prm', es.eventSegment, False)

	def test_e5seg(self):
		self.runTestCase('testdata/testEventPartition5.csv', 'testdata/testEventPartition5.prm', es.eventSegment, False)

	def test_e1segP(self):
		self.runTestCase('testdata/testEventPartition1.csv', 'testdata/testEventPartition1.prm', es.eventSegment, True)

	def test_e2segP(self):
		self.runTestCase('testdata/testEventPartition2.csv', 'testdata/testEventPartition2.prm', es.eventSegment, True)

	def test_e3segP(self):
		self.runTestCase('testdata/testEventPartition3.csv', 'testdata/testEventPartition3.prm', es.eventSegment, True)

	def test_e4segP(self):
		self.runTestCase('testdata/testEventPartition4.csv', 'testdata/testEventPartition4.prm', es.eventSegment, True)

	def test_e5segP(self):
		self.runTestCase('testdata/testEventPartition5.csv', 'testdata/testEventPartition5.prm', es.eventSegment, True)

class PEGSRATests(PEGAlgorithmTest):
	def test_e1sra(self):
		self.runTestCase('testdata/test1.csv', 'testdata/test1.prm', sra.stepResponseAnalysis)

	def test_e2sra(self):
		self.runTestCase('testdata/test2.csv', 'testdata/test2.prm', sra.stepResponseAnalysis)

	def test_e3sra(self):
		self.runTestCase('testdata/test3.csv', 'testdata/test3.prm', sra.stepResponseAnalysis)

	def test_e4sra(self):
		self.runTestCase('testdata/test4.csv', 'testdata/test4.prm', sra.stepResponseAnalysis)

	def test_e5sra(self):
		self.runTestCase('testdata/test5.csv', 'testdata/test5.prm', sra.stepResponseAnalysis)

	def test_e6sra(self):
		self.runTestCase('testdata/test6.csv', 'testdata/test6.prm', sra.stepResponseAnalysis)

	def test_e7sra(self):
		self.runTestCase('testdata/test7.csv', 'testdata/test7.prm', sra.stepResponseAnalysis)

	def test_e8sra(self):
		self.runTestCase('testdata/test8.csv', 'testdata/test8.prm', sra.stepResponseAnalysis)

	def test_e9sra(self):
		self.runTestCase('testdata/test9.csv', 'testdata/test9.prm', sra.stepResponseAnalysis)

	def test_e10sra(self):
		self.runTestCase('testdata/test10.csv', 'testdata/test10.prm', sra.stepResponseAnalysis)

	def test_e11sra(self):
		self.runTestCase('testdata/test11.csv', 'testdata/test11.prm', sra.stepResponseAnalysis)

	def test_e12sra(self):
		self.runTestCase('testdata/test12.csv', 'testdata/test12.prm', sra.stepResponseAnalysis)

	def test_e13sra(self):
		self.runTestCase('testdata/test13.csv', 'testdata/test13.prm', sra.stepResponseAnalysis)
	
	def test_e14sra(self):
		self.runTestCase('testdata/test14.csv', 'testdata/test14.prm', sra.stepResponseAnalysis)

	def test_e15sra(self):
		self.runTestCase('testdata/test15.csv', 'testdata/test15.prm', sra.stepResponseAnalysis)

	def test_e16sra(self):
		self.runTestCase('testdata/test16.csv', 'testdata/test16.prm', sra.stepResponseAnalysis)

	def test_e17sra(self):
		self.runTestCase('testdata/test17.csv', 'testdata/test17.prm', sra.stepResponseAnalysis)

	def test_e18sra(self):
		self.runTestCase('testdata/test18.csv', 'testdata/test18.prm', sra.stepResponseAnalysis)

	def test_e19sra(self):
		self.runTestCase('testdata/test19.csv', 'testdata/test19.prm', sra.stepResponseAnalysis)

	def test_e20sra(self):
		self.runTestCase('testdata/test20.csv', 'testdata/test20.prm', sra.stepResponseAnalysis)

	def test_e21sra(self):
		self.runTestCase('testdata/test21.csv', 'testdata/test21.prm', sra.stepResponseAnalysis)

	def test_e22sra(self):
		self.runTestCase('testdata/test22.csv', 'testdata/test22.prm', sra.stepResponseAnalysis)

	def test_e23sra(self):
		self.runTestCase('testdata/test23.csv', 'testdata/test23.prm', sra.stepResponseAnalysis)

	def test_e24sra(self):
		self.runTestCase('testdata/test24.csv', 'testdata/test24.prm', sra.stepResponseAnalysis)

# class PEGSSETests(PEGAlgorithmTest):
# 	def test_e1sse(self):
# 		self.runTestCase('testdata/test1.csv', 'testdata/test1.prm', sse.singleStepEvent)

# 	def test_e2sse(self):
# 		self.runTestCase('testdata/test2.csv', 'testdata/test2.prm', sse.singleStepEvent)

# 	def test_e3sse(self):
# 		self.runTestCase('testdata/test3.csv', 'testdata/test3.prm', sse.singleStepEvent)

# 	def test_e4sse(self):
# 		self.runTestCase('testdata/test4.csv', 'testdata/test4.prm', sse.singleStepEvent)

# 	def test_e5sse(self):
# 		self.runTestCase('testdata/test5.csv', 'testdata/test5.prm', sse.singleStepEvent)

# 	def test_e6sse(self):
# 		self.runTestCase('testdata/test6.csv', 'testdata/test6.prm', sse.singleStepEvent)

# 	def test_e7sse(self):
# 		self.runTestCase('testdata/test7.csv', 'testdata/test7.prm', sse.singleStepEvent)

# 	def test_e8sse(self):
# 		self.runTestCase('testdata/test8.csv', 'testdata/test8.prm', sse.singleStepEvent)

# 	def test_e9sse(self):
# 		self.runTestCase('testdata/test9.csv', 'testdata/test9.prm', sse.singleStepEvent)

# 	def test_e10sse(self):
# 		self.runTestCase('testdata/test10.csv', 'testdata/test10.prm', sse.singleStepEvent)

# 	def test_e11sse(self):
# 		self.runTestCase('testdata/test11.csv', 'testdata/test11.prm', sse.singleStepEvent)

# 	def test_e12sse(self):
# 		self.runTestCase('testdata/test12.csv', 'testdata/test12.prm', sse.singleStepEvent)

# 	def test_e13sse(self):
# 		self.runTestCase('testdata/test13.csv', 'testdata/test13.prm', sse.singleStepEvent)

# 	def test_e14sse(self):
# 		self.runTestCase('testdata/test14.csv', 'testdata/test14.prm', sse.singleStepEvent)

# 	def test_e15sse(self):
# 		self.runTestCase('testdata/test15.csv', 'testdata/test15.prm', sse.singleStepEvent)

# 	def test_e16sse(self):
# 		self.runTestCase('testdata/test16.csv', 'testdata/test16.prm', sse.singleStepEvent)
