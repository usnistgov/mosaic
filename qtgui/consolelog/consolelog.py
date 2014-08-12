from __future__ import with_statement

import sys
import os
import csv

from PyQt4 import QtCore, QtGui, uic

class AnalysisLogDialog(QtGui.QDialog):
	def __init__(self, parent = None):
		super(AnalysisLogDialog, self).__init__(parent)

		uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"consoleDialog.ui"), self)
		
		# self.setupUi(self)
		self._positionWindow()

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		screen = QtGui.QDesktopWidget().screenGeometry()
		self.setGeometry(910, 0, 400, 400)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )

	# SLOTS
	def OnSave(self):
		# self.accept()
		pass

	def OnCancel(self):
		self.reject()

		
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = AnalysisLogDialog()
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

