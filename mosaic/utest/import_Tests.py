class ModuleImportTest(object):
	def runTestCase(self, modulename):
		module=__import__(modulename)

		for submod in modulename.split('.')[1:]:
			module=getattr(module, submod)

		return
		
class ModuleImport_TestSuite(ModuleImportTest):
	def test_moduleImport(self):
		moduleList=[
		'mosaic',
		'mosaic.ConvertToCSV', 
		'mosaic.besselLowpassFilter',	
		'mosaic.metaEventPartition', 
		'mosaic.settings',
		'mosaic.SingleChannelAnalysis',	
		'mosaic.binTrajIO', 
		'mosaic.metaEventProcessor', 
		'mosaic.singleStepEvent', 
		'mosaic.commonExceptions', 
		'mosaic.metaIOFilter', 
		'mosaic.sqlite3MDIO',
		'mosaic._version', 
		'mosaic.convolutionFilter',
		'mosaic.metaMDIO', 
		'mosaic.tsvTrajIO',
		'mosaic.abfTrajIO', 
		'mosaic.cusumPlus', 
		'mosaic.metaTrajIO', 
		'mosaic.waveletDenoiseFilter',
		'mosaic.adept', 
		'mosaic.errors', 
		'mosaic.adept2State',
		'mosaic.eventSegment', 
		'mosaic.qdfTrajIO', 
		'mosaic.zmqWorker',
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
