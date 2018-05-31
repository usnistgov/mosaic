import mosaicweb.mosaicAnalysis.analysisContour as analysisContour
from mosaic.utilities.resource_path import resource_path
from mosaicweb.tests.mwebCommon import mwebSimpleCommonTest

class Status_TestSuite(mwebSimpleCommonTest):
	def test_analysisContourInit(self):
		ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "", 200, False)

		self.assertEqual(ac.responseDict, {})
		self.assertEqual(ac.queryString, """select BlockDepth, ResTime from metadata where ProcessingStatus='normal' and ResTime > 0.02""")

	def test_analysisContour(self):
		ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), "", 200, False)

		res=ac.analysisContour()

		self.assertGreater(len(res.keys()), 0)
		self.assertEqual(res['data'][0]['type'], "heatmap")
		self.assertEqual(res['queryCols'], ['BlockedCurrent', 'BlockDepth', 'ResTime'])


	def test_analysisContourQuerySyntax(self):
		ac=analysisContour.analysisContour(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), """select ResTime from metadata where ProcessingStatus='normal' and ResTime > 0.02""", 200, False)

		with self.assertRaises(analysisContour.QuerySyntaxError):
			ac._hist2d()

		res=ac.analysisContour()

		self.assertGreater(len(res.keys()), 0)
		self.assertEqual(res['data'][0]['type'], "heatmap")
		self.assertEqual(res['queryCols'], ['BlockedCurrent', 'BlockDepth', 'ResTime'])		