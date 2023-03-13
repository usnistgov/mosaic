import pytest
from mosaicweb.tests.mwebCommon import mwebCommonTest

@pytest.fixture
def mwebCommonTestObject():
	return mwebCommonTest()

def test_init(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/initialization', dict() )

	d=mwebCommonTestObject._get_data(result)

	mwebCommonTestObject.assertBaseline("initialization", result)

def test_about(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/about', dict() )

	d=mwebCommonTestObject._get_data(result)

	mwebCommonTestObject.assertBaseline("about", result)
	assert eval(d["ver"][0]) >= 2

def test_listActiveSessions(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/list-active-sessions', dict() )

	d=mwebCommonTestObject._get_data(result)

	print(d)

	mwebCommonTestObject.assertBaseline("list-active-sessions", result)
	assert len(d["sessions"]) >= 0
