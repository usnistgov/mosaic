import pytest
import mosaic.process.adept as adept
from mosaic.tests.algorithmCommon import BaseMultiStateTest

@pytest.fixture
def baseMultiStateTestObject(request):
	b=BaseMultiStateTest()
	b.datFile='mosaic/tests/testdata/eventLong_'+str(request.param)+'_raw.bin'
	b.jsonFile='mosaic/tests/testdata/eventLong_0_params.json'
	return b

@pytest.fixture
def baseMultiStateErrorObject(request):
	basename='mosaic/tests/testdata/eventLong_0'

	b=BaseMultiStateTest()
	b.datFile=basename+'_raw.bin'
	b.jsonFile=basename+'_params.json'
	b.paramStr=request.param

	return b

@pytest.fixture
def baseMultiStateAttrObject():
	return BaseMultiStateTest()

@pytest.mark.parametrize(
		'baseMultiStateTestObject',
		(0,2,3,4,5,6,7,10,12,14,15,16,17,18,19,20),
		indirect=True
	)
def test_adept(baseMultiStateTestObject):
	baseMultiStateTestObject.runTestCase(baseMultiStateTestObject.datFile, baseMultiStateTestObject.jsonFile, adept.adept)

@pytest.mark.parametrize(
		'baseMultiStateErrorObject',
		("StepSize", "MinStateLength", "MaxEventLength", "FitTol", "FitIters", "LinkRCConst"),
		indirect=True
	)
def test_adepterror(baseMultiStateErrorObject):
	baseMultiStateErrorObject.runTestError(baseMultiStateErrorObject.datFile, baseMultiStateErrorObject.jsonFile, adept.adept, baseMultiStateErrorObject.paramStr)

def test_adeptattrr(baseMultiStateAttrObject):
	basename='mosaic/tests/testdata/eventLong_0'

	baseMultiStateAttrObject.runTestAttr(basename+'_raw.bin', basename+'_params.json', adept.adept)
