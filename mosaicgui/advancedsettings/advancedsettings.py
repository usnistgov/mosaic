from __future__ import with_statement

import numpy as np
import sys
import os
import csv

from PyQt4 import QtCore, QtGui, uic

import mosaic.abfTrajIO as abf
import mosaic.qdfTrajIO as qdf
from mosaic.metaTrajIO import FileNotFoundError, EmptyDataPipeError
from mosaic.utilities.resource_path import resource_path

# from advancedSettingsDialog import Ui_advancedSettingsDialog

class AdvancedSettingsDialog(QtGui.QDialog):

	def __init__(self, parent = None):
		super(AdvancedSettingsDialog, self).__init__(parent)

		# uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"advancedSettingsDialog.ui"), self)
		uic.loadUi(resource_path("advancedSettingsDialog.ui"), self)
		# self.setupUi(self)
		self._positionWindow()

		QtCore.QObject.connect(self.cancelPushButton, QtCore.SIGNAL("clicked()"), self.OnCancel)
		QtCore.QObject.connect(self.savePushButton, QtCore.SIGNAL("clicked()"), self.OnSave)

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		if sys.platform=='win32':
			self.setGeometry(425, 475, 500, 300)
		else:
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

