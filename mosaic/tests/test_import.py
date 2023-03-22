import pytest
import importlib
import mosaic.utilities.mosaicLogging as mlog 

class moduleImportTest(object):
	def __init__(self, modulename):
		self.modulename=modulename

	def testImport(self):
		log=mlog.mosaicLogging().getLogger(__name__)
		
		module=importlib.__import__(self.modulename)

		log.debug("import "+self.modulename)

		for submod in self.modulename.split('.')[1:]:
			module=getattr(module, submod)
			log.debug("import "+submod)

		return

@pytest.fixture
def moduleList(request):
	return moduleImportTest(request.param)

def modList():
	return (
		'mosaic',
		'mosaic._version', 
		'mosaic.apps.SingleChannelAnalysis',	
		'mosaic.apps.ConvertTrajIO', 
		'mosaic.settings',
		'mosaic.commonExceptions', 
		'mosaic.errors', 
		'mosaic.filters.metaIOFilter', 
		'mosaic.filters.besselLowpassFilter',	
		'mosaic.filters.convolutionFilter',
		'mosaic.filters.waveletDenoiseFilter',
		'mosaic.partition.metaEventPartition', 
		'mosaic.partition.eventSegment', 
		'mosaic.trajio.metaTrajIO', 
		'mosaic.trajio.qdfTrajIO', 
		'mosaic.trajio.tsvTrajIO',
		'mosaic.trajio.abfTrajIO', 
		'mosaic.trajio.binTrajIO', 
		'mosaic.process.metaEventProcessor', 
		'mosaic.process.cusumPlus', 
		'mosaic.process.adept', 
		'mosaic.process.adept2State',	
		'mosaic.mdio.metaMDIO', 		
		'mosaic.mdio.sqlite3MDIO',	
		# 'mosaic.zmqWorker',
		'mosaic.utilities.ionic_current_stats', 
		'mosaic.utilities.resource_path',
		'mosaic.utilities.analysis',
		'mosaic.utilities.mosaicLogFormat',
		'mosaic.utilities.sqlQuery',
		'mosaic.utilities.fit_funcs',
		'mosaic.utilities.mosaicTiming',
		'mosaic.utilities.util',
		'mosaic.utilities.mosaicLogging'
	)
	
@pytest.mark.parametrize(
	'moduleList', 
	modList(), 
	indirect=True)
def test_ImportModule(moduleList):
	assert moduleList.testImport() == None
