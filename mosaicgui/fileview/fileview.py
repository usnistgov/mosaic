from __future__ import with_statement

import os
import sys
import operator
import time
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt

import mosaic.sqlite3MDIO as sqlite
from mosaic.utilities.resource_path import resource_path, last_file_in_directory
import mosaicgui.sqlQueryWorker as sqlworker

class FileViewWindow(QtGui.QDialog):
	def __init__(self, parent = None):
		super(FileViewWindow, self).__init__(parent)

		# uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"statisticsview.ui"), self)
		uic.loadUi(resource_path("fileview.ui"), self)
		
		self._positionWindow()

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(3000)
	
		self.queryString="select filename, fileformat, modifiedtime from processedfiles"
		self.queryData=[]

		self.tableModel = FileViewModel(self, [['N/A','N/A','N/A']], ['File Name', 'File Type', 'Last Modified'])
		self.fileTableView.setModel(self.tableModel)

		self.qWorker=None
		self.qThread=QtCore.QThread()

	def openDB(self, dbpath):
		"""
			Open the latest sqlite file in a directory
		"""
		self.openDBFile( last_file_in_directory(dbpath, "*sqlite") )

	def openDBFile(self, dbfile):
		"""
			Open a specific database file.
		"""
		self.qWorker=sqlworker.sqlQueryWorker(dbfile)
	
		# Connect signals and slots
		self.qWorker.resultsReady.connect(self.OnDataReady)

		self.qWorker.moveToThread(self.qThread)	
		self.qWorker.finished.connect(self.qThread.quit)
		self.qThread.start()

		# Query the DB
		self._updatequery()

		# Idle processing
		QtCore.QObject.connect(self.idleTimer, QtCore.SIGNAL('timeout()'), self.OnAppIdle)

	def closeDB(self):
		pass

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		if sys.platform=='win32':
			self.setGeometry(405, 555, 640, 200)
		else:
			self.setGeometry(405, 585, 640, 200)

	def _updatequery(self):
		self.qThread.start()
		QtCore.QMetaObject.invokeMethod(self.qWorker, 'executeSQL', Qt.QueuedConnection, QtCore.Q_ARG(str, self.queryString) )
		self.queryRunning=True

	def OnDataReady(self, res, errorstr):
		if not errorstr:
			try:
				if len(res) > 0:
					self.queryData=[ [r[0], r[1], time.ctime(float(r[2])) ] for r in res]

					# self.tableModel = FileViewModel(self, self.queryData, ['File Name', 'File Type', 'Last Modified'])
					self.tableModel.update(self.queryData)
					# self.fileTableView.setModel(self.tableModel)

					self.fileTableView.resizeColumnsToContents()
			except:
				raise
				
		self.queryRunning=False

	def OnAppIdle(self):
		if not self.queryRunning:
			self._updatequery()

class FileViewModel(QtCore.QAbstractTableModel):
	def __init__(self, parent, data, header, *args):
		QtCore.QAbstractTableModel.__init__(self, parent, *args)

		self.data=data
		self.header=header

	def rowCount(self, parent):
		return len(self.data)

	def columnCount(self, parent):
		return len(self.data[0])

	def data(self, index, role):
		if not index.isValid():
			return None
		elif role != QtCore.Qt.DisplayRole:
			return None
		return self.data[index.row()][index.column()]

	def headerData(self, col, orientation, role):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return self.header[col]

		return None

	def sort(self, col, order):
		self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
		self.data = sorted(self.data, key=operator.itemgetter(col))

		if order == QtCore.Qt.DescendingOrder:
			self.data.reverse()
		
		self.emit(QtCore.SIGNAL("layoutChanged()"))

	def update(self, data):
		self.data=data
		self.emit(QtCore.SIGNAL("layoutChanged()"))

if __name__ == '__main__':
	dbfile=resource_path('eventMD-PEG29-Reference.sqlite')

	app = QtGui.QApplication(sys.argv)
	dmw = FileViewWindow()
	dmw.openDBFile(dbfile)
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

