""" 
	A class that defines the main mosaicGUI window.

	:Created:	4/22/2013
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
"""	
import sys
import os
import glob
import json
import types
import multiprocessing
import webbrowser

from PyQt4 import QtCore, QtGui, uic
from mosaic.utilities.resource_path import resource_path, format_path
import mosaicgui.EBSStateFileDict
import mosaicgui.trajview.trajview
import mosaicgui.advancedsettings.advancedsettings
import mosaicgui.blockdepthview.blockdepthview
import mosaicgui.statisticsview.statisticsview
import mosaicgui.consolelog.consolelog
import mosaicgui.fiteventsview.fiteventsview
import mosaicgui.csvexportview.csvexportview
import mosaicgui.aboutdialog.aboutdialog
import mosaicgui.datamodel
import mosaicgui.datapathedit

class settingsview(QtGui.QMainWindow):
	def __init__(self, parent = None):
		super(settingsview, self).__init__(parent)

		# uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"SettingsWindow.ui"), self)
		uic.loadUi(resource_path("SettingsWindow.ui"), self)
		
		# self.setupUi(self)

		self.setMenuBar(self.menubar)
		self._positionWindow()

		self.updateDialogs=False
		self.analysisRunning=False
		self.dataFilterDenoise=False

		# setup handles and data structs for other application windows
		self.trajViewerWindow = mosaicgui.trajview.trajview.TrajectoryWindow(parent=self)
		self.advancedSettingsDialog = mosaicgui.advancedsettings.advancedsettings.AdvancedSettingsDialog(parent=self)
		self.consoleLog = mosaicgui.consolelog.consolelog.AnalysisLogDialog(parent=self)
		self.blockDepthWindow = mosaicgui.blockdepthview.blockdepthview.BlockDepthWindow(parent=self)
		self.statisticsView = mosaicgui.statisticsview.statisticsview.StatisticsWindow(parent=self)
		self.fitEventsView = mosaicgui.fiteventsview.fiteventsview.FitEventWindow(parent=self)
		self.exportView = mosaicgui.csvexportview.csvexportview.CSVExportWindow(parent=self)
		self.aboutDialog = mosaicgui.aboutdialog.aboutdialog.AboutDialog(parent=self)
		

		self.showBlockDepthWindow=False
		self.showFitEventsWindow=False
		self.ShowTrajectory=True
		# redirect stdout and stderr
		# sys.stdout = redirectSTDOUT( edit=self.consoleLog.consoleLogTextEdit, out=sys.stdout, color=QtGui.QColor(0,0,0) )
		# sys.stderr = redirectSTDOUT( edit=self.consoleLog.consoleLogTextEdit, out=sys.stderr, color=QtGui.QColor(255,0,0) )
		# # Always show the console log
		# self.consoleLog.show()
		# self.consoleLog.raise_()

		# Setup and initialize the data model for the settings view
		self.analysisDataModel=mosaicgui.datamodel.guiDataModel()

		# temp keys
		self.analysisDataModel["lastMeanOpenCurr"]=-1.
		self.analysisDataModel["lastSDOpenCurr"]=-1.

		# default settings
		self._updateControls()

		# Setup validators
		self.startIndexLineEdit.setValidator( QtGui.QDoubleValidator(0, 999999,2, self) )
		self.endIndexLineEdit.setValidator( QtGui.QDoubleValidator(0, 999999,2, self) )

		# Set the default processing algorithm to stepResponse
		self.processingAlgorithmComboBox.setCurrentIndex( 0 )

		# Connect signals and slots

		# Data settings signals
		QtCore.QObject.connect(self.datPathToolButton, QtCore.SIGNAL('clicked()'), self.OnSelectPath)
		QtCore.QObject.connect(self.datPathLineEdit, QtCore.SIGNAL('editingFinished()'), self.OnDataPathChange)
		QtCore.QObject.connect(self.datTypeComboBox, QtCore.SIGNAL('currentIndexChanged(const QString &)'), self.OnDataTypeChange)
		QtCore.QObject.connect(self.dcOffsetDoubleSpinBox, QtCore.SIGNAL('valueChanged ( double )'), self.OnDataOffsetChange)
		QtCore.QObject.connect(self.startIndexLineEdit, QtCore.SIGNAL('editingFinished()'), self.OnDataStartIndexChange)
		QtCore.QObject.connect(self.endIndexLineEdit, QtCore.SIGNAL('textChanged ( const QString & )'), self.OnDataEndIndexChange)

		# Baseline detection signals
		QtCore.QObject.connect(self.baselineAutoCheckBox, QtCore.SIGNAL('clicked(bool)'), self.OnBaselineAutoCheckbox)
		QtCore.QObject.connect(self.baselineBlockSizeDoubleSpinBox, QtCore.SIGNAL('valueChanged ( double )'), self.OnBlockSizeChangeSpinbox)
		QtCore.QObject.connect(self.baselineMeanLineEdit, QtCore.SIGNAL('textChanged ( const QString & )'), self.OnBaselineMeanChange)
		QtCore.QObject.connect(self.baselineSDLineEdit, QtCore.SIGNAL('textChanged ( const QString & )'), self.OnBaselineSDChange)

		# Event partition signals
		QtCore.QObject.connect(self.ThresholdDoubleSpinBox, QtCore.SIGNAL('valueChanged ( double )'), self.OnThresholdChange)
		QtCore.QObject.connect(self.partitionThresholdHorizontalSlider, QtCore.SIGNAL('valueChanged ( int )'), self.OnThresholdChange)

		# Misc signals
		QtCore.QObject.connect(self.advancedModeCheckBox, QtCore.SIGNAL('clicked(bool)'), self.OnAdvancedMode)
		QtCore.QObject.connect(self.writeEventsCheckBox, QtCore.SIGNAL('clicked(bool)'), self.OnWriteEvents)
		QtCore.QObject.connect(self.parallelCheckBox, QtCore.SIGNAL('clicked(bool)'), self.OnParallelProcessing)
		QtCore.QObject.connect(self.parallelCoresSpinBox, QtCore.SIGNAL('valueChanged ( int )'), self.OnParallelProcessing)
		QtCore.QObject.connect(self.processingAlgorithmComboBox, QtCore.SIGNAL('currentIndexChanged(const QString &)'), self.OnProcessingAlgoChange)
		
		# Plots signals
		QtCore.QObject.connect(self.plotBlockDepthHistCheckBox, QtCore.SIGNAL('clicked(bool)'), self.OnPlotBlockDepth)
		QtCore.QObject.connect(self.plotEventFitsCheckBox, QtCore.SIGNAL('clicked(bool)'), self.OnPlotFitEvent)

		# View Menu signals
		QtCore.QObject.connect(self.actionAdvanced_Settings_Mode, QtCore.SIGNAL('triggered()'), self.OnAdvancedModeMenuAction)
		QtCore.QObject.connect(self.actionTrajectory_Viewer, QtCore.SIGNAL('triggered()'), self.OnShowTrajectoryViewer)
		QtCore.QObject.connect(self.actionBlockade_Depth_Histogram, QtCore.SIGNAL('triggered()'), self.OnShowBlockDepthViewer)
		QtCore.QObject.connect(self.actionEvent_Fits, QtCore.SIGNAL('triggered()'), self.OnShowFitEventsViewer)
		QtCore.QObject.connect(self.actionStatistics, QtCore.SIGNAL('triggered()'), self.OnShowStatisticsWindow)
		QtCore.QObject.connect(self.actionAnalysis_Log, QtCore.SIGNAL('triggered()'), self.OnShowConsoleLog)
		

		# Help Menu signals
		QtCore.QObject.connect(self.actionMOSAIC_Help, QtCore.SIGNAL('triggered()'), self.OnShowHelp)

		# Dialog signals and slots
		QtCore.QObject.connect(self.trajViewerWindow.waveletLevelSpinBox, QtCore.SIGNAL('valueChanged ( int )'), self.OnWaveletLevelChange)
		QtCore.QObject.connect(self.trajViewerWindow.denoiseCheckBox, QtCore.SIGNAL('clicked(bool)'), self.OnTrajDenoise)

		QtCore.QObject.connect(self.advancedSettingsDialog, QtCore.SIGNAL('rejected()'), self.OnAdvancedModeCancel)
		QtCore.QObject.connect(self.advancedSettingsDialog, QtCore.SIGNAL('accepted()'), self.OnAdvancedModeSave)	

		QtCore.QObject.connect(self.blockDepthWindow, QtCore.SIGNAL('rejected()'), self.OnBlockDepthWindowClose)


	def _positionWindow(self):
		""" 
			Position settings window at the top left corner
		"""
		screen = QtGui.QDesktopWidget().screenGeometry()
		# self.move( -screen.width()/2, -screen.height()/2 )
		self.move( screen.x(), screen.y() )

	def _updateControls(self):
		self.updateDialogs=False

		model=self.analysisDataModel

		datidx= { 
					"QDF" : self.datTypeComboBox.findText("QDF"), 
					"ABF" : self.datTypeComboBox.findText("ABF"),
					"BIN" : self.datTypeComboBox.findText("BIN"),
					"TSV" : self.datTypeComboBox.findText("TSV")
				}
		path=model["DataFilesPath"] 
		if len(glob.glob(format_path( str(path)+'/*qdf') )) > 0:
			self.datTypeComboBox.setCurrentIndex( datidx["QDF"] )
			model["filter"]="*.qdf"
		elif len(glob.glob( format_path(str(path)+'/*abf') )) > 0:
			self.datTypeComboBox.setCurrentIndex( datidx["ABF"] )
			model["filter"]="*.abf"
		elif len(glob.glob( format_path(str(path)+'/*bin') )) > 0:
			self.datTypeComboBox.setCurrentIndex( datidx["BIN"] )
			model["filter"]="*.bin"
		elif len(glob.glob( format_path(str(path)+'/*dat') )) > 0:
			self.datTypeComboBox.setCurrentIndex( datidx["BIN"] )
			model["filter"]="*.dat"
		elif len(glob.glob( format_path(str(path)+'/*tsv') )) > 0:
			self.datTypeComboBox.setCurrentIndex( datidx["TSV"] )
			model["filter"]="*.tsv"
		elif len(glob.glob( format_path(str(path)+'/*txt') )) > 0:
			self.datTypeComboBox.setCurrentIndex( datidx["TSV"] )
			model["filter"]="*.txt"

		# store the  data type in the trajviewer data struct
		model["DataFilesType"] = str(self.datTypeComboBox.currentText())

		self.startIndexLineEdit.setText(str(model["start"]))
		if model["end"]==-1:
			self.endIndexLineEdit.setText("")
		else:
			self.endIndexLineEdit.setText(str(model["end"]))

		self.dcOffsetDoubleSpinBox.setValue(model["dcOffset"])

		if float(model["meanOpenCurr"]) == -1. or float(model["sdOpenCurr"]) == -1.:
			self.baselineAutoCheckBox.setChecked(True)
			self.OnBaselineAutoCheckbox(True)

			# Manually disable baseline mean and SD controls
			self.baselineMeanLineEdit.setText("")
			self.baselineSDLineEdit.setText("")

			self.baselineMeanLineEdit.setPlaceholderText("<auto>")
			self.baselineSDLineEdit.setPlaceholderText("<auto>")

			self.baselineMeanLineEdit.setEnabled(False)
			self.baselineSDLineEdit.setEnabled(False)			
		else:
			# Populate baseline parameters
			self.baselineAutoCheckBox.setChecked(False)
			self.OnBaselineAutoCheckbox(False)

			self.baselineMeanLineEdit.setText(str(model["meanOpenCurr"]))
			self.baselineSDLineEdit.setText(str(model["sdOpenCurr"]))
			self.baselineBlockSizeDoubleSpinBox.setValue(float(model["blockSizeSec"]))

			# Manually enable baseline mean and SD controls
			self.baselineMeanLineEdit.setEnabled(True)
			self.baselineSDLineEdit.setEnabled(True)
	
		# Populate EventSegment parameters
		self._setThreshold(float(model["meanOpenCurr"]), float(model["sdOpenCurr"]), float(model["eventThreshold"]))
		
		# Populate misc parameters
		self.writeEventsCheckBox.setChecked(int(model["writeEventTS"]))

		# Populate plot widgets
		self.plotEventFitsCheckBox.setEnabled(int(model["writeEventTS"]))

		# check if parallel is available
		# try:
		# 	import zmq
			
		# 	self.parallelCheckBox.setChecked(int(model["parallelProc"]))				
		# 	self.parallelCoresSpinBox.setValue(multiprocessing.cpu_count()-int(model["reserveNCPU"]))
		# except ImportError:
		# 	self.parallelCheckBox.hide()
		# 	self.parallelCoresSpinBox.hide()
		# 	self.parallelCoresLabel.hide()
		self.parallelCheckBox.hide()
		self.parallelCoresSpinBox.hide()
		self.parallelCoresLabel.hide()	

		procidx= {}
		for v in self.analysisDataModel.eventProcessingAlgoKeys.keys():
			procidx[v]=self.processingAlgorithmComboBox.findText(v)
		
		self.processingAlgorithmComboBox.setCurrentIndex( procidx[self.analysisDataModel.EventProcessingAlgorithmLabel()] )

		# If an advanced mode dialog exists, update its settings
		if self.advancedSettingsDialog:
			if self.dataFilterDenoise:
				fltr=self.analysisDataModel["FilterAlgorithm"]
			else:
				fltr=None
			self.advancedSettingsDialog.updateSettingsString(
					model.GenerateSettingsView(
							eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
							eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText()),
							dataFilterAlgo=fltr
						)
				)

		# If the trajviewer is initialized, update the denoising settings
		if self.trajViewerWindow:
			self.trajViewerWindow.waveletLevelSpinBox.setValue(int(self.analysisDataModel["level"]))

		# Hide Rfb and Cfb for QDF files
		[control.hide() for control in [self.RfbLabel, self.qdfRfbLineEdit, self.RfbUnitsLabel, self.CfbLabel, self.qdfCfbLineEdit, self.CfbUnitsLabel]]

		self.updateDialogs=True

	def _loadEBSState(self):
		path=self.analysisDataModel["DataFilesPath"] 

		if path:
			ebsFile=glob.glob(format_path(str(path)+'/*_?tate.txt'))

			if len(ebsFile) > 0:
				ebsState=mosaicgui.EBSStateFileDict.EBSStateFileDict(ebsFile[0])
				
				rfb=ebsState.pop('FB Resistance',1.0)
				cfb=ebsState.pop('FB Capacitance',1.0)

				self.qdfRfbLineEdit.setText( str(float(rfb)/1E9) )
				self.qdfCfbLineEdit.setText( str(float(cfb)/1E-12) )

				# More Traj viewer settings
				self.analysisDataModel["Rfb"]=rfb
				self.analysisDataModel["Cfb"]=cfb

				# Show QDF specific widgets
				# self.qdfCfbLineEdit.show()				
				# self.qdfRfbLineEdit.show()
				# self.CfbLabel.show()
				# self.RfbLabel.show()
				# self.CfbUnitsLabel.show()
				# self.RfbUnitsLabel.show()
			# else:
				# Hide QDF specific widgets
				# self.qdfCfbLineEdit.hide()				
				# self.qdfRfbLineEdit.hide()
				# self.CfbLabel.hide()
				# self.RfbLabel.hide()
				# self.CfbUnitsLabel.hide()
				# self.RfbUnitsLabel.hide()


	def _setThreshold(self, mean, sd, threshold):
		self.updateDialogs=True
		if self.baselineAutoCheckBox.isChecked():
			try:
				mu=self.trajViewerWindow.meanCurr
				sig=self.trajViewerWindow.sdCurr
			except AttributeError:
				mu=self.analysisDataModel["lastMeanOpenCurr"]
				sig=self.analysisDataModel["lastSDOpenCurr"]
			self.ThresholdDoubleSpinBox.setMaximum(max(0,mu))
			self.ThresholdDoubleSpinBox.setValue(mu-sig*threshold)
		else:
			self.updateDialogs=False
			self.ThresholdDoubleSpinBox.setValue(mean-sd*threshold)
			self.updateDialogs=True
			self.OnThresholdChange(float(mean-sd*threshold))
			self.ThresholdDoubleSpinBox.setMaximum(mean)
			
		self.updateDialogs=False

	def _setEnableSettingsWidgets(self, state):
		self.baselineGroupBox.setEnabled(state)
		self.eventPartitionGroupBox.setEnabled(state)
		self.writeEventsCheckBox.setEnabled(state)
		self.parallelCheckBox.setEnabled(state)
		self.parallelCoresSpinBox.setEnabled(state)
		self.processingAlgorithmComboBox.setEnabled(state)
		self.advancedModeCheckBox.setEnabled(state)

	def _setEnableDataSettingsWidgets(self, state):
		self.processingAlgorithmComboBox.setEnabled(state)
		self.dataSettingsGroupBox.setEnabled(state)

	def _baselineupdate(self, value):
		if not self.baselineAutoCheckBox.isChecked():
			if value=="meanOpenCurr":
				control=self.baselineMeanLineEdit
			else:
				control=self.baselineSDLineEdit

			try:
				self.analysisDataModel[value] = float(control.text())
				self.analysisDataModel["eventThresholdpA"]=float(self.ThresholdDoubleSpinBox.value())
				self.analysisDataModel["slopeOpenCurr"]=0.0
			except:
				self.analysisDataModel[value]=-1
				self.analysisDataModel["eventThresholdpA"]=float(self.ThresholdDoubleSpinBox.value())
				self.analysisDataModel["slopeOpenCurr"]=-1

			self.analysisDataModel["blockSizeSec"]=float(self.baselineBlockSizeDoubleSpinBox.value())

			self._trajviewerdata()
		

	def _trajviewerdata(self):
		if self.dataFilterDenoise:
			fltr=self.analysisDataModel.GenerateDataFilesObject(dataFilterAlgo=self.analysisDataModel["FilterAlgorithm"])
		else:
			fltr=None

		self.trajViewerWindow.setTrajdata(
				self.analysisDataModel.GenerateTrajView(),
				fltr
			)
	# SLOTS

	# Data settings SLOTS
	def OnSelectPath(self):
		""" 
			Select the data directory. Once a folder is selected, 
			call additional functions to read in settings if they exist.
		"""
		fd=QtGui.QFileDialog()
		
		if self.datPathLineEdit.text() != "":
			fd.setDirectory( self.datPathLineEdit.text() )

		path=fd.getExistingDirectory()
		if path:
			self.datPathLineEdit.setText(path)
			self.OnDataPathChange()

	def OnDataPathChange(self, dbfile=None):
		if self.updateDialogs:
			self.analysisDataModel["DataFilesPath"]=str(self.datPathLineEdit.text())
			self.analysisDataModel.UpdateDataModelFromSettings(dbfile)

			self._loadEBSState()
			self._updateControls()
			if self.ShowTrajectory:
				self._trajviewerdata()
				self.trajViewerWindow.refreshPlot()
				self.blockDepthWindow.hide()
				self.trajViewerWindow.show()
			self.analysisDataModel["eventThresholdpA"]=self.trajViewerWindow.thrCurr
			self._updateControls()


	def OnDataTypeChange(self, item):
		if self.updateDialogs:
			if str(item) == "QDF":
				self.qdfRfbLineEdit.setEnabled(True)
				self.qdfCfbLineEdit.setEnabled(True)

				# If the data type was changed reload the EBS state
				self._loadEBSState()
			else:
				self.qdfRfbLineEdit.setEnabled(False)
				self.qdfCfbLineEdit.setEnabled(False)

			self.analysisDataModel["DataFilesType"]=str(item)

			self._trajviewerdata()
			self.trajViewerWindow.refreshPlot()


	def OnDataOffsetChange(self, item):
		if self.updateDialogs:
			self.analysisDataModel["dcOffset"]=item

			# print self.analysisDataModel["dcOffset"]
			# self.trajViewerWindow.updatePlot(self.analysisDataModel.GenerateTrajView())
			self._trajviewerdata()
			self.trajViewerWindow.refreshPlot()

	def OnDataStartIndexChange(self):
		text=str(self.startIndexLineEdit.text())
		if self.updateDialogs:
			if text:
				self.analysisDataModel["start"]=text
			else:
				self.analysisDataModel["start"]=0

			# Refresh the trajviewer when a new start value is specified.
			self._trajviewerdata()
			self.trajViewerWindow.refreshPlot()
			
	def OnDataEndIndexChange(self, text):
		# text=str(self.endIndexLineEdit.text())
		if self.updateDialogs:
			if text:
				self.analysisDataModel["end"]=float(text)
			else:
				self.analysisDataModel["end"]=-1

			# Refresh the trajviewer when a new end value is specified.
			self._trajviewerdata()
			self.trajViewerWindow.refreshPlot()

	# Baseline detection SLOTS
	def OnBaselineAutoCheckbox(self, value):
		if self.updateDialogs:
			if value:
				self.analysisDataModel["lastMeanOpenCurr"]=self.baselineMeanLineEdit.text()
				self.analysisDataModel["lastSDOpenCurr"]=self.baselineSDLineEdit.text()


				self.baselineMeanLineEdit.setText("")
				self.baselineSDLineEdit.setText("")

				self.baselineMeanLineEdit.setPlaceholderText("<auto>")
				self.baselineSDLineEdit.setPlaceholderText("<auto>")

				self.analysisDataModel["meanOpenCurr"]=-1
				self.analysisDataModel["sdOpenCurr"]=-1
				self.analysisDataModel["slopeOpenCurr"]=-1

				self.baselineMeanLineEdit.setEnabled(False)
				self.baselineSDLineEdit.setEnabled(False)

				self.analysisDataModel["blockSizeSec"]=float(self.baselineBlockSizeDoubleSpinBox.value())
			else:
				self.baselineMeanLineEdit.setPlaceholderText("")
				self.baselineSDLineEdit.setPlaceholderText("")

				self.updateDialogs=False
				self.analysisDataModel["slopeOpenCurr"]=0.0
				
				if float(self.analysisDataModel["lastMeanOpenCurr"])==-1. or float(self.analysisDataModel["lastSDOpenCurr"])==-1.:
					self.analysisDataModel["meanOpenCurr"]=self.trajViewerWindow.meanCurr
					self.analysisDataModel["sdOpenCurr"]=self.trajViewerWindow.sdCurr
					self.analysisDataModel["eventThresholdpA"]=self.ThresholdDoubleSpinBox.value()

					self.baselineMeanLineEdit.setText(str(round(self.trajViewerWindow.meanCurr,1)))
					self.baselineSDLineEdit.setText(str(round(self.trajViewerWindow.sdCurr,1)))
				else:
					self.analysisDataModel["meanOpenCurr"]=self.analysisDataModel["lastMeanOpenCurr"]
					self.analysisDataModel["sdOpenCurr"]=self.analysisDataModel["lastSDOpenCurr"]

					self.baselineMeanLineEdit.setText(str(self.analysisDataModel["lastMeanOpenCurr"]))
					self.baselineSDLineEdit.setText(str(self.analysisDataModel["lastSDOpenCurr"]))
				self.updateDialogs=True

				self.baselineMeanLineEdit.setEnabled(True)
				self.baselineSDLineEdit.setEnabled(True)

			# Update trajviewer
			self.trajViewerWindow.updatePlot(self.analysisDataModel.GenerateTrajView())


	def OnBlockSizeChangeSpinbox(self, value):
		if self.updateDialogs:
			self.analysisDataModel["blockSizeSec"]=float(value)
			self._trajviewerdata()
			self.trajViewerWindow.refreshPlot()

	def OnBaselineMeanChange(self, value):
		if self.updateDialogs:
			self._baselineupdate("meanOpenCurr")

			self.trajViewerWindow.updatePlot(self.analysisDataModel.GenerateTrajView())

	def OnBaselineSDChange(self, value):
		if self.updateDialogs:
			self._baselineupdate("sdOpenCurr")

			self.trajViewerWindow.updatePlot(self.analysisDataModel.GenerateTrajView())

	# Event partition SLOTS
	def OnThresholdChange(self, value):
		# print "value=", value, "type(value)=", type(value)
		if self.updateDialogs:
			[min,max]=[self.ThresholdDoubleSpinBox.minimum(), self.ThresholdDoubleSpinBox.maximum()]
			[smin,smax]=[self.partitionThresholdHorizontalSlider.minimum(),self.partitionThresholdHorizontalSlider.maximum()]

			# The trajectory window needs the update threshold
			self.analysisDataModel["blockSizeSec"]=self.baselineBlockSizeDoubleSpinBox.value()

			if self.baselineAutoCheckBox.isChecked():
				mu=self.trajViewerWindow.meanCurr
				sigma=self.trajViewerWindow.sdCurr
			else:
				mu=self.analysisDataModel["meanOpenCurr"]
				sigma=self.analysisDataModel["sdOpenCurr"]

			if type(value)==types.FloatType:
				self.analysisDataModel["eventThreshold"]=(mu-value)/sigma
				self.analysisDataModel["eventThresholdpA"]=value
				self.updateDialogs=False
				self.partitionThresholdHorizontalSlider.setValue( (int(smax-smin)*value/float(max-min)) )
				self.ThresholdDoubleSpinBox.setMaximum( mu )
				self.updateDialogs=True
			else:
				v=float((int((max-min))*value/float(smax-smin)))
				self.analysisDataModel["eventThreshold"]=(mu-v)/sigma
				self.analysisDataModel["eventThresholdpA"]=v
				self.updateDialogs=False
				self.ThresholdDoubleSpinBox.setValue( (int((max-min))*value/float(smax-smin)) )
				self.ThresholdDoubleSpinBox.setMaximum( mu )
				self.updateDialogs=True

			self.trajViewerWindow.updatePlot(self.analysisDataModel.GenerateTrajView())

	# Misc SLOTS
	def OnWriteEvents(self, value):
		self.analysisDataModel["writeEventTS"]=int(value)

		self.plotEventFitsCheckBox.setEnabled(value)
		if not value:
			self.plotEventFitsCheckBox.setChecked(value)
			self.showFitEventsWindow=value


	def OnParallelProcessing(self, value):
		if self.parallelCheckBox.isChecked():
			self.analysisDataModel["parallelProc"]=1
		else:
			self.analysisDataModel["parallelProc"]=0

		self.analysisDataModel["reserveNCPU"]=multiprocessing.cpu_count()-int(self.parallelCoresSpinBox.value())

	def OnAdvancedMode(self, value):
		if value:
			if self.dataFilterDenoise:
				fltr=self.analysisDataModel["FilterAlgorithm"]
			else:
				fltr=None

			self.advancedSettingsDialog.updateSettingsString(
					self.analysisDataModel.GenerateSettingsView(
						eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
						eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText()),
						dataFilterAlgo=fltr
					)
				)
			self.advancedSettingsDialog.show()
			self._setEnableSettingsWidgets(False)
		else:
			self.advancedSettingsDialog.hide()
			self._setEnableSettingsWidgets(True)

	def OnProcessingAlgoChange(self, value):
		self.analysisDataModel["ProcessingAlgorithm"]=value

	# Plot SLOTS
	def OnPlotBlockDepth(self, value):
		self.showBlockDepthWindow=bool(value)
		if value:
			# if self.analysisRunning:
			self.blockDepthWindow.show()
		else:
			self.blockDepthWindow.hide()

	def OnPlotFitEvent(self, value):
		self.showFitEventsWindow=value
		if value:
			self.fitEventsView.show()
		else:
			self.fitEventsView.hide()


	# Menu SLOTs
	def OnAdvancedModeMenuAction(self):
		self.advancedModeCheckBox.setChecked(True)
		self.OnAdvancedMode(True)

	def OnShowStatisticsWindow(self):
		self.statisticsView.show()

	def OnShowConsoleLog(self):
		self.consoleLog.show()

	def OnShowHelp(self):
		webbrowser.open('http://usnistgov.github.io/mosaic/html/index.html', new=0, autoraise=True)

	# Dialog SLOTS
	def OnShowTrajectoryViewer(self):
		self.trajViewerWindow.show()

	def OnShowBlockDepthViewer(self):
		self.blockDepthWindow.show()
		self.plotBlockDepthHistCheckBox.setChecked(True)

	def OnShowFitEventsViewer(self):
		self.fitEventsView.show()
		self.plotEventFitsCheckBox.setChecked(True)

	def OnAdvancedModeCancel(self):
		if not self.analysisRunning:
			self.advancedModeCheckBox.setChecked(False)
			self._setEnableSettingsWidgets(True)

	def OnTrajDenoise(self, value):
		# If the checkbox was just checked, display a warning
		if self.trajViewerWindow.denoiseCheckBox.isChecked():
			if self.trajViewerWindow.DenoiseWarning():
				self.trajViewerWindow.denoiseCheckBox.setChecked(False)
				return

		self.dataFilterDenoise=value

		if value:
			self.analysisDataModel["FilterAlgorithm"]="waveletDenoiseFilter"

		with open(self.analysisDataModel["DataFilesPath"]+"/.settings", 'w') as f:
			f.write(
				self.analysisDataModel.GenerateSettingsView(
					eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
					eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText()),
					dataFilterAlgo=self.analysisDataModel["FilterAlgorithm"]
				)
			)
			
		self._trajviewerdata()
		self.trajViewerWindow.refreshPlot()

	def OnWaveletLevelChange(self, value):
		self.analysisDataModel["level"]=value

		with open(self.analysisDataModel["DataFilesPath"]+"/.settings", 'w') as f:
			f.write(
				self.analysisDataModel.GenerateSettingsView(
					eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
					eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText()),
					dataFilterAlgo=self.analysisDataModel["FilterAlgorithm"]
				)
			)

		self._trajviewerdata()
		self.trajViewerWindow.refreshPlot()

	def OnBlockDepthWindowClose(self):
		self.plotBlockDepthHistCheckBox.setChecked(False)

	def OnAdvancedModeSave(self):
		updatesettings=self.analysisDataModel.UpdateDataModelFromSettingsString
		settingString=str(self.advancedSettingsDialog.advancedSettingsTextEdit.toPlainText())

		try:
			updatesettings(settingString)
		except ValueError, err:
			mb=QtGui.QMessageBox(self.advancedSettingsDialog)
			mb.setIcon(QtGui.QMessageBox.Critical)
			mb.setWindowTitle("Syntax Error")
			mb.setText("Syntax Error: "+str(err) )
			mb.exec_()
		
			self.advancedSettingsDialog.show()
			return
		finally:
			self._updateControls()
			
			# update trajviewer
			self._trajviewerdata()
			self.trajViewerWindow.refreshPlot()

			self.advancedModeCheckBox.setChecked(False)
			self._setEnableSettingsWidgets(True)


def main():
	app = QtGui.QApplication(sys.argv)
	dmw = settingsview()
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()

