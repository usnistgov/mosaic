import copy
import pytest
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
		# print(dat)
		current=self.currentStats(dat)
		q._formatsettings()

		# print( current, TrajIOTest._refcurrent )
		assert round(current[0],1)==round(TrajIOTest._refcurrent[0],1)
		assert round(current[1],1)==round(TrajIOTest._refcurrent[1],1)

	def runTestCaseChimera(self, dattype, dirname):
		t=TrajIOTest._trajioHnd[dattype]
		q=t[0](dirname=dirname, **t[1])

		dat=q.popdata(100000)
		current=self.currentStats(dat)
		q._formatsettings()

		assert len(dat)==100000

	def runSettingsErrorTestCase(self, dattype, dirname, setting):
		with pytest.raises( (metaTrajIO.InsufficientArgumentsError, KeyError) ):
			t=copy.deepcopy(TrajIOTest._trajioHnd[dattype])
			t[1].pop(setting)

			t[0](dirname=dirname, **t[1])

	def runSetupErrorTestCase(self, dattype, sdict):
		with pytest.raises( (metaTrajIO.InsufficientArgumentsError, metaTrajIO.IncompatibleArgumentsError, metaTrajIO.FileNotFoundError) ):
			t=copy.deepcopy(TrajIOTest._trajioHnd[dattype])

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

	def runTSVCurrentTestCase(self, dirname):
		with pytest.raises(IndexError):
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
		
		assert len(str(getattr(d, propname))) > 0

@pytest.fixture
def trajIOTestObject():
	return TrajIOTest()


def test_trajio(trajIOTestObject):
	for dat in ['qdf','bin', 'tsv', 'csv']:
		trajIOTestObject.runTestCase(dat, 'mosaic/tests/testdata/')

def test_trajiochimera(trajIOTestObject):
	trajIOTestObject.runTestCaseChimera('chi', 'mosaic/tests/testdata/')

def test_chiErrorTest(trajIOTestObject):
	for k in ["SamplingFrequency", "ColumnTypes", "IonicCurrentColumn", "TIAgain", "preADCgain", "mVoffset", "pAoffset", "ADCvref", "ADCbits"]:
		trajIOTestObject.runCHIErrorTestCase('mosaic/tests/testdata/', k)

def test_binErrorTest(trajIOTestObject):
	for k in ["SamplingFrequency", "ColumnTypes", "IonicCurrentColumn"]:
		trajIOTestObject.runBINErrorTestCase('mosaic/tests/testdata/', k)

def test_binSettingsTest(trajIOTestObject):
	for k in [("HeaderOffset", 0), ("AmplifierScale",1), ("AmplifierOffset",0)]:
		trajIOTestObject.runBINSettingsTestCase('mosaic/tests/testdata/', k[0], k[1])

def test_qdfErrorTest(trajIOTestObject):
	for k in ["Rfb", "Rfb"]:
		trajIOTestObject.runQDFErrorTestCase('mosaic/tests/testdata/', k)

def test_qdfCurrentTest(trajIOTestObject):
	trajIOTestObject.runQDFCurrentTestCase('mosaic/tests/testdata/')

def test_tsvSettingsTest(trajIOTestObject):
	trajIOTestObject.runTSVCurrentTestCase('mosaic/tests/testdata/')

def test_trajioSetupErrorTest(trajIOTestObject):
	for sett in [
				{"dirname": "mosaic/tests/testdata/", "fnames" : resource_path("SingleChan-0001.qdf")},
				{"dirname": "mosaic/tests/testdata/", "nfiles" : 1},
				{"dirname": "mosaic/tests/testdata/", "filter" : "*.xyz"},
				{}
			]:
		trajIOTestObject.runSetupErrorTestCase("qdf", sett)

def test_trajioSetupTest(trajIOTestObject):
	for sett in [
				{"dirname": "mosaic/tests/testdata/", "datafilter" : besselLowpassFilter.besselLowpassFilter}
			]:
		trajIOTestObject.runSetupTestCase("qdf", sett)

def test_trajioFuncTest(trajIOTestObject):
	for n in [10, 1000, 100000, 1000000]:
		trajIOTestObject.runFuncTestCase("qdf", {"dirname": "mosaic/tests/testdata/"}, "previewdata", [n], {})

def test_trajioPropTest(trajIOTestObject):
	for prop in ["FsHz", "ElapsedTimeSeconds", "LastFileProcessed", "ProcessedFiles", "DataLengthSec"]:
		trajIOTestObject.runPropTestCase("qdf", {"dirname": "mosaic/tests/testdata/"}, prop)
