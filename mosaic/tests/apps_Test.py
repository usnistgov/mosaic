import time
import mosaic.apps.SingleChannelAnalysis
import mosaic.partition.eventSegment as es
import mosaic.process.adept2State as adept2State
from mosaic.trajio.qdfTrajIO import *

from mosaic.filters.besselLowpassFilter import *
from mosaic.filters.waveletDenoiseFilter import *

class EventPartitionTest(object):
	def setUp(self):
		pass

	def setupTestCase(self):
		self.appObj=mosaic.apps.SingleChannelAnalysis.SingleChannelAnalysis(
			'data/',
			qdfTrajIO, 
			None,
			es.eventSegment,
			adept2State.adept2State
		)

	def runTest(self, forkProcess):
		self.setupTestCase()

		self.appObj.Run(forkProcess=forkProcess)

		if forkProcess:
			time.sleep(3)
			self.appObj.Stop()

	def runTestSetup(self):
		self.setupTestCase()

		assert type(self.appObj)==mosaic.apps.SingleChannelAnalysis.SingleChannelAnalysis

class EventPartitionSingle_TestSuite(EventPartitionTest):
	def test_singleChannelAppSetup(self):
		yield self.runTestSetup

	# def test_singleChannelAppSetupRun(self):
	# 	yield self.runTest, False

	def test_singleChannelAppSetupRunFork(self):
		yield self.runTest, True


