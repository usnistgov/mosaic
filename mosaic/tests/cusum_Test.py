import mosaic.process.cusumPlus as cpl
from mosaic.tests.algorithmCommon import BaseMultiStateTest

class CUSUM_TestSuite(BaseMultiStateTest):
	def test_cusum(self):
		for i in [0,2,3,4,5,6,7,8,10,11,12,14,15,16,17,18,19,20]:
			basename='mosaic/tests/testdata/eventLong_'+str(i)
			baseobj=BaseMultiStateTest()

			yield self.runTestCase, basename+'_raw.bin', basename+'_params.json', cpl.cusumPlus

	def test_cusumerror(self):
		basename='mosaic/tests/testdata/eventLong_0'

		for param in [ "StepSize", "MinThreshold", "MaxThreshold", "MinLength" ]:
			yield self.runTestError, basename+'_raw.bin', basename+'_params.json', cpl.cusumPlus, param

	def test_cusumattrr(self):
		basename='mosaic/tests/testdata/eventLong_0'

		yield self.runTestAttr, basename+'_raw.bin', basename+'_params.json', cpl.cusumPlus