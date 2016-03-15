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


class Base2StateTest(object): 
	def _setupTestCase(self, datfile, prmfile, algoHnd):
		[self.Fs, self.dat]=testutil.readcsv(datfile)
		self.prm=testutil.readparams(prmfile)

		self.sett = (settings.settings('.', defaultwarn=False).settingsDict)[algoHnd.__name__]

		self.dt=int(1e6/self.dat[0])

	def runTestCase(self, datfile, prmfile, algoHnd):
		self._setupTestCase(datfile, prmfile,algoHnd)

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

		assert self.testobj.mdProcessingStatus == 'normal' 
		assert round(self.testobj.mdBlockDepth,1) == 1.0-abs(self.prm['a']) 
		assert round(self.testobj.mdResTime,1) == (self.prm['tau2']-self.prm['tau1'])/1000. 


class BaseMultiStateTest(object):
	def _setupTestCase(self, datfile, prmfile, algoHnd):
		self.dat=testutil.readDataRAW(datfile)
		self.prm=testutil.readParametersJSON(prmfile)
		self.Fs=int(self.prm['FsKHz']*1000)

		self.dt=1./self.prm['FsKHz']

		self.noiseRMS=self.prm['noisefArtHz']*np.sqrt(self.prm['BkHz']*1000.)/1000.
				
		self.sett = (settings.settings('.', defaultwarn=False).settingsDict)[algoHnd.__name__]
		# self.sett={}

		# self.sett["InitThreshold"] = 4.5
		# self.sett["MinStateLength"] = 10
		# self.sett["FitIters"] = 5000
		# self.sett["FitTol"] = 1.0e-7
		# self.sett["MaxEventLength"] = 100000
		# self.sett["UnlinkRCConst"] = 0
	
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

		assert testobj.mdProcessingStatus == 'normal'
		

class EventPartitionTest(object):

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

		assert testobj.eventcount == prm['nevents']

		testobj.Stop()

		for f in glob.glob('testdata/*.sqlite'):
			os.remove(f)

class EventPartition_TestSuite(EventPartitionTest):
	def test_eventPartition(self):
		for i in range(1,5):
			basename='testdata/testEventPartition'+str(i)
			yield self.runTestCase, basename+'.csv', basename+'.prm', es.eventSegment, False

	def test_eventPartition(self):
		for i in range(1,5):
			basename='testdata/testEventPartition'+str(i)
			yield self.runTestCase, basename+'.csv', basename+'.prm', es.eventSegment, True


class Multistate_TestSuite(BaseMultiStateTest):
	def test_adept(self):
		for i in [0,2,3,4,5,6,7,8,10,11,12,14,15,16,17,18,19,20]:
			basename='testdata/eventLong_'+str(i)
			yield self.runTestCase, basename+'_raw.bin', basename+'_params.json', adept.adept

	def test_cusum(self):
		for i in [0,2,3,4,5,6,7,8,10,11,12,14,15,16,17,18,19,20]:
			basename='testdata/eventLong_'+str(i)
			baseobj=BaseMultiStateTest()

			yield self.runTestCase, basename+'_raw.bin', basename+'_params.json', cpl.cusumPlus


class TwoState_TestSuite(Base2StateTest):
	def test_adept2state(self):
		for i in range(1,15):
			basename='testdata/test'+str(i)
			yield self.runTestCase, basename+'.csv', basename+'.prm', a2s.adept2State
