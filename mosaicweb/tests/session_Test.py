import unittest
import time
import mosaicweb.tests.mwebCommon
from mosaicweb.tests.mwebCommon import mwebCommonTest

class Session_TestSuite(mwebCommonTest):
	def test_newAnalysis(self):
		result=self._post( '/new-analysis', dict( dataPath="data/" ) )

		self.assertBaseline("new-analysis", result)

	def test_newAnalysisError(self):
		result=self._post( '/new-analysis', dict() )

		self.assertBaselineError("new-analysis", result)

	def test_runAnalysis(self):
		result=self._post( '/new-analysis', dict( dataPath="data/" ) )
		self.assertBaseline("new-analysis", result)

		d=self._get_data(result)


		result=self._post( '/start-analysis', dict( sessionID=d["sessionID"] ) )

		self.assertBaseline("start-analysis", result)

		# time.sleep(3)

		result=self._post( '/stop-analysis', dict( sessionID=d["sessionID"] ) )
		self.assertBaseline("stop-analysis", result)
		

	def test_loadAnalysis(self):
		result=self._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )

		d=self._get_data(result)
		self.assertBaseline("load-analysis", result)

	def test_loadHistogram(self):
		self._histTest(False)

	def test_loadPDF(self):
		self._histTest(True)

	def test_loadContour(self):
		result=self._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )
		d=self._get_data(result)

		result=self._post( '/analysis-contour', dict( 
			sessionID=d["sessionID"],
			query="select BlockDepth, ResTime from metadata where ProcessingStatus='normal' and ResTime > 0.02",
			nBins=200, 
			databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) 
		)
		d=result.get_data()
		# self.assertBaseline("analysis-contour", result)
		self.assertGreater(len(d), 0)

	def test_analysisLog(self):
		result=self._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )
		d=self._get_data(result)

		result=self._post( '/analysis-log', dict( 
			sessionID=d["sessionID"],
			databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) 
		)
		d=self._get_data(result)

		self.assertBaseline("analysis-log", result)
		self.assertGreater(len(d["logText"]), 0)

	def test_analysisStatistics(self):
		result=self._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )
		d=self._get_data(result)

		result=self._post( '/analysis-statistics', dict( 
			sessionID=d["sessionID"],
			databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) 
		)
		d=self._get_data(result)

		d1={'fractionWarn': 0.0, 'openChannelCurrentMean': 136.8, 'dataType': 'qdf', 'captureRateSigma': 21.3, 'nTotal': 420, 'fractionNormal': 0.995, 'FskHz': 500.0, 'processTimePerEventSigma': 5.0, 'analysisProgressPercent': 100, 'openChannelCurrentSigma': 0.7, 'partitionAlgorithm': 'CurrentThreshold', 'captureRateMean': 434.9, 'fractionError': 0.005, 'processingAlgorithm': 'ADEPT 2-state', 'processTimePerEventMean': 9.2}

		self.assertBaseline("analysis-statistics", result)
		
		[ self.assertEqual(d[k], d1[k]) for k in d1.keys() ]

	def test_eventView(self):
		result=self._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )
		d=self._get_data(result)
		sid=d["sessionID"]
		
		for i in range(50):
			result=self._post( '/event-view', dict( 
					sessionID=sid,
					eventNumber=i
				)
			)
			d=self._get_data(result)

			self.assertBaseline("event-view", result)
			self.assertEqual(d["errorText"], "")
			self.assertEqual(d["warning"], "")

	def test_validateSettings(self):	
		result=self._post( '/validate-settings', dict( analysisSettings="{}" ) )

		self.assertBaseline("validate-settings", result)

	def test_validateSettingsError(self):	
		result=self._post( '/validate-settings', dict( analysisSettings="" ) )

		self.assertBaselineError("validate-settings", result)

	def test_processingAlgorithm(self):	
		result=self._post( '/processing-algorithm', dict( procAlgorithm="adept" ) )

		self.assertBaseline("processing-algorithm", result)

	def test_processingAlgorithmError(self):	
		result=self._post( '/processing-algorithm', dict( procAlgorithm="proc" ) )

		self.assertBaselineError("processing-algorithm", result)



	def _histTest(self, density):
		result=self._post( '/load-analysis', dict( databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite" ) )
		d=self._get_data(result)

		result=self._post( '/analysis-histogram', dict( 
				sessionID=d["sessionID"],
				query="select BlockDepth from metadata where ResTime > 0.02",
				nBins=500, 
				databaseFile="data/eventMD-PEG28-ADEPT2State.sqlite",
				density=density
			)
			
		)
		d=self._get_data(result)

		self.assertBaseline("analysis-histogram", result)
		self.assertGreater(d.keys(), 0)
		
