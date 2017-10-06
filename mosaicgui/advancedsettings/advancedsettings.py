from __future__ import with_statement

import numpy as np
import sys
import os
import csv

from PyQt4 import QtCore, QtGui, uic

import mosaic.trajio.abfTrajIO as abf
import mosaic.trajio.qdfTrajIO as qdf
from mosaic.trajio.metaTrajIO import FileNotFoundError, EmptyDataPipeError
from mosaic.utilities.resource_path import resource_path
import mosaicgui.mosaicSyntaxHighlight as mosaicSyntaxHighlight

# from advancedSettingsDialog import Ui_advancedSettingsDialog

class AdvancedSettingsDialog(QtGui.QDialog):

	def __init__(self, parent = None):
		super(AdvancedSettingsDialog, self).__init__(parent)

		uic.loadUi(resource_path("advancedSettingsDialog.ui"), self)
		self._positionWindow()

		mosaicSyntaxHighlight.mosaicSyntaxHighlight( self.advancedSettingsTextEdit, resource_path("mosaicgui/highlight-spec/json.json") )

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

	def updateSettingsString(self, str):
		self.advancedSettingsTextEdit.setText(str)

	# SLOTS
	def OnSave(self):
		self.accept()

	def OnCancel(self):
		self.reject()

		
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = AdvancedSettingsDialog()
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

