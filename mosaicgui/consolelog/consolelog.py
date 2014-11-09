from __future__ import with_statement

import sys
import os
import csv

from PyQt4 import QtCore, QtGui, uic
import mosaic.sqlite3MDIO as sqlite
from mosaic.utilities.resource_path import resource_path, last_file_in_directory, format_path

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


	def Update(self):
		self.OnAppIdle()

	def openDB(self, dbpath):
		"""
			Open the latest sqlite file in a directory
		"""
		self.openDBFile( last_file_in_directory(dbpath, "*sqlite") )

	def openDBFile(self, dbfile):
		"""
			Open a specific database file.
		"""
		self.queryDatabase=sqlite.sqlite3MDIO()
		self.queryDatabase.openDB(dbfile)

	def closeDB(self):
		self.queryDatabase.closeDB()

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
				self.consoleLogTextEdit.clear()
				self.consoleLogTextEdit.setText( self.queryDatabase.readAnalysisLog() )
		except AttributeError:
			pass
		except OSError:
			pass

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = AnalysisLogDialog()
	dmw.openDBFile(resource_path("eventMD-PEG29-Reference.sqlite"))

	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

