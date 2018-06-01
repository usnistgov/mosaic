import os
import time
import mosaicweb.mosaicAnalysis.analysisContour as analysisContour
import mosaicweb.mosaicAnalysis.analysisDBUtils as analysisDBUtils
import mosaicweb.mosaicAnalysis.mosaicAnalysis as mosaicAnalysis
import mosaicweb.sessionManager.sessionManager as sessionManager
import mosaicweb.plotlyUtils.plotlyWrapper as plotlyWrapper
from mosaic.utilities.resource_path import resource_path
from mosaicweb.tests.mwebCommon import mwebSimpleCommonTest
import mosaic
import mosaic.settings as settings

class Status_TestSuite(mwebSimpleCommonTest):
	def test_analysisContourInit(self):
		ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "", 200, False)

		self.assertEqual(ac.responseDict, {})
		self.assertEqual(ac.queryString, """select BlockDepth, ResTime from metadata where ProcessingStatus='normal' and ResTime > 0.02""")

	def test_analysisContourADEPT2State(self):
		ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "", 200, False)

		res=ac.analysisContour()

		self.assertGreater(len(res.keys()), 0)
		self.assertEqual(res['data'][0]['type'], "heatmap")
		self.assertEqual(res['queryCols'], ['BlockedCurrent', 'BlockDepth', 'ResTime'])

	def test_analysisContourADEPT(self):
		ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "", 200, False)

		ac.processingAlgorithm="ADEPT"
		ac._queryString("")
		ac._queryCols()
		ac._queryConsCols()
		ac._querySelectedCols()

		self.assertEqual(ac.responseDict, {})


	def test_analysisContourQuerySyntax(self):
		ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), """select ResTime from metadata where ProcessingStatus='normal' and ResTime > 0.02""", 200, False)

		with self.assertRaises(analysisContour.QuerySyntaxError):
			ac._hist2d()

		res=ac.analysisContour()

		self.assertGreater(len(res.keys()), 0)
		self.assertEqual(res['data'][0]['type'], "heatmap")
		self.assertEqual(res['queryCols'], ['BlockedCurrent', 'BlockDepth', 'ResTime'])		


	def test_analysisDBUtilsInit(self):
		adb=analysisDBUtils.analysisDBUtils(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "")

		self.assertEqual(adb.responseDict, {})


	def test_analysisDBUtils(self):
		adb=analysisDBUtils.analysisDBUtils(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "")

		self.assertEqual(adb.responseDict, {})
		
		res=adb.csv()

		self.assertGreater(len(res["dbName"]), 0)
		self.assertGreater(len(res["dbData"]), 0)

	def test_mosaicAnalysisSetup(self):
		ma=self._setupAnalysis(settingsString=open(mosaic.WebServerDataLocation+"/data/.settings", 'r').read())

		self.assertEqual(ma.defaultSettings, False)

	def test_mosaicAnalysisSetupDefault(self):
		ma=self._setupAnalysis()

		sObj=settings.settings("", defaultwarn=False)
			
		ma.analysisSettingsDict=sObj.settingsDict
		ma.defaultSettings=sObj.defaultSettingsLoaded

		ma.setupAnalysis()
		ma._pruneDefaultSettings()

		self.assertEqual(ma.defaultSettings, True)

	def test_runAnalysis(self):
		ma=self._setupAnalysis(settingsString=open(mosaic.WebServerDataLocation+"/data/.settings", 'r').read())

		ma.runAnalysis()

		self.assertEqual(ma.analysisStatus, True)
		dbFile=ma.dbFile
		
		ma.stopAnalysis()

		os.remove(dbFile)

		tempfile=dbFile.split(".sqlite")[0].split("eventMD-")
		os.remove(tempfile[0]+"/eventProcessing-"+tempfile[1]+".log")
	

	def test_sessionDict(self):
		s=sessionManager.session()

		s["sessionID"]="sessionID"
		
		s.update({"analysisRunning" : True})

		self.assertEqual(s["sessionID"], "sessionID")
		self.assertIn("sessionRunStartTime", s.keys())

	def test_sessionManagerSessionNotFoundError(self):
		sm=sessionManager.sessionManager()

		with self.assertRaises(sessionManager.SessionNotFoundError):
			sm.getSession("")

		with self.assertRaises(sessionManager.SessionNotFoundError):
			sm.getSessionAttribute("", "")

		with self.assertRaises(sessionManager.SessionNotFoundError):
			sm.addSettingsString("", "")

	def test_sessionManagerAttributeNotFoundError(self):
		sm=sessionManager.sessionManager()

		sid=sm.newSession()

		sm.addSettingsString(sid, "")

		with self.assertRaises(sessionManager.AttributeNotFoundError):
			sm.getSessionAttribute(sid, "db")

	def test_plotlyWrapperErrors(self):
		with self.assertRaises(plotlyWrapper.InvalidTraceTypeError):
			plotlyWrapper.plotlyTrace([],[],"")

		with self.assertRaises(plotlyWrapper.InvalidLayoutTypeError):
			plotlyWrapper.plotlyLayout("")

	def _setupAnalysis(self, **kwargs):
		try:
			ma=mosaicAnalysis.mosaicAnalysis(mosaic.WebServerDataLocation+"/data/", "session", kwargs["settingsString"])
		except:
			ma=mosaicAnalysis.mosaicAnalysis(mosaic.WebServerDataLocation+"/data/", "session") 
		
		self.assertEqual(ma.analysisStatus, False)
		self.assertEqual(ma.returnMessageJSON, { 

						"warning": "" 

				}
			 )

		ma.setupAnalysis()

		return ma
