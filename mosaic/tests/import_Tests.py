import mosaic.utilities.mosaicLogging as mlog 

class ModuleImportTest(object):
	log=mlog.mosaicLogging().getLogger(__name__)
	
	def runTestCase(self, modulename):
		module=__import__(modulename)

		ModuleImportTest.log.debug("import "+modulename)

		for submod in modulename.split('.')[1:]:
			module=getattr(module, submod)
			ModuleImportTest.log.debug("import "+submod)

		return
		
class ModuleImport_TestSuite(ModuleImportTest):
	def test_moduleImport(self):
		moduleList=[
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
		'mosaic.utilities.mosaicLogging',
		'mosaicgui',
		'mosaicgui.EBSStateFileDict',
		'mosaicgui.autocompleteedit',
		'mosaicgui.mosaicGUI',
		'mosaicgui.sqlQueryWorker',
		'mosaicgui.datamodel', 
		'mosaicgui.mplwidget',
		'mosaicgui.mosaicSyntaxHighlight',
		'mosaicgui.updateService',
		'mosaicgui.analysisWorker',
		'mosaicgui.datapathedit',
		'mosaicgui.settingsview',
		'mosaicgui.aboutdialog.aboutdialog',
		'mosaicgui.advancedsettings.advancedsettings',
		'mosaicgui.blockdepthview.blockdepthview',
		'mosaicgui.consolelog.consolelog',
		'mosaicgui.csvexportview.csvexportview',
		'mosaicgui.fiteventsview.fiteventsview',
		'mosaicgui.statisticsview.statisticsview',
		'mosaicgui.trajview.trajview'
		]

		for module in moduleList:
			yield self.runTestCase, module
