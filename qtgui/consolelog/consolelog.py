from __future__ import with_statement

import sys
import os
import csv

from PyQt4 import QtCore, QtGui, uic
from utilities.resource_path import resource_path, last_file_in_directory

class AnalysisLogDialog(QtGui.QDialog):
	def __init__(self, parent = None):
		super(AnalysisLogDialog, self).__init__(parent)

		# uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"consoleDialog.ui"), self)
		uic.loadUi( resource_path("consoleDialog.ui"), self)
		
		# self.setupUi(self)
		self._positionWindow()

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(5000)

		self.logFileTimeStamp=0.0

		# Idle processing
		QtCore.QObject.connect(self.idleTimer, QtCore.SIGNAL('timeout()'), self.OnAppIdle)


	def dataPath(self, path):
		self.logFileTimeStamp=0.0
		self.logfile=path+'/eventProcessing.log'

	def Update(self):
		self.OnAppIdle()

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		screen = QtGui.QDesktopWidget().screenGeometry()
		self.setGeometry(405, 555, 640, 200)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )

	# SLOTS
	def OnSave(self):
		# self.accept()
		pass

	def OnCancel(self):
		self.reject()

	def OnAppIdle(self):
		try:
			t1=os.stat(self.logfile).st_mtime
			if t1 > self.logFileTimeStamp:
				self.logFileTimeStamp=t1

				with open(self.logfile, 'r') as logfile:
					logtxt = logfile.read()
				self.consoleLogTextEdit.clear()
				self.consoleLogTextEdit.setText( logtxt )
		except AttributeError:
			pass

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = AnalysisLogDialog()
	dmw.dataPath("/Users/arvind/Research/Experiments/PEG29EBSRefData/20120323/singleChan/")

	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

