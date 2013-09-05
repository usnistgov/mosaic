import random
import unittest
import testutil
import json

import stepResponseAnalysis as sra
import singleStepEvent as sse

class PEGTestFunctions(unittest.TestCase):

	def setUp(self):
		self.datapath = 'testdata'
		self.seq=range(1000)

	def runTestCase(self, datfile, prmfile, algoHnd):
		dat=testutil.readcsv(datfile)
		prm=testutil.readparams(prmfile)

		sett=json.loads( "".join((open('../.settings', 'r').readlines())) )[algoHnd.__name__]

		dt=int(1e6/dat[0])

		testobj=algoHnd(
							dat[1], 
							dat[0],
							eventstart=int(prm['tau1']/dt),			# event start point
							eventend=int(prm['tau2']/dt),    		# event end point
							baselinestats=[ 1.0, 0.01, 0.0 ],
							algosettingsdict=sett,
							savets=0
						)
		testobj.processEvent()

		self.assertEqual( testobj.mdProcessingStatus, 'normal' )
		self.assertEqual( round(testobj.mdBlockDepth,1), 1.0-abs(prm['a']) )
		self.assertEqual( round(testobj.mdResTime,1), (prm['tau2']-prm['tau1'])/1000. )


class PEGSRATests(PEGTestFunctions):
	def test_e1sra(self):
		self.runTestCase('testdata/test1.csv', 'testdata/test1.prm', sra.stepResponseAnalysis)

	def test_e2sra(self):
		self.runTestCase('testdata/test2.csv', 'testdata/test2.prm', sra.stepResponseAnalysis)

	def test_e3sra(self):
		self.runTestCase('testdata/test3.csv', 'testdata/test3.prm', sra.stepResponseAnalysis)

	def test_e4sra(self):
		self.runTestCase('testdata/test4.csv', 'testdata/test4.prm', sra.stepResponseAnalysis)

	def test_e5sra(self):
		self.runTestCase('testdata/test5.csv', 'testdata/test5.prm', sra.stepResponseAnalysis)

	def test_e6sra(self):
		self.runTestCase('testdata/test6.csv', 'testdata/test6.prm', sra.stepResponseAnalysis)

	def test_e7sra(self):
		self.runTestCase('testdata/test7.csv', 'testdata/test7.prm', sra.stepResponseAnalysis)

	def test_e8sra(self):
		self.runTestCase('testdata/test8.csv', 'testdata/test8.prm', sra.stepResponseAnalysis)

	def test_e9sra(self):
		self.runTestCase('testdata/test9.csv', 'testdata/test9.prm', sra.stepResponseAnalysis)

	def test_e10sra(self):
		self.runTestCase('testdata/test10.csv', 'testdata/test10.prm', sra.stepResponseAnalysis)

	def test_e11sra(self):
		self.runTestCase('testdata/test11.csv', 'testdata/test11.prm', sra.stepResponseAnalysis)

	def test_e12sra(self):
		self.runTestCase('testdata/test12.csv', 'testdata/test12.prm', sra.stepResponseAnalysis)

	def test_e13sra(self):
		self.runTestCase('testdata/test13.csv', 'testdata/test13.prm', sra.stepResponseAnalysis)
	
	def test_e14sra(self):
		self.runTestCase('testdata/test14.csv', 'testdata/test14.prm', sra.stepResponseAnalysis)

	def test_e15sra(self):
		self.runTestCase('testdata/test15.csv', 'testdata/test15.prm', sra.stepResponseAnalysis)

	def test_e16sra(self):
		self.runTestCase('testdata/test16.csv', 'testdata/test16.prm', sra.stepResponseAnalysis)

	def test_e17sra(self):
		self.runTestCase('testdata/test17.csv', 'testdata/test17.prm', sra.stepResponseAnalysis)

	def test_e18sra(self):
		self.runTestCase('testdata/test18.csv', 'testdata/test18.prm', sra.stepResponseAnalysis)

	def test_e19sra(self):
		self.runTestCase('testdata/test19.csv', 'testdata/test19.prm', sra.stepResponseAnalysis)

	def test_e20sra(self):
		self.runTestCase('testdata/test20.csv', 'testdata/test20.prm', sra.stepResponseAnalysis)

	def test_e21sra(self):
		self.runTestCase('testdata/test21.csv', 'testdata/test21.prm', sra.stepResponseAnalysis)

	def test_e22sra(self):
		self.runTestCase('testdata/test22.csv', 'testdata/test22.prm', sra.stepResponseAnalysis)

	def test_e23sra(self):
		self.runTestCase('testdata/test23.csv', 'testdata/test23.prm', sra.stepResponseAnalysis)

	def test_e24sra(self):
		self.runTestCase('testdata/test24.csv', 'testdata/test24.prm', sra.stepResponseAnalysis)

class PEGSSETests(PEGTestFunctions):
	def test_e1sse(self):
		self.runTestCase('testdata/test1.csv', 'testdata/test1.prm', sse.singleStepEvent)

	def test_e2sse(self):
		self.runTestCase('testdata/test2.csv', 'testdata/test2.prm', sse.singleStepEvent)

	def test_e3sse(self):
		self.runTestCase('testdata/test3.csv', 'testdata/test3.prm', sse.singleStepEvent)

	def test_e4sse(self):
		self.runTestCase('testdata/test4.csv', 'testdata/test4.prm', sse.singleStepEvent)

	def test_e5sse(self):
		self.runTestCase('testdata/test5.csv', 'testdata/test5.prm', sse.singleStepEvent)

	def test_e6sse(self):
		self.runTestCase('testdata/test6.csv', 'testdata/test6.prm', sse.singleStepEvent)

	def test_e7sse(self):
		self.runTestCase('testdata/test7.csv', 'testdata/test7.prm', sse.singleStepEvent)

	def test_e8sse(self):
		self.runTestCase('testdata/test8.csv', 'testdata/test8.prm', sse.singleStepEvent)

	def test_e9sse(self):
		self.runTestCase('testdata/test9.csv', 'testdata/test9.prm', sse.singleStepEvent)

	def test_e10sse(self):
		self.runTestCase('testdata/test10.csv', 'testdata/test10.prm', sse.singleStepEvent)

	def test_e11sse(self):
		self.runTestCase('testdata/test11.csv', 'testdata/test11.prm', sse.singleStepEvent)

	def test_e12sse(self):
		self.runTestCase('testdata/test12.csv', 'testdata/test12.prm', sse.singleStepEvent)

	def test_e13sse(self):
		self.runTestCase('testdata/test13.csv', 'testdata/test13.prm', sse.singleStepEvent)

	def test_e14sse(self):
		self.runTestCase('testdata/test14.csv', 'testdata/test14.prm', sse.singleStepEvent)

	def test_e15sse(self):
		self.runTestCase('testdata/test15.csv', 'testdata/test15.prm', sse.singleStepEvent)

	def test_e16sse(self):
		self.runTestCase('testdata/test16.csv', 'testdata/test16.prm', sse.singleStepEvent)
