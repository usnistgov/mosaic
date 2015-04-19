"""
	Graphical User Interface for Mosaic written in Python and Qt4. 

	Usage from project root: python mosaicgui/mosaicGUI.py

	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
"""	
import sys
import time
import string
import glob
import multiprocessing
from  mosaic.utilities.resource_path import format_path
from sqlite3 import DatabaseError

from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4 import QtGui

import mosaicgui.settingsview
import mosaicgui.analysisWorker as analysisworker

from mosaic.metaTrajIO import FileNotFoundError

class qtAnalysisGUI(mosaicgui.settingsview.settingsview):
	def __init__(self, parent = None):
		super(qtAnalysisGUI, self).__init__(parent)

		self.nDBFiles=0
		self.startButtonClicked=False

		self.idleTimer=QtCore.QTimer()

		self.aWorker=None
		self.aThread=None


		self.idleTimer.start(5000)

		# Start Analysis Signals
		QtCore.QObject.connect(self.startAnalysisPushButton, QtCore.SIGNAL('clicked()'), self.OnStartAnalysis)
		QtCore.QObject.connect(self.actionStart_Analysis, QtCore.SIGNAL('triggered()'), self.OnStartAnalysis)
		QtCore.QObject.connect(self.actionOpen_Analysis, QtCore.SIGNAL('triggered()'), self.OnLoadAnalysis)
		QtCore.QObject.connect(self.actionLoad_Data, QtCore.SIGNAL('triggered()'), self.OnSelectPath)
		QtCore.QObject.connect(self.actionSave_Settings, QtCore.SIGNAL('triggered()'), self.OnSaveSettings)
		QtCore.QObject.connect(self.actionSave_Histogram, QtCore.SIGNAL('triggered()'), self.OnSaveHistogram)
		QtCore.QObject.connect(self.actionAbout_MOSAIC, QtCore.SIGNAL('triggered()'), self.OnAboutApp)
		
		
		
		# Idle processing
		QtCore.QObject.connect(self.idleTimer, QtCore.SIGNAL('timeout()'), self.OnAppIdle)

	def OnStartAnalysis(self):
		try:
			if not self.analysisRunning:
				if self.analysisDataModel["DataFilesPath"]:
					self._setEnableSettingsWidgets(False)
					self._setEnableDataSettingsWidgets(False)

					if self.dataFilterDenoise:
						fltr=self.analysisDataModel["FilterAlgorithm"]
					else:
						fltr=None

					with open(self.analysisDataModel["DataFilesPath"]+"/.settings", 'w') as f:
						f.write(
							self.analysisDataModel.GenerateSettingsView(
								eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
								eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText()),
								dataFilterAlgo=fltr
							)
						)

					self.startAnalysisPushButton.setEnabled(False)
					self.actionStart_Analysis.setEnabled(False)

					self.startAnalysisPushButton.setStyleSheet("")
					self.startAnalysisPushButton.setText("Starting...")
					self.actionStart_Analysis.setText("Starting...")

					self.trajViewerWindow.hide()

					# Query the number of database files in the analysis directory
					self.nDBFiles=len(self._getdbfiles())	

					# setup the worker thread
					self.aThread=QtCore.QThread(parent=self)
					self.aWorker=analysisworker.analysisWorker(
						self.analysisDataModel.GenerateAnalysisObject(
								eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
								eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText()),
								dataFilterAlgo=fltr
							)
						)
					self.aWorker.moveToThread(self.aThread)

					self.aWorker.analysisFinished.connect(self.OnAnalysisFinished)
					
					# Handle the threads finished signal
					# self.aThread.finished.connect(self.OnThreadFinished)
					# self.aThread.finished.connect(self.aThread.quit)

					self.aThread.start()

					# Start the analysis
					QtCore.QMetaObject.invokeMethod(self.aWorker, 'startAnalysis', Qt.QueuedConnection)

					self.startButtonClicked=True	
			else:
				# Stop the analysis
				QtCore.QMetaObject.invokeMethod(self.aWorker, 'stopAnalysis', Qt.QueuedConnection)

				self.startAnalysisPushButton.setEnabled(False)
				self.actionStart_Analysis.setEnabled(False)
				# self._setEnableSettingsWidgets(True)
				# self._setEnableDataSettingsWidgets(True)

				self.startAnalysisPushButton.setStyleSheet("")
				self.startAnalysisPushButton.setText("Stopping...")
				self.actionStart_Analysis.setText("Stopping...")

				# self.analysisRunning=False
		except FileNotFoundError:
			QtGui.QMessageBox.warning(self, "Data Error", "No data files found in " + str(self.analysisDataModel["DataFilesPath"]) )

			self._setEnableSettingsWidgets(True)
			self._setEnableDataSettingsWidgets(True)

			self.startAnalysisPushButton.setStyleSheet("")
			self.startAnalysisPushButton.setText("Start Analysis")
			self.actionStart_Analysis.setText("Start Analysis")

	def OnSaveSettings(self):
		if not self.analysisRunning:
			if self.analysisDataModel["DataFilesPath"]:
				
				if self.dataFilterDenoise:
					fltr=self.analysisDataModel["FilterAlgorithm"]
				else:
					fltr=None

				with open(self.analysisDataModel["DataFilesPath"]+"/.settings", 'w') as f:
					f.write(
						self.analysisDataModel.GenerateSettingsView(
							eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
							eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText()),
							dataFilterAlgo=fltr
						)
					)
				# QtGui.QMessageBox.information(self, "Settings Saved", "Settings file "+self.analysisDataModel["DataFilesPath"]+"/.settings saved.")
				QtGui.QMessageBox.information(self, "Settings Saved", "Settings file saved.")

	def OnSaveHistogram(self):
		if self.blockDepthWindow:
			self.blockDepthWindow.saveHistogram(self.analysisDataModel["DataFilesPath"])


	def OnAnalysisFinished(self, value=True):
		if value:
			self._setEnableSettingsWidgets(True)
			self._setEnableDataSettingsWidgets(True)

			self.startAnalysisPushButton.setStyleSheet("")
			self.startAnalysisPushButton.setText("Start Analysis")
			self.actionStart_Analysis.setText("Start Analysis")

			self.startAnalysisPushButton.setEnabled(True)
			self.actionStart_Analysis.setEnabled(True)

			self.analysisRunning=False

			# Force an update of the console log
			self.consoleLog.Update()

			# reset the analysis workers
			del self.aWorker
			del self.aThread

	def OnLoadAnalysis(self):
		fd=QtGui.QFileDialog(parent=self, caption=QtCore.QString('Open Analysis Results'))
		
		if self.datPathLineEdit.text() != "":
			fd.setDirectory( self.datPathLineEdit.text() )

		fd.setNameFilters(['SQLite databases (*.sqlite)'])
		analysisfile=str(fd.getOpenFileName())

		# self.ShowTrajectory=False

		try:
			if analysisfile != "":
				analysisdir= '/'.join( (str(analysisfile).split('/'))[:-1] )
				
				# Load settings from the analysis directory
				self.datPathLineEdit.setText(analysisdir)
				self.OnDataPathChange(analysisfile)

				# Disable widgets
				self.trajViewerWindow.hide()
				# self._setEnableSettingsWidgets(False)
				# self._setEnableDataSettingsWidgets(False)
				
				# Load analysis
				if self.blockDepthWindow:
					self.blockDepthWindow.hide()
					del self.blockDepthWindow
					self.blockDepthWindow = mosaicgui.blockdepthview.blockdepthview.BlockDepthWindow(parent=self)
				if self.statisticsView:
					self.statisticsView.hide()
					del self.statisticsView
					self.statisticsView = mosaicgui.statisticsview.statisticsview.StatisticsWindow(parent=self)
				if self.fitEventsView:
					self.fitEventsView.hide()
					del self.fitEventsView
					self.fitEventsView = mosaicgui.fiteventsview.fiteventsview.FitEventWindow(parent=self)
			
				self.blockDepthWindow.openDBFile( analysisfile, updateOnIdle=False )
				self.blockDepthWindow.show()
				self.plotBlockDepthHistCheckBox.setChecked(True)
				
				self.statisticsView.openDBFile( analysisfile, updateOnIdle=False )
				self.statisticsView.show()

				self.fitEventsView.openDBFile( analysisfile, self.trajViewerWindow.FskHz, updateOnIdle=False )
				self.fitEventsView.show()
				self.plotEventFitsCheckBox.setChecked(True)

				# set data path in the console viewer
				self.consoleLog.openDBFile(analysisfile)

				# set data path in the processed files viewer
				self.processedFiles.openDBFile(analysisfile)

				# enable the path select button to allow a new alaysis to be started
				self.datPathLineEdit.setEnabled(True)
		except DatabaseError:
			QtGui.QMessageBox.warning(self, "File Error", analysisfile+" is not a valid sqlite database.")
			self._setEnableSettingsWidgets(False)
			self._setEnableDataSettingsWidgets(False)
			raise

		self.ShowTrajectory=True
		
	def OnAboutApp(self):
		self.aboutDialog.show()

	def _getdbfiles(self):
		path=self.analysisDataModel["DataFilesPath"]
		return glob.glob(format_path(path+'/*sqlite'))

	def _launchAnalysisWindows(self):
		self.blockDepthWindow.openDBFile( self.DataFile )
		if self.showBlockDepthWindow:	
			self.blockDepthWindow.show()
		self.statisticsView.openDBFile( self.DataFile )
		self.statisticsView.show()

		# set data path in the processed files viewer
		self.processedFiles.openDBFile( self.DataFile )

		self.fitEventsView.openDBFile( self.DataFile, self.trajViewerWindow.FskHz )
		if self.showFitEventsWindow:
			self.fitEventsView.show()

		self.consoleLog.openDBFile( self.DataFile )

		# self.startAnalysisPushButton.setStyleSheet('QPushButton {color: white; background-color: qlineargradient(spread:pad, x1:0, y1:1, x2:0, y2:0, stop:0 rgba(190, 49, 8), stop:1 rgba(255, 10, 4));}')
		self.startAnalysisPushButton.setStyleSheet('QPushButton {color: red;}')
		self.startAnalysisPushButton.setText("Stop Analysis")
		self.actionStart_Analysis.setText("Stop Analysis")

		self.startAnalysisPushButton.setEnabled(True)
		self.actionStart_Analysis.setEnabled(True)

		self.analysisRunning=True	

	def OnAppIdle(self):
		# QtGui.QApplication.processEvents()
		if not self.analysisRunning and self.startButtonClicked:
			dbfiles=self._getdbfiles()
			if len(dbfiles)>self.nDBFiles:
				self.DataFile=dbfiles[-1]
				self._launchAnalysisWindows()
				self.startButtonClicked=False
		# if self.aThread.isFinished() and self.analysisRunning:
		# 	print "finished"
		# 	self.OnAnalysisFinished(True)

	def OnQuit(self):
		if self.analysisRunning:
			self.OnStartAnalysis()
		self.statisticsView.closeDB()
		self.blockDepthWindow.closeDB()
		self.processedFiles.closeDB()

def main():
	app = QtGui.QApplication(sys.argv)
	dmw = qtAnalysisGUI()
	dmw.show()
	dmw.raise_()

	# cleanup processing
	app.connect(app, QtCore.SIGNAL("aboutToQuit()"), dmw.OnQuit)
	
	sys.exit(app.exec_())

if __name__ == '__main__':
	if sys.platform.startswith('win'):
		multiprocessing.freeze_support()
	main()

