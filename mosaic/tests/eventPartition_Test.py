from mosaic.tests.eventPartitionCommon import EventPartitionTest
import mosaic.partition.eventSegment as es

class EventPartitionSingle_TestSuite(EventPartitionTest):
	def test_eventPartition(self):
		for i in range(1,6):
			basename='mosaic/tests/testdata/testEventPartition'+str(i)
			yield self.runTestCase, basename+'.csv', basename+'.prm', es.eventSegment, False

	def test_eventPartitionErrors(self):
		for param in ['writeEventTS', 'driftThreshold', 'blockSizeSec', 'meanOpenCurr', 'sdOpenCurr', 'slopeOpenCurr','driftThreshold','maxDriftRate', 'eventThreshold']:
			basename='mosaic/tests/testdata/testEventPartition1'
			yield self.runTestError, basename+'.csv', param, es.eventSegment, False
