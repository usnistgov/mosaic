import sys

from PyQt4 import QtCore
from PyQt4 import QtGui

import qtgui.settingsview

from pyeventanalysis.metaTrajIO import FileNotFoundError

class qtAnalysisGUI(qtgui.settingsview.settingsview):
	def __init__(self, parent = None):
		super(qtAnalysisGUI, self).__init__(parent)

		self.analysisObject=None
		self.analysisRunning=False
		self.idleTimer=QtCore.QTimer()

		self.idleTimer.start()

		# Start Analysis Signals
		QtCore.QObject.connect(self.startAnalysisPushButton, QtCore.SIGNAL('clicked()'), self.OnStartAnalysis)
		QtCore.QObject.connect(self.actionStart_Analysis, QtCore.SIGNAL('triggered()'), self.OnStartAnalysis)

		# Idle processing
		# QtCore.QObject.connect(self.idleTimer, QtCore.SIGNAL('timeout()'), self.OnAppIdle)

	def OnStartAnalysis(self):
		try:
			if not self.analysisRunning:
				self._setEnableSettingsWidgets(False)
				self._setEnableDataSettingsWidgets(False)
				
				if self.analysisDataModel["DataFilesPath"]:
					with open(self.analysisDataModel["DataFilesPath"]+"/.settings", 'w') as f:
						f.write(
							self.analysisDataModel.GenerateSettingsView(
								eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
								eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText())
							)
						)


					self.startAnalysisPushButton.setText("Stop Analysis")
					self.actionStart_Analysis.setText("Stop Analysis")

					self.trajViewerWindow.hide()

					self.analysisObject=self.analysisDataModel.GenerateAnalysisObject(
						eventPartitionAlgo=str(self.partitionAlgorithmComboBox.currentText()), 
						eventProcessingAlgo=str(self.processingAlgorithmComboBox.currentText())
					)
					
					self.analysisObject.Run(forkProcess=True)

					# import time
					# time.sleep(10)
					# self.analysisObject.Stop()
					
					self.analysisRunning=True	
			else:
				self.analysisObject.Stop()

				self._setEnableSettingsWidgets(True)
				self._setEnableDataSettingsWidgets(True)

				self.startAnalysisPushButton.setText("Start Analysis")
				self.actionStart_Analysis.setText("Start Analysis")

				self.analysisRunning=False
		except FileNotFoundError:
			QtGui.QMessageBox.warning(self, "Data Error", "Files not found")

			self._setEnableSettingsWidgets(True)
			self._setEnableDataSettingsWidgets(True)

			self.startAnalysisPushButton.setText("Start Analysis")
			self.actionStart_Analysis.setText("Start Analysis")

	def OnAppIdle(self):
		pass
		# if self.analysisObject:
		# 	print self.analysisObject.subProc.pid

if __name__ == '__main__':
	# multiprocessing.freeze_support()
	
	app = QtGui.QApplication(sys.argv)
	dmw = qtAnalysisGUI()
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

