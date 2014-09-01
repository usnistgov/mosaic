from __future__ import with_statement

import numpy as np
import sys
import os
import csv

from PyQt4 import QtCore, QtGui, uic

import pyeventanalysis.abfTrajIO as abf
import pyeventanalysis.qdfTrajIO as qdf
from pyeventanalysis.metaTrajIO import FileNotFoundError, EmptyDataPipeError

# from advancedSettingsDialog import Ui_advancedSettingsDialog

class AdvancedSettingsDialog(QtGui.QDialog):

	def __init__(self, parent = None):
		super(AdvancedSettingsDialog, self).__init__(parent)

		uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"advancedSettingsDialog.ui"), self)
		# self.setupUi(self)
		self._positionWindow()

		QtCore.QObject.connect(self.cancelPushButton, QtCore.SIGNAL("clicked()"), self.OnCancel)
		QtCore.QObject.connect(self.savePushButton, QtCore.SIGNAL("clicked()"), self.OnSave)

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		screen = QtGui.QDesktopWidget().screenGeometry()
		self.setGeometry(405, 475, 500, 300)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )

	def updateSettingsString(self, str):
		self.advancedSettingsTextEdit.setText(str)

	# SLOTS
	def OnSave(self):
		self.accept()
		# pass

	def OnCancel(self):
		self.reject()

		
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = AdvancedSettingsDialog()
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

