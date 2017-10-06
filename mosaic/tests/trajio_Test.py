import mosaic.trajio.qdfTrajIO as qdfTrajIO
import mosaic.trajio.binTrajIO as binTrajIO
import mosaic.trajio.tsvTrajIO as tsvTrajIO
from mosaic.utilities.ionic_current_stats import OpenCurrentDist
import numpy as np

class TrajIOTest(object):
	_refcurrent=[135.99604311732614, 6.6679749349455024]
	_trajioHnd={
		'qdf' : ( qdfTrajIO.qdfTrajIO, {'filter' : 'SingleChan-0001.qdf', 'Rfb' : 9.1e9, 'Cfb' : 1.07e-12} ),
		'bin' : ( binTrajIO.binTrajIO, {
						"AmplifierScale": "1.0", 
						"AmplifierOffset": 0.0, 
						"SamplingFrequency": 500000,
						"HeaderOffset": 0,
						"ColumnTypes": "[('curr_pA', 'f8')]",
						"IonicCurrentColumn" : "curr_pA",
						"dcOffset": 0.0, 
						"filter": "SingleChan-0001_1.bin"
						} 
				),	
		'tsv' : ( tsvTrajIO.tsvTrajIO, {
				        "filter" :  "SingleChan-0001_1.tsv", 
				        "headers" : "False", 
				        "Fs" :	"500000",
				        "dcOffset" : 0.0, 
				        "start" : 0.0 
			    	}
			  	),
		'csv' : ( tsvTrajIO.tsvTrajIO, {
				        "filter" :  "SingleChan-0001_1.tsv", 
				        "headers" : "False", 
				        "Fs" :	"500000",
				        "dcOffset" : 0.0, 
				        "start" : 0.0 
			    	}
			  	)
	}

	def currentStats(self, curr):
		return OpenCurrentDist(curr, 0.5)

	def runTestCase(self, dattype, dirname):
		t=TrajIOTest._trajioHnd[dattype]
		q=t[0](dirname=dirname, **t[1])

		dat=q.popdata(100000)
		current=self.currentStats(dat)

		assert round(current[0],1)==round(TrajIOTest._refcurrent[0],1)
		assert round(current[1],1)==round(TrajIOTest._refcurrent[1],1)

class TrajIO_TestSuite(TrajIOTest):
	def test_trajio(self):
		for dat in ['qdf','bin', 'tsv', 'csv']:
			yield self.runTestCase, dat, 'testdata/'

if __name__ == '__main__':
	t=TrajIOTest()
	t.runTestCase('bin', 'mosaic/tests/testdata/')