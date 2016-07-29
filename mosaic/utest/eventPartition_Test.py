from mosaic.utest.eventPartitionCommon import EventPartitionTest
import mosaic.partition.eventSegment as es

class EventPartitionSingle_TestSuite(EventPartitionTest):
	def test_eventPartition(self):
		for i in range(1,6):
			basename='testdata/testEventPartition'+str(i)
			yield self.runTestCase, basename+'.csv', basename+'.prm', es.eventSegment, False