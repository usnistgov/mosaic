import random
import unittest
import testutil
import json
import time
import os
import glob

import mosaic.settings as settings
import mosaic.singleStepEvent as sse
import mosaic.adept2State as a2s 
import mosaic.adept as adept
import mosaic.cusumPlus as cpl

import mosaic.eventSegment as es

from mosaic.qdfTrajIO import *
from mosaic.abfTrajIO import *
from mosaic.tsvTrajIO import *
from mosaic.binTrajIO import *

class ProcessingAlgorithmsCommon(unittest.TestCase):

	def setUp(self):
		self.datapath = 'testdata'

	def runTestCase(self, datfile, prmfile, algoHnd):
		self.testobj=algoHnd(
							self.dat, 
							self.Fs,
							eventstart=int(self.prm['tau1']/self.dt),			# event start point
							eventend=int(self.prm['tau2']/self.dt),    		# event end point
							baselinestats=[ 1.0, 0.01, 0.0 ],
							algosettingsdict=self.sett,
							savets=0,
							absdatidx=0.0,
							datafileHnd=None
						)
		self.testobj.processEvent()


class Base2StateTest(ProcessingAlgorithmsCommon):
	def _setupTestCase(self, datfile, prmfile, algoHnd):
		[self.Fs, self.dat]=testutil.readcsv(datfile)
		self.prm=testutil.readparams(prmfile)

		self.sett = (settings.settings('.', defaultwarn=False).settingsDict)[algoHnd.__name__]

		self.dt=int(1e6/self.dat[0])

	def runTestCase(self, datfile, prmfile, algoHnd):
		self._setupTestCase(datfile, prmfile,algoHnd)

		super(Base2StateTest, self).runTestCase(datfile, prmfile, algoHnd)

		self.assertEqual( self.testobj.mdProcessingStatus, 'normal' )
		self.assertEqual( round(self.testobj.mdBlockDepth,1), 1.0-abs(self.prm['a']) )
		self.assertEqual( round(self.testobj.mdResTime,1), (self.prm['tau2']-self.prm['tau1'])/1000. )

class SSETest(ProcessingAlgorithmsCommon):
	def _setupTestCase(self, datfile, prmfile, algoHnd):
		[self.Fs, self.dat]=testutil.readcsv(datfile)
		self.prm=testutil.readparams(prmfile)

		self.sett = (settings.settings('.', defaultwarn=False).settingsDict)[algoHnd.__name__]

		self.dt=int(1e6/self.dat[0])
		
	def runTestCase(self, datfile, prmfile, algoHnd):
		self._setupTestCase(datfile, prmfile,algoHnd)

		super(SSETest, self).runTestCase(datfile, prmfile, algoHnd)

		self.assertEqual( self.testobj.mdProcessingStatus, 'eShortEvent' )
		# self.assertEqual( round(self.testobj.mdBlockDepth,1), 1.0-abs(self.prm['a']) )
		# self.assertEqual( round(self.testobj.mdResTime,1), (self.prm['tau2']-self.prm['tau1'])/1000. )

class BaseMultiStateTest(ProcessingAlgorithmsCommon):
	def _setupTestCase(self, datfile, prmfile, algoHnd):
		self.dat=testutil.readDataRAW(datfile)
		self.prm=testutil.readParametersJSON(prmfile)
		self.Fs=int(self.prm['FsKHz']*1000)

		self.dt=1./self.prm['FsKHz']

		self.noiseRMS=self.prm['noisefArtHz']*np.sqrt(self.prm['BkHz']*1000.)/1000.
				
		self.sett = (settings.settings('.', defaultwarn=False).settingsDict)[algoHnd.__name__]
	
	def runTestCase(self, datfile, prmfile, algoHnd):
		self._setupTestCase(datfile, prmfile,algoHnd)
			
		testobj=algoHnd(
					self.dat, 
					self.Fs,
					eventstart=int(self.prm['eventDelay'][0]/self.dt),			# event start point
					eventend=int(self.prm['eventDelay'][-1]/self.dt),    		# event end point
					baselinestats=[ self.prm['OpenChCurrent'], self.noiseRMS, 0.0 ],
					algosettingsdict=self.sett,
					savets=0,
					absdatidx=0.0,
					datafileHnd=None
				)
		testobj.processEvent()

		self.assertEqual( testobj.mdProcessingStatus, 'normal' )
		# self.assertEqual( round(self.testobj.mdBlockDepth,1), 1.0-abs(self.prm['a']) )
		# self.assertEqual( round(self.testobj.mdResTime,1), round((self.prm['tau2']-self.prm['tau1'])/1000.,1) )


class PEGEventPartitionTest(unittest.TestCase):

	def setUp(self):
		self.datapath = 'testdata'

	def runTestCase(self, datfile, prmfile, eventPartHnd, parallel):
		prm=testutil.readparams(prmfile)
		dat=tsvTrajIO(fnames=[datfile], Fs=prm['Fs'], separator=',')

		# sett=json.loads( "".join((open('../../.settings', 'r').readlines())) )
		sett = (settings.settings('.', defaultwarn=False).settingsDict)

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
							a2s.adept2State, 
							epartsettings,
							sett["adept2State"],
							json.dumps(sett, indent=4)
						)
		testobj.PartitionEvents()

		self.assertEqual( testobj.eventcount, prm['nevents'] )

		testobj.Stop()

		for f in glob.glob('testdata/*.sqlite'):
			os.remove(f)

class EventPartitionTestSuite(PEGEventPartitionTest):
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

class ADEPT_TestSuite(BaseMultiStateTest):
	def test_e1adept(self):
		self.runTestCase('testdata/eventLong_0_raw.bin', 'testdata/eventLong_0_params.json', adept.adept)

	def test_e2adept(self):
		self.runTestCase('testdata/eventLong_2_raw.bin', 'testdata/eventLong_2_params.json', adept.adept)

	def test_e3adept(self):
		self.runTestCase('testdata/eventLong_3_raw.bin', 'testdata/eventLong_3_params.json', adept.adept)

	def test_e4adept(self):
		self.runTestCase('testdata/eventLong_4_raw.bin', 'testdata/eventLong_4_params.json', adept.adept)

	def test_e5adept(self):
		self.runTestCase('testdata/eventLong_5_raw.bin', 'testdata/eventLong_5_params.json', adept.adept)

	def test_e6adept(self):
		self.runTestCase('testdata/eventLong_6_raw.bin', 'testdata/eventLong_6_params.json', adept.adept)

	def test_e7adept(self):
		self.runTestCase('testdata/eventLong_7_raw.bin', 'testdata/eventLong_7_params.json', adept.adept)

	def test_e8adept(self):
		self.runTestCase('testdata/eventLong_8_raw.bin', 'testdata/eventLong_8_params.json', adept.adept)

	def test_e9adept(self):
		self.runTestCase('testdata/eventLong_10_raw.bin', 'testdata/eventLong_10_params.json', adept.adept)

	def test_e10adept(self):
		self.runTestCase('testdata/eventLong_11_raw.bin', 'testdata/eventLong_11_params.json', adept.adept)

class CUSUMPlus_TestSuite(BaseMultiStateTest):
	def test_e1cpl(self):
		self.runTestCase('testdata/eventLong_0_raw.bin', 'testdata/eventLong_0_params.json', cpl.cusumPlus)

	def test_e2cpl(self):
		self.runTestCase('testdata/eventLong_2_raw.bin', 'testdata/eventLong_2_params.json', cpl.cusumPlus)

	def test_e3cpl(self):
		self.runTestCase('testdata/eventLong_3_raw.bin', 'testdata/eventLong_3_params.json', cpl.cusumPlus)

	def test_e4cpl(self):
		self.runTestCase('testdata/eventLong_4_raw.bin', 'testdata/eventLong_4_params.json', cpl.cusumPlus)

	def test_e5cpl(self):
		self.runTestCase('testdata/eventLong_5_raw.bin', 'testdata/eventLong_5_params.json', cpl.cusumPlus)

	def test_e6cpl(self):
		self.runTestCase('testdata/eventLong_6_raw.bin', 'testdata/eventLong_6_params.json', cpl.cusumPlus)

	def test_e7cpl(self):
		self.runTestCase('testdata/eventLong_7_raw.bin', 'testdata/eventLong_7_params.json', cpl.cusumPlus)

	def test_e8cpl(self):
		self.runTestCase('testdata/eventLong_8_raw.bin', 'testdata/eventLong_8_params.json', cpl.cusumPlus)

	def test_e9cpl(self):
		self.runTestCase('testdata/eventLong_10_raw.bin', 'testdata/eventLong_10_params.json', cpl.cusumPlus)

	def test_e10cpl(self):
		self.runTestCase('testdata/eventLong_11_raw.bin', 'testdata/eventLong_11_params.json', cpl.cusumPlus)

class ADEPT2State_TestSuite(Base2StateTest):
	def test_e1a2s(self):
		self.runTestCase('testdata/test1.csv', 'testdata/test1.prm', a2s.adept2State)

	def test_e2a2s(self):
		self.runTestCase('testdata/test2.csv', 'testdata/test2.prm', a2s.adept2State)

	def test_e3a2s(self):
		self.runTestCase('testdata/test3.csv', 'testdata/test3.prm', a2s.adept2State)

	def test_e4a2s(self):
		self.runTestCase('testdata/test4.csv', 'testdata/test4.prm', a2s.adept2State)

	def test_e5a2s(self):
		self.runTestCase('testdata/test5.csv', 'testdata/test5.prm', a2s.adept2State)

	def test_e6a2s(self):
		self.runTestCase('testdata/test6.csv', 'testdata/test6.prm', a2s.adept2State)

	def test_e7a2s(self):
		self.runTestCase('testdata/test7.csv', 'testdata/test7.prm', a2s.adept2State)

	def test_e8a2s(self):
		self.runTestCase('testdata/test8.csv', 'testdata/test8.prm', a2s.adept2State)

	def test_e9a2s(self):
		self.runTestCase('testdata/test9.csv', 'testdata/test9.prm', a2s.adept2State)

	def test_e10a2s(self):
		self.runTestCase('testdata/test10.csv', 'testdata/test10.prm', a2s.adept2State)

	def test_e11a2s(self):
		self.runTestCase('testdata/test11.csv', 'testdata/test11.prm', a2s.adept2State)

	def test_e12a2s(self):
		self.runTestCase('testdata/test12.csv', 'testdata/test12.prm', a2s.adept2State)

	def test_e13a2s(self):
		self.runTestCase('testdata/test13.csv', 'testdata/test13.prm', a2s.adept2State)
	
	def test_e14a2s(self):
		self.runTestCase('testdata/test14.csv', 'testdata/test14.prm', a2s.adept2State)

	def test_e15a2s(self):
		self.runTestCase('testdata/test15.csv', 'testdata/test15.prm', a2s.adept2State)

class SSETestSuite(SSETest):
	def test_e1sse(self):
		self.runTestCase('testdata/test1.csv', 'testdata/test1.prm', sse.singleStepEvent)

	def test_e2sse(self):
		self.runTestCase('testdata/test2.csv', 'testdata/test2.prm', sse.singleStepEvent)

	def test_e3sse(self):
		self.runTestCase('testdata/test3.csv', 'testdata/test3.prm', sse.singleStepEvent)

	def test_e4sse(self):
		self.runTestCase('testdata/test4.csv', 'testdata/test4.prm', sse.singleStepEvent)

	def test_e5sse(self):
		self.runTestCase('testdata/test5.csv', 'testdata/test5.prm', sse.singleStepEvent)

	def test_e6sse(self):
		self.runTestCase('testdata/test6.csv', 'testdata/test6.prm', sse.singleStepEvent)

	def test_e7sse(self):
		self.runTestCase('testdata/test7.csv', 'testdata/test7.prm', sse.singleStepEvent)

	def test_e8sse(self):
		self.runTestCase('testdata/test8.csv', 'testdata/test8.prm', sse.singleStepEvent)

	def test_e9sse(self):
		self.runTestCase('testdata/test9.csv', 'testdata/test9.prm', sse.singleStepEvent)

	def test_e10sse(self):
		self.runTestCase('testdata/test10.csv', 'testdata/test10.prm', sse.singleStepEvent)

	def test_e11sse(self):
		self.runTestCase('testdata/test11.csv', 'testdata/test11.prm', sse.singleStepEvent)

	def test_e12sse(self):
		self.runTestCase('testdata/test12.csv', 'testdata/test12.prm', sse.singleStepEvent)

	def test_e13sse(self):
		self.runTestCase('testdata/test13.csv', 'testdata/test13.prm', sse.singleStepEvent)

	def test_e14sse(self):
		self.runTestCase('testdata/test14.csv', 'testdata/test14.prm', sse.singleStepEvent)

	def test_e15sse(self):
		self.runTestCase('testdata/test15.csv', 'testdata/test15.prm', sse.singleStepEvent)
