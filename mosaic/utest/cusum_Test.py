import mosaic.cusumPlus as cpl
from mosaic.utest.algorithmCommon import BaseMultiStateTest

class CUSUM_TestSuite(BaseMultiStateTest):
	def test_cusum(self):
		for i in [0,2,3,4,5,6,7,8,10,11,12,14,15,16,17,18,19,20]:
			basename='testdata/eventLong_'+str(i)
			baseobj=BaseMultiStateTest()

			yield self.runTestCase, basename+'_raw.bin', basename+'_params.json', cpl.cusumPlus