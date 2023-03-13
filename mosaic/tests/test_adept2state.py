import pytest
import mosaic.process.adept2State as a2s 
from mosaic.tests.algorithmCommon import Base2StateTest, DatBlockTest

@pytest.fixture
def Base2StateTestObject(request):
	basename='mosaic/tests/testdata/test'+str(request.param)

	b=Base2StateTest()
	b.datFile=basename+'.csv'
	b.prmFile=basename+'.prm'
	return b

@pytest.fixture
def Base2StateErrorObject(request):
	basename='mosaic/tests/testdata/test1'

	b=Base2StateTest()
	b.datFile=basename+'.csv'
	b.prmFile=basename+'.prm'
	b.prmStr=request.param
	return b

@pytest.fixture
def DatBlockTestObject():
	return DatBlockTest()

@pytest.mark.parametrize(
		'Base2StateTestObject',
		(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15),
		indirect=True
	)
def test_adept2state(Base2StateTestObject):
	Base2StateTestObject.runTestCase(Base2StateTestObject.datFile, Base2StateTestObject.prmFile, a2s.adept2State)

@pytest.mark.parametrize(
		'Base2StateErrorObject',
		("FitTol", "FitIters", "BlockRejectRatio", "LinkRCConst"),
		indirect=True
	)
def test_adepterror(Base2StateErrorObject):
	Base2StateErrorObject.runTestError(Base2StateErrorObject.datFile, Base2StateErrorObject.prmFile, a2s.adept2State, Base2StateErrorObject.prmStr)


def test_datblock(DatBlockTestObject):
	DatBlockTestObject.runTestCase(a2s)