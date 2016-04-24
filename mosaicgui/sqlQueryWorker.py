# -*- coding: utf-8 -*-
import sys
import sqlite3
from os.path import expanduser
import mosaic.sqlite3MDIO as sqlite
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt


class sqlQueryWorker(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	resultsReady = QtCore.pyqtSignal(list, str)
	resultsReady2 = QtCore.pyqtSignal(list, list, str)
	dbColumnsReady = QtCore.pyqtSignal(list)

	def __init__(self, dbfile, **kwargs):
		super(sqlQueryWorker, self).__init__(**kwargs)
		self.dbFile=dbfile

	@QtCore.pyqtSlot(bool)
	def dbColumnNames(self, filterRealList):
		self.queryDatabase=sqlite.sqlite3MDIO()
		self.queryDatabase.openDB(self.dbFile)
		if filterRealList:
			self.dbColumnsReady.emit( [ col[0] for col in zip( self.queryDatabase.mdColumnNames, self.queryDatabase.mdColumnTypes ) if col[1] != 'REAL_LIST' ] )
		else:
			self.dbColumnsReady.emit(self.queryDatabase.mdColumnNames)
		self.queryDatabase.closeDB()
		self.finished.emit()

	@QtCore.pyqtSlot(str)
	def queryDB(self, q):
		try:
			self.queryDatabase=sqlite.sqlite3MDIO()
			self.queryDatabase.openDB(self.dbFile)

			self.resultsReady.emit(self.queryDatabase.queryDB(str(q)), "")
			
			self.queryDatabase.closeDB()
			
		except sqlite3.OperationalError, err:
			self.queryDatabase.closeDB()
			self.resultsReady.emit([], str(err))
		
		self.finished.emit()
		
	@QtCore.pyqtSlot(str)
	def executeSQL(self, q):
		try:
			# t1=time.time()
			self.queryDatabase=sqlite.sqlite3MDIO()
			self.queryDatabase.openDB(self.dbFile)

			# t1a=time.time()
			self.resultsReady.emit(self.queryDatabase.executeSQL(str(q)), "")
			# t2a=time.time()

			self.queryDatabase.closeDB()
			# t2=time.time()

			# print "query time = ", t2a-t1a
			# print "overhead = ", (t2-t1)-(t2a-t1a)
			# print "total time = ", t2-t1
		except sqlite3.OperationalError, err:
			self.queryDatabase.closeDB()
			self.resultsReady.emit([], str(err))
		
		self.finished.emit()
	
	@QtCore.pyqtSlot(str, str)
	def queryDB2(self, q1, q2):
		try:
			self.queryDatabase=sqlite.sqlite3MDIO()
			self.queryDatabase.openDB(self.dbFile)

			r1=self.queryDatabase.queryDB(str(q1))
			r2=self.queryDatabase.queryDB(str(q2))

			self.resultsReady2.emit(r1, r2, "")

			self.queryDatabase.closeDB()
		except sqlite3.OperationalError, err:
			self.queryDatabase.closeDB()
			self.resultsReady.emit([], str(err))
		
		self.finished.emit()

def OnDBColsReady(cols):
	print cols

def onDataReady(results, errorstr):
	print results
	print errorstr

if __name__ == '__main__':
	from mosaic.utilities.resource_path import resource_path

	app = QtGui.QApplication(sys.argv)

	dbfile=resource_path('eventMD-PEG29-Reference.sqlite')
	q="select filename, fileformat, modifiedtime from processedfiles"

	c=sqlite.sqlite3MDIO()
	c.openDB(dbfile)
	print c.executeSQL( q )
	c.closeDB()

	thread = QtCore.QThread()  
	obj = sqlQueryWorker(dbfile)
	obj.resultsReady.connect(onDataReady)
	obj.dbColumnsReady.connect(OnDBColsReady)

	obj.moveToThread(thread)

	
	obj.finished.connect(thread.quit)

	thread.start()

	QtCore.QMetaObject.invokeMethod(obj, 'dbColumnNames', Qt.QueuedConnection, QtCore.Q_ARG(bool, False) )
	QtCore.QMetaObject.invokeMethod(obj, 'executeSQL', Qt.QueuedConnection, QtCore.Q_ARG(str, q) )
	app.exec_()
