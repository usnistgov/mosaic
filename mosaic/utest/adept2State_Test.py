import mosaic.adept2State as a2s 
from mosaic.utest.algorithmCommon import Base2StateTest

class TwoState_TestSuite(Base2StateTest):
	def test_adept2state(self):
		for i in range(1,15):
			basename='testdata/test'+str(i)
			yield self.runTestCase, basename+'.csv', basename+'.prm', a2s.adept2State
