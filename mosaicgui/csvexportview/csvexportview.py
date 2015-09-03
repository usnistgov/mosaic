from __future__ import with_statement

import numpy as np
import sys
import os
import csv
import sqlite3

from PyQt4 import QtCore, QtGui, uic

import mosaic.sqlite3MDIO as sqlite
import mosaicgui.autocompleteedit as autocomplete
from mosaic.utilities.resource_path import resource_path, last_file_in_directory
import mosaic.utilities.fit_funcs as fit_funcs

import matplotlib.ticker as ticker
# from mosaicgui.trajview.trajviewui import Ui_Dialog

class CSVExportWindow(QtGui.QDialog):
	def __init__(self, parent = None):
		self.v=[]

		super(CSVExportWindow, self).__init__(parent)

		# uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"fiteventsview.ui"), self)
		uic.loadUi(resource_path("csvexportview.ui"), self)
		self._positionWindow()

		self.queryString=""
		self.queryData=[]


		self.dbFieldsGroupBox.setEnabled(True)

		self.advancedCheckBox.setChecked(False)
		self.advancedGroupBox.setHidden(True)


		QtCore.QObject.connect(self.cancelButton, QtCore.SIGNAL("clicked()"), self.OnCancel)
		QtCore.QObject.connect(self.exportButton, QtCore.SIGNAL("clicked()"), self.OnExport)

		QtCore.QObject.connect(self.advancedCheckBox, QtCore.SIGNAL("clicked(bool)"), self.OnAdvancedChecked)


	# SLOTS
	def OnExport(self):
		# print self.FskHz
		self._exportCSV()

		self.accept()
		# pass

	def OnCancel(self):
		self.reject()
		# QtCore.QObject.connect(self.eventIndexHorizontalSlider, QtCore.SIGNAL('valueChanged ( int )'), self.OnEventIndexSliderChange)

	def OnAdvancedChecked(self, checked):
		if checked:
			self.sqlQueryLineEdit.setFocus()

	def openDB(self, dbpath, updateOnIdle=True):
		"""
			Open the latest sqlite file in a directory
		"""
		self.openDBFile( last_file_in_directory(dbpath, "*sqlite"), FskHz, updateOnIdle)

	def openDBFile(self, dbfile, updateOnIdle=True):
		self.queryDatabase=sqlite.sqlite3MDIO()
		self.queryDatabase.openDB(dbfile)

		self._updateDBFields()


	def closeDB(self):
		if self.queryDatabase:
			self.queryDatabase.closeDB()

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		screen = QtGui.QDesktopWidget().screenGeometry()
		self.setGeometry(50, 200, 250, 150)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )

	def _updateDBFields(self):
		cols=self.queryDatabase.mdColumnNames

		checkboxlayout = QtGui.QVBoxLayout()
		self.dbFieldsGroupBox.setLayout(checkboxlayout)

		for col in cols:
			cb=QtGui.QCheckBox(str(col))
			cb.setChecked(True)
			checkboxlayout.addWidget( cb )

	def _exportCSV(self):
		try:
			return self.queryDatabase.exportToCSV( self._genquery() )
		except:
			raise

	def _genquery(self):
		if self.advancedCheckBox.isChecked():
			basequery = str(self.sqlQueryLineEdit.text())
		else:
			cols=', '.join([ str(cb.text()) for cb in self.dbFieldsGroupBox.children()[1:] if cb.isChecked() ])
			basequery = "select "+cols+" from metadata"

		return basequery

if __name__ == '__main__':
	# dbfile=resource_path('eventMD-PEG29-Reference.sqlite')
	dbfile=resource_path('eventMD-PEG28-cusumLevelAnalysis.sqlite')
	# dbfile=resource_path('eventMD-PEG28-stepResponseAnalysis.sqlite')

	app = QtGui.QApplication(sys.argv)
	dmw = CSVExportWindow()
	
	dmw.openDBFile(dbfile, 500)
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

