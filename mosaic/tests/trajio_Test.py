import copy
from nose.tools import raises
from mosaic.utilities.resource_path import resource_path
import mosaic.trajio.metaTrajIO as metaTrajIO
import mosaic.trajio.qdfTrajIO as qdfTrajIO
import mosaic.trajio.binTrajIO as binTrajIO
import mosaic.trajio.tsvTrajIO as tsvTrajIO
import mosaic.trajio.chimeraTrajIO as chimeraTrajIO
import mosaic.filters.besselLowpassFilter as besselLowpassFilter
from mosaic.utilities.ionic_current_stats import OpenCurrentDist
import numpy as np

class TrajIOTest(object):
	_refcurrent=[135.99604311732614, 6.6679749349455024]
	_trajioHnd={
		'qdf' : ( qdfTrajIO.qdfTrajIO, {
						'filter' : 'SingleChan-0001.qdf', 
						'Rfb' : 9.1e9, 
						'Cfb' : 1.07e-12
					} ),
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
			  	),
		'chi' :	( chimeraTrajIO.chimeraTrajIO, {
						"filter": "Chimera.log", 
						"start": 0.0,
						"HeaderOffset": 0
					}
				)
	}

	def currentStats(self, curr):
		return OpenCurrentDist(curr, 0.5)

	def runTestCase(self, dattype, dirname):
		print(dattype, dirname)
		t=TrajIOTest._trajioHnd[dattype]
		q=t[0](dirname=dirname, **t[1])

		dat=q.popdata(100000)
		print(dat)
		current=self.currentStats(dat)
		q._formatsettings()

		print( current, TrajIOTest._refcurrent )
		assert round(current[0],1)==round(TrajIOTest._refcurrent[0],1)
		assert round(current[1],1)==round(TrajIOTest._refcurrent[1],1)

	def runTestCaseChimera(self, dattype, dirname):
		t=TrajIOTest._trajioHnd[dattype]
		q=t[0](dirname=dirname, **t[1])

		dat=q.popdata(100000)
		current=self.currentStats(dat)
		q._formatsettings()

		assert len(dat)==100000

	@raises(metaTrajIO.InsufficientArgumentsError, KeyError)
	def runSettingsErrorTestCase(self,dattype, dirname, setting):
		t=copy.deepcopy(TrajIOTest._trajioHnd[dattype])

		t[1].pop(setting)

		t[0](dirname=dirname, **t[1])

	@raises(metaTrajIO.InsufficientArgumentsError, metaTrajIO.IncompatibleArgumentsError, metaTrajIO.FileNotFoundError)
	def runSetupErrorTestCase(self, dattype, sdict):
		t=copy.deepcopy(TrajIOTest._trajioHnd[dattype])

		print(sdict)
		t[0](**sdict)

	def runSetupTestCase(self, dattype, sdict):
		t=copy.deepcopy(TrajIOTest._trajioHnd[dattype])

		for k in list(sdict.keys()):
			t[1][k]=sdict[k]

		t[0](**t[1])

	def runBINErrorTestCase(self, dirname, setting):
		self.runSettingsErrorTestCase('bin', dirname, setting)

	def runBINSettingsTestCase(self, dirname, setting, val):
		t=copy.deepcopy(TrajIOTest._trajioHnd['bin'])

		t[1].pop(setting)

		q=t[0](dirname=dirname, **t[1])

		assert getattr(q, setting)==val

	def runQDFErrorTestCase(self, dirname, setting):
		self.runSettingsErrorTestCase('qdf', dirname, setting)

	def runQDFCurrentTestCase(self, dirname):
		t=TrajIOTest._trajioHnd['qdf']

		d=copy.deepcopy(t[1])
		d['format']='i'
	
		q=t[0](dirname=dirname, **d)

		dat=q.popdata(100000)

		assert len(dat)>0

	def runCHIErrorTestCase(self, dirname, setting):
		self.runSettingsErrorTestCase('chi', dirname, setting)

	@raises(IndexError)
	def runTSVCurrentTestCase(self, dirname):
		t=TrajIOTest._trajioHnd['tsv']

		d=copy.deepcopy(t[1])
		d.pop("Fs")
	
		q=t[0](dirname=dirname, **d)

		dat=q.popdata(1000)

	def runFuncTestCase(self, dattype, sdict, funcname, args, kwargs):
		t=copy.deepcopy(TrajIOTest._trajioHnd[dattype])

		for k in list(sdict.keys()):
			t[1][k]=sdict[k]

		d=t[0](**t[1])
		getattr(d, funcname)(*args, **kwargs)

	def runPropTestCase(self, dattype, sdict, propname):
		t=copy.deepcopy(TrajIOTest._trajioHnd[dattype])

		for k in list(sdict.keys()):
			t[1][k]=sdict[k]

		d=t[0](**t[1])
		
		print(propname, "=", getattr(d, propname))
		assert len(str(getattr(d, propname))) > 0

class TrajIO_TestSuite(TrajIOTest):
	def test_trajio(self):
		for dat in ['qdf','bin', 'tsv', 'csv']:
			yield self.runTestCase, dat, 'mosaic/tests/testdata/'

	def test_trajiochimera(self):
		yield self.runTestCaseChimera, 'chi', 'mosaic/tests/testdata/'

	def test_chiErrorTest(self):
		for k in ["SamplingFrequency", "ColumnTypes", "IonicCurrentColumn", "TIAgain", "preADCgain", "mVoffset", "pAoffset", "ADCvref", "ADCbits"]:
			yield self.runCHIErrorTestCase, 'mosaic/tests/testdata/', k

	def test_binErrorTest(self):
		for k in ["SamplingFrequency", "ColumnTypes", "IonicCurrentColumn"]:
			yield self.runBINErrorTestCase, 'mosaic/tests/testdata/', k

	def test_binSettingsTest(self):
		for k in [("HeaderOffset", 0), ("AmplifierScale",1), ("AmplifierOffset",0)]:
			yield self.runBINSettingsTestCase, 'mosaic/tests/testdata/', k[0], k[1]

	def test_qdfErrorTest(self):
		for k in ["Rfb", "Rfb"]:
			yield self.runQDFErrorTestCase, 'mosaic/tests/testdata/', k

	def test_qdfCurrentTest(self):
		yield self.runQDFCurrentTestCase, 'mosaic/tests/testdata/'

	def test_tsvSettingsTest(self):
		yield self.runTSVCurrentTestCase, 'mosaic/tests/testdata/'

	def test_trajioSetupErrorTest(self):
		for sett in [
					{"dirname": "mosaic/tests/testdata/", "fnames" : resource_path("SingleChan-0001.qdf")},
					{"dirname": "mosaic/tests/testdata/", "nfiles" : 1},
					{"dirname": "mosaic/tests/testdata/", "filter" : "*.xyz"},
					{}
				]:
			yield self.runSetupErrorTestCase, "qdf", sett	

	def test_trajioSetupTest(self):
		for sett in [
					{"dirname": "mosaic/tests/testdata/", "datafilter" : besselLowpassFilter.besselLowpassFilter}
				]:
			yield self.runSetupTestCase, "qdf", sett

	def test_trajioFuncTest(self):
		for n in [10, 1000, 100000, 1000000]:
			yield self.runFuncTestCase, "qdf", {"dirname": "mosaic/tests/testdata/"}, "previewdata", [n], {}

	def test_trajioPropTest(self):
		for prop in ["FsHz", "ElapsedTimeSeconds", "LastFileProcessed", "ProcessedFiles", "DataLengthSec"]:
			yield self.runPropTestCase, "qdf", {"dirname": "mosaic/tests/testdata/"}, prop

if __name__ == '__main__':
	t=TrajIOTest()
	t.runTestCase('bin', 'mosaic/tests/testdata/')
	t.runTestCaseChimera('chi', 'mosaic/tests/testdata/')