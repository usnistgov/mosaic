import sys
import time

from PyQt4 import QtCore
from PyQt4 import QtGui

import qtgui.settingsview

from pyeventanalysis.metaTrajIO import FileNotFoundError

class qtAnalysisGUI(qtgui.settingsview.settingsview):
	def __init__(self, parent = None):
		super(qtAnalysisGUI, self).__init__(parent)

		self.analysisObject=None

		self.analysisThreadObj=analysisThread(None)
		self.idleTimer=QtCore.QTimer()

		self.idleTimer.start(5000)

		# Start Analysis Signals
		QtCore.QObject.connect(self.startAnalysisPushButton, QtCore.SIGNAL('clicked()'), self.OnStartAnalysis)
		QtCore.QObject.connect(self.actionStart_Analysis, QtCore.SIGNAL('triggered()'), self.OnStartAnalysis)

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


					self.startAnalysisPushButton.setText("Stop Analysis")
					self.actionStart_Analysis.setText("Stop Analysis")

					self.trajViewerWindow.hide()

					self.analysisObject=self.analysisDataModel.GenerateAnalysisObject(
						eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
						eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText()),
						dataFilterAlgo=fltr
					)

					self.analysisThreadObj=analysisThread( self.analysisObject, parent=self )
					self.analysisThreadObj.start()
					
					time.sleep(5)

					self.blockDepthWindow.openDB( self.analysisObject.DataPath )
					if self.showBlockDepthWindow:	
						self.blockDepthWindow.show()
					self.statisticsView.openDB( self.analysisObject.DataPath )
					self.statisticsView.show()

					self.fitEventsView.openDB( self.analysisObject.DataPath, self.trajViewerWindow.FskHz )
					if self.showFitEventsWindow:
						self.fitEventsView.show()

					self.analysisRunning=True	
			else:
				self.analysisObject.Stop()

				self.startAnalysisPushButton.setEnabled(False)
				self.actionStart_Analysis.setEnabled(False)
				# self._setEnableSettingsWidgets(True)
				# self._setEnableDataSettingsWidgets(True)

				self.startAnalysisPushButton.setText("Stopping...")
				self.actionStart_Analysis.setText("Stopping...")

				# self.analysisRunning=False
		except FileNotFoundError:
			QtGui.QMessageBox.warning(self, "Data Error", "Files not found")

			self._setEnableSettingsWidgets(True)
			self._setEnableDataSettingsWidgets(True)

			self.startAnalysisPushButton.setText("Start Analysis")
			self.actionStart_Analysis.setText("Start Analysis")

	def OnAnalysisFinished(self, value):
		if value:
			self._setEnableSettingsWidgets(True)
			self._setEnableDataSettingsWidgets(True)

			self.startAnalysisPushButton.setText("Start Analysis")
			self.actionStart_Analysis.setText("Start Analysis")

			self.startAnalysisPushButton.setEnabled(True)
			self.actionStart_Analysis.setEnabled(True)

			self.analysisRunning=False

	def OnAppIdle(self):
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

