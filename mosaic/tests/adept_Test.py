import mosaic.process.adept as adept
from mosaic.tests.algorithmCommon import BaseMultiStateTest

class ADEPT_TestSuite(BaseMultiStateTest):
	def test_adept(self):
		for i in [0,2,3,4,5,6,7,8,10,11,12,14,15,16,17,18,19,20]:
			basename='mosaic/tests/testdata/eventLong_'+str(i)
			yield self.runTestCase, basename+'_raw.bin', basename+'_params.json', adept.adept