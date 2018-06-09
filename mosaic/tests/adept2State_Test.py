import mosaic.process.adept2State as a2s 
from mosaic.tests.algorithmCommon import Base2StateTest, DatBlockTest

class TwoState_TestSuite(Base2StateTest):
	def test_adept2state(self):
		for i in range(1,15):
			basename='mosaic/tests/testdata/test'+str(i)
			yield self.runTestCase, basename+'.csv', basename+'.prm', a2s.adept2State

	def test_adepterror(self):
		basename='mosaic/tests/testdata/test1'

		for param in [ "FitTol", "FitIters", "BlockRejectRatio", "LinkRCConst" ]:
			yield self.runTestError, basename+'.csv', basename+'.prm', a2s.adept2State, param

class adept2sDatBlock_TestSuite(DatBlockTest):
	def test_datblock(self):
		yield self.runTestCase, a2s