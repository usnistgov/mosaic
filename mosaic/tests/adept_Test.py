import mosaic.process.adept as adept
from mosaic.tests.algorithmCommon import BaseMultiStateTest

class ADEPT_TestSuite(BaseMultiStateTest):
	def test_adept(self):
		for i in [0,2,3,4,5,6,7,8,10,11,12,14,15,16,17,18,19,20]:
			basename='mosaic/tests/testdata/eventLong_'+str(i)
			yield self.runTestCase, basename+'_raw.bin', basename+'_params.json', adept.adept

	def test_adepterror(self):
		basename='mosaic/tests/testdata/eventLong_0'

		for param in [ "StepSize", "MinStateLength", "MaxEventLength", "FitTol", "FitIters", "LinkRCConst" ]:
			yield self.runTestError, basename+'_raw.bin', basename+'_params.json', adept.adept, param

	def test_adeptattrr(self):
		basename='mosaic/tests/testdata/eventLong_0'

		yield self.runTestAttr, basename+'_raw.bin', basename+'_params.json', adept.adept

