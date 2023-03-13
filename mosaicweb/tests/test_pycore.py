import os
import time
import pytest
import numpy as np
import mosaicweb.mosaicAnalysis.analysisHistogram as analysisHistogram
import mosaicweb.mosaicAnalysis.analysisContour as analysisContour
import mosaicweb.mosaicAnalysis.analysisStatistics as analysisStatistics
import mosaicweb.mosaicAnalysis.analysisTimeSeries as analysisTimeSeries
import mosaicweb.mosaicAnalysis.analysisDBUtils as analysisDBUtils
import mosaicweb.mosaicAnalysis.mosaicAnalysis as mosaicAnalysis
import mosaicweb.sessionManager.sessionManager as sessionManager
import mosaicweb.plotlyUtils.plotlyWrapper as plotlyWrapper
from mosaic.utilities.resource_path import resource_path
import mosaic
import mosaic.settings as settings

def _setupAnalysis(**kwargs):
	try:
		ma=mosaicAnalysis.mosaicAnalysis(mosaic.__path__[0]+"/.."+"/data/", "session", kwargs["settingsString"])
	except:
		ma=mosaicAnalysis.mosaicAnalysis(mosaic.__path__[0]+"/.."+"/data/", "session") 
	
	assert ma.analysisStatus == False
	assert ma.returnMessageJSON == { 

					"warning": "" 

			}

	ma.setupAnalysis()

	return ma

def test_analysisHistogramInit():
	ac=analysisHistogram.analysisHistogram(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "", 200, False)

	assert ac.responseDict == {}
	assert ac.queryString == ""

def test_analysisHistogramADEPT2State():
	ac=analysisHistogram.analysisHistogram(
		resource_path("eventMD-PEG28-ADEPT2State.sqlite"), 
		"""select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.2""", 
		200, 
		False
	)

	res=ac.analysisHistogram()

	assert len(res.keys()) > 0

def test_analysisPDFADEPT2State():
	ac=analysisHistogram.analysisHistogram(
		resource_path("eventMD-PEG28-ADEPT2State.sqlite"), 
		"""select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.2""", 
		200, 
		True
	)

	res=ac.analysisHistogram()

	assert len(res.keys()) > 0

def test_analysisContourInit():
	ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "", 200, False)

	assert ac.responseDict == {}
	assert ac.queryString == """select BlockDepth, ResTime from metadata where ProcessingStatus='normal' and ResTime > 0.02"""

def test_analysisContourADEPT2State():
	ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "", 200, False)

	res=ac.analysisContour()

	assert len(res.keys()) > 0
	assert res['data'][0]['type'] == "heatmap"
	assert res['queryCols'] == ['BlockedCurrent', 'BlockDepth', 'ResTime']

def test_analysisContourADEPT():
	ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "", 200, False)

	ac.processingAlgorithm="ADEPT"
	ac._queryString("")
	ac._queryCols()
	ac._queryConsCols()
	ac._querySelectedCols()

	assert ac.responseDict == {}

def test_analysisContourQuerySyntax():
	ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), """select ResTime from metadata where ProcessingStatus='normal' and ResTime > 0.02""", 200, False)

	with pytest.raises(analysisContour.QuerySyntaxError):
		ac._hist2d()

	res=ac.analysisContour()

	assert len(res.keys()) > 0
	assert res['data'][0]['type'] == "heatmap"
	assert res['queryCols'] == ['BlockedCurrent', 'BlockDepth', 'ResTime']

def test_analysisStatistics():
	ac=analysisStatistics.analysisStatistics(resource_path("eventMD-PEG28-ADEPT2State.sqlite"))

	res=ac.analysisStatistics()

	assert len(res.keys()) > 0

def test_analysisTimeSeries():
	np.seterr(over='ignore', invalid='ignore')
	ac=analysisTimeSeries.analysisTimeSeries(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), 1, ['normal', 'warning', 'error'])

	res=ac.timeSeries()

	assert len(res.keys()) > 0

def test_analysisDBUtilsInit():
	adb=analysisDBUtils.analysisDBUtils(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "")

	assert adb.responseDict == {}


def test_analysisDBUtils():
	adb=analysisDBUtils.analysisDBUtils(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "")

	assert adb.responseDict == {}
	
	res=adb.csv()

	assert len(res["dbName"]) > 0
	assert len(res["dbData"]) > 0

def test_mosaicAnalysisSetup():
	ma=_setupAnalysis(settingsString=open(mosaic.__path__[0]+"/.."+"/data/.settings", 'r').read())

	assert ma.defaultSettings == False

def test_mosaicAnalysisSetupDefault():
	ma=_setupAnalysis()

	sObj=settings.settings("", defaultwarn=False)
		
	ma.analysisSettingsDict=sObj.settingsDict
	ma.defaultSettings=sObj.defaultSettingsLoaded

	ma.setupAnalysis()
	ma._pruneDefaultSettings()

	assert ma.defaultSettings == True

# def test_runAnalysis():
# 	ma=_setupAnalysis(settingsString=open(mosaic.__path__[0]+"/.."+"/data/.settings", 'r').read())

# 	ma.runAnalysis()

# 	assert ma.analysisStatus == True
# 	dbFile=ma.dbFile
	
# 	ma.stopAnalysis()

# 	os.remove(dbFile)

# 	tempfile=dbFile.split(".sqlite")[0].split("eventMD-")
# 	os.remove(tempfile[0]+"/eventProcessing-"+tempfile[1]+".log")
	
def test_sessionDict():
	s=sessionManager.session()

	s["sessionID"]="sessionID"
	
	s.update({"analysisRunning" : True})

	assert s["sessionID"] == "sessionID"
	assert "sessionRunStartTime" in s.keys()

def test_sessionManager():
	s=sessionManager.sessionManager()

	sid=s.newSession()

	s.addAnalysisRunningFlag(sid, True)
	s.addDatabaseFile(sid, resource_path("eventMD-PEG28-ADEPT2State.sqlite"))

	assert s.getSessionAttribute(sid, 'analysisRunning') == True

def test_sessionManagerSessionNotFoundError():
	sm=sessionManager.sessionManager()

	with pytest.raises(sessionManager.SessionNotFoundError):
		sm.getSession("")

	with pytest.raises(sessionManager.SessionNotFoundError):
		sm.getSessionAttribute("", "")

	with pytest.raises(sessionManager.SessionNotFoundError):
		sm.addSettingsString("", "")

def test_sessionManagerAttributeNotFoundError():
	sm=sessionManager.sessionManager()

	sid=sm.newSession()

	sm.addSettingsString(sid, "")

	with pytest.raises(sessionManager.AttributeNotFoundError):
		sm.getSessionAttribute(sid, "db")

def test_plotlyWrapperErrors():
	with pytest.raises(plotlyWrapper.InvalidTraceTypeError):
		plotlyWrapper.plotlyTrace([],[],"")

	with pytest.raises(plotlyWrapper.InvalidLayoutTypeError):
		plotlyWrapper.plotlyLayout("")

