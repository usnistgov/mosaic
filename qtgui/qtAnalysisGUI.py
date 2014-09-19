import sys
import time
import string
import glob
from sqlite3 import DatabaseError

from PyQt4 import QtCore
from PyQt4 import QtGui

import qtgui.settingsview

from pyeventanalysis.metaTrajIO import FileNotFoundError

class qtAnalysisGUI(qtgui.settingsview.settingsview):
	def __init__(self, parent = None):
		super(qtAnalysisGUI, self).__init__(parent)

		self.analysisObject=None
		self.nDBFiles=0
		self.startButtonClicked=False

		self.analysisThreadObj=analysisThread(None)
		self.idleTimer=QtCore.QTimer()

		self.idleTimer.start(5000)

		# Start Analysis Signals
		QtCore.QObject.connect(self.startAnalysisPushButton, QtCore.SIGNAL('clicked()'), self.OnStartAnalysis)
		QtCore.QObject.connect(self.actionStart_Analysis, QtCore.SIGNAL('triggered()'), self.OnStartAnalysis)
		QtCore.QObject.connect(self.actionOpen_Analysis, QtCore.SIGNAL('triggered()'), self.OnLoadAnalysis)
		QtCore.QObject.connect(self.actionLoad_Data, QtCore.SIGNAL('triggered()'), self.OnSelectPath)
		

		QtCore.QObject.connect(self.analysisThreadObj, QtCore.SIGNAL('finished(bool)'), self.OnAnalysisFinished)

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

					self.analysisObject=self.analysisDataModel.GenerateAnalysisObject(
						eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
						eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText()),
						dataFilterAlgo=fltr
					)

					self.analysisThreadObj=analysisThread( self.analysisObject, parent=self )
					self.analysisThreadObj.start()	

					self.nDBFiles=len(self._getdbfiles())	

					self.startButtonClicked=True	
			else:
				self.analysisObject.Stop()

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

	def OnAnalysisFinished(self, value):
		if value:
			self._setEnableSettingsWidgets(True)
			self._setEnableDataSettingsWidgets(True)

			self.startAnalysisPushButton.setStyleSheet("")
			self.startAnalysisPushButton.setText("Start Analysis")
			self.actionStart_Analysis.setText("Start Analysis")

			self.startAnalysisPushButton.setEnabled(True)
			self.actionStart_Analysis.setEnabled(True)

			self.analysisRunning=False

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
				self.OnDataPathChange()

				# Disable widgets
				self.trajViewerWindow.hide()
				self._setEnableSettingsWidgets(False)
				self._setEnableDataSettingsWidgets(False)
				
				# Load analysis
				if self.blockDepthWindow:
					del self.blockDepthWindow
					self.blockDepthWindow = qtgui.blockdepthview.blockdepthview.BlockDepthWindow(parent=self)
				if self.statisticsView:
					del self.statisticsView
					self.statisticsView = qtgui.statisticsview.statisticsview.StatisticsWindow(parent=self)
				if self.fitEventsView:
					del self.fitEventsView
					self.fitEventsView = qtgui.fiteventsview.fiteventsview.FitEventWindow(parent=self)
			
				self.blockDepthWindow.openDBFile( analysisfile )
				self.blockDepthWindow.show()
				
				self.statisticsView.openDBFile( analysisfile )
				self.statisticsView.show()

				self.fitEventsView.openDBFile( analysisfile, self.trajViewerWindow.FskHz )
				if self.showFitEventsWindow:
					self.fitEventsView.show()

				# enable the path select button to allow a new alaysis to be started
				self.datPathLineEdit.setEnabled(True)
		except DatabaseError:
			QtGui.QMessageBox.warning(self, "File Error", analysisfile+" is not a valid sqlite database.")
			self._setEnableSettingsWidgets(False)
			self._setEnableDataSettingsWidgets(False)

		self.ShowTrajectory=True
		
	def _getdbfiles(self):
		path=self.analysisDataModel["DataFilesPath"]
		return glob.glob(path+'/*sqlite')

	def _launchAnalysisWindows(self):
		self.blockDepthWindow.openDBFile( self.DataFile )
		if self.showBlockDepthWindow:	
			self.blockDepthWindow.show()
		self.statisticsView.openDBFile( self.DataFile )
		self.statisticsView.show()

		self.fitEventsView.openDBFile( self.DataFile, self.trajViewerWindow.FskHz )
		if self.showFitEventsWindow:
			self.fitEventsView.show()

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
		if self.analysisThreadObj.isFinished() and self.analysisRunning:
			# print "finished"
			self.OnAnalysisFinished(True)

	def OnQuit(self):
		if self.analysisRunning:
			self.OnStartAnalysis()
		self.statisticsView.closeDB()
		self.blockDepthWindow.closeDB()

class analysisThread(QtCore.QThread):
	def __init__(self, analysisObj, parent=None):
		super(analysisThread, self).__init__(parent)

		self.analysisObj=analysisObj

	def run(self):
		self.analysisObj.Run(forkProcess=True)
		self.analysisObj.subProc.join()
		self.exit()
		self.emit(QtCore.SIGNAL("finished(bool)"), True)
		# print "thread finished"


if __name__ == '__main__':
	# multiprocessing.freeze_support()
	
	app = QtGui.QApplication(sys.argv)
	dmw = qtAnalysisGUI()
	dmw.show()

	# cleanup processing
	app.connect(app, QtCore.SIGNAL("aboutToQuit()"), dmw.OnQuit)

	dmw.raise_()
	sys.exit(app.exec_())

