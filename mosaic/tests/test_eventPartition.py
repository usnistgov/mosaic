import pytest
from mosaic.tests.eventPartitionCommon import EventPartitionTest
import mosaic.partition.eventSegment as es

@pytest.fixture
def EventPartitionTestObject():
	return EventPartitionTest()


def test_eventPartition(EventPartitionTestObject):
	for i in range(1,6):
		basename='mosaic/tests/testdata/testEventPartition'+str(i)
		EventPartitionTestObject.runTestCase(basename+'.csv', basename+'.prm', es.eventSegment, False)

def test_eventPartitionErrors(EventPartitionTestObject):
	for param in ['writeEventTS', 'driftThreshold', 'blockSizeSec', 'meanOpenCurr', 'sdOpenCurr', 'slopeOpenCurr','driftThreshold','maxDriftRate', 'eventThreshold']:
		basename='mosaic/tests/testdata/testEventPartition1'
		EventPartitionTestObject.runTestError(basename+'.csv', param, es.eventSegment, False)
