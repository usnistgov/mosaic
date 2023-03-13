import unittest
import pytest 
import time
import mosaic
import mosaicweb.tests.mwebCommon
from mosaicweb.tests.mwebCommon import mwebCommonTest

@pytest.fixture
def mwebCommonTestObject():
	return mwebCommonTest()

@unittest.skipUnless(mosaic.WebServerMode=="local", "requires local web server.")
def _histTest(mwebCommonTestObject, density):
	result=mwebCommonTestObject._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )
	d=mwebCommonTestObject._get_data(result)

	result=mwebCommonTestObject._post( '/analysis-histogram', dict( 
			sessionID=d["sessionID"],
			query="select BlockDepth from metadata where ResTime > 0.02",
			nBins=500, 
			databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite",
			density=density
		)
		
	)
	d=mwebCommonTestObject._get_data(result)

	mwebCommonTestObject.assertBaseline("analysis-histogram", result)
	assert len(d.keys()) > 0

@unittest.skipUnless(mosaic.WebServerMode=="local", "requires local web server.")
def test_newAnalysis(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/new-analysis', dict( dataPath="data/" ) )

	mwebCommonTestObject.assertBaseline("new-analysis", result)

def test_newAnalysisError(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/new-analysis', dict() )

	mwebCommonTestObject.assertBaselineError("new-analysis", result)

@unittest.skipUnless(mosaic.WebServerMode=="local", "requires local web server.")
def test_runAnalysis(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/new-analysis', dict( dataPath="data/" ) )
	mwebCommonTestObject.assertBaseline("new-analysis", result)

	d=mwebCommonTestObject._get_data(result)


	result=mwebCommonTestObject._post( '/start-analysis', dict( sessionID=d["sessionID"] ) )

	mwebCommonTestObject.assertBaseline("start-analysis", result)

	#time.sleep(3)

	# result=mwebCommonTestObject._post( '/stop-analysis', dict( sessionID=d["sessionID"] ) )
	# mwebCommonTestObject.assertBaseline("stop-analysis", result)
	
@unittest.skipUnless(mosaic.WebServerMode=="local", "requires local web server.")
def test_loadAnalysis(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )

	d=mwebCommonTestObject._get_data(result)
	mwebCommonTestObject.assertBaseline("load-analysis", result)

def test_loadHistogram(mwebCommonTestObject):
	_histTest(mwebCommonTestObject, False)

def test_loadPDF(mwebCommonTestObject):
	_histTest(mwebCommonTestObject, True)

@unittest.skipUnless(mosaic.WebServerMode=="local", "requires local web server.")
def test_loadContour(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )
	d=mwebCommonTestObject._get_data(result)

	result=mwebCommonTestObject._post( '/analysis-contour', dict( 
		sessionID=d["sessionID"],
		query="select BlockDepth, ResTime from metadata where ProcessingStatus='normal' and ResTime > 0.02",
		nBins=200, 
		databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) 
	)
	d=result.get_data()
	# self.assertBaseline("analysis-contour", result)
	assert len(d) > 0

@unittest.skipUnless(mosaic.WebServerMode=="local", "requires local web server.")
def test_analysisLog(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )
	print(result)
	d=mwebCommonTestObject._get_data(result)

	print(d)
	result=mwebCommonTestObject._post( '/analysis-log', dict( 
		sessionID=d["sessionID"],
		databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) 
	)
	d=mwebCommonTestObject._get_data(result)

	mwebCommonTestObject.assertBaseline("analysis-log", result)
	assert len(d["logText"]) > 0

@unittest.skipUnless(mosaic.WebServerMode=="local", "requires local web server.")
def test_analysisStatistics(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )
	d=mwebCommonTestObject._get_data(result)

	result=mwebCommonTestObject._post( '/analysis-statistics', dict( 
		sessionID=d["sessionID"],
		databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) 
	)
	d=mwebCommonTestObject._get_data(result)

	d1={'fractionWarn': 0.0, 'openChannelCurrentMean': 136.8, 'dataType': 'qdf', 'captureRateSigma': 21.3, 'nTotal': 420, 'fractionNormal': 0.995, 'FskHz': 500.0, 'processTimePerEventSigma': 5.0, 'analysisProgressPercent': 100, 'openChannelCurrentSigma': 0.7, 'partitionAlgorithm': 'CurrentThreshold', 'captureRateMean': 434.9, 'fractionError': 0.005, 'processingAlgorithm': 'ADEPT 2-state', 'processTimePerEventMean': 9.2}

	mwebCommonTestObject.assertBaseline("analysis-statistics", result)
	
	assert all(d[k] == d1[k] for k in d1.keys())

@unittest.skipUnless(mosaic.WebServerMode=="local", "requires local web server.")
def test_eventView(mwebCommonTestObject):
	result=mwebCommonTestObject._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )
	d=mwebCommonTestObject._get_data(result)
	sid=d["sessionID"]
	
	for i in range(50):
		result=mwebCommonTestObject._post( '/event-view', dict( 
				sessionID=sid,
				eventNumber=i
			)
		)
		d=mwebCommonTestObject._get_data(result)

		mwebCommonTestObject.assertBaseline("event-view", result)
		assert d["errorText"] == ""
		assert d["warning"] == ""

def test_validateSettings(mwebCommonTestObject):	
	result=mwebCommonTestObject._post( '/validate-settings', dict( analysisSettings="{}" ) )

	mwebCommonTestObject.assertBaseline("validate-settings", result)

def test_validateSettingsError(mwebCommonTestObject):	
	result=mwebCommonTestObject._post( '/validate-settings', dict( analysisSettings="" ) )

	mwebCommonTestObject.assertBaselineError("validate-settings", result)

def test_processingAlgorithm(mwebCommonTestObject):	
	result=mwebCommonTestObject._post( '/processing-algorithm', dict( procAlgorithm="adept" ) )

	mwebCommonTestObject.assertBaseline("processing-algorithm", result)

def test_processingAlgorithmError(mwebCommonTestObject):	
	result=mwebCommonTestObject._post( '/processing-algorithm', dict( procAlgorithm="proc" ) )

	mwebCommonTestObject.assertBaselineError("processing-algorithm", result)
	
