# -*- coding: utf-8 -*-
import sys
import sqlite3
import time
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
			# t1=time.time()
			self.queryDatabase=sqlite.sqlite3MDIO()
			self.queryDatabase.openDB(self.dbFile)

			# t1a=time.time()
			self.resultsReady.emit(self.queryDatabase.queryDB(str(q)), "")
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
			# t1=time.time()
			self.queryDatabase=sqlite.sqlite3MDIO()
			self.queryDatabase.openDB(self.dbFile)

			# t1a=time.time()
			r1=self.queryDatabase.queryDB(str(q1))
			r2=self.queryDatabase.queryDB(str(q2))

			self.resultsReady2.emit(r1, r2, "")
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

def OnDBColsReady(cols):
	print cols

def onDataReady(results, errorstr):
	print len(results)
	print errorstr

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)

	dbpath=expanduser('~')+'/Research/Experiments/Nanoclusters/PW9O34/20140916/m120mV1/eventMD-20140916-145800.sqlite'
	q="select BlockDepth from metadata where ProcessingStatus='normal' and BlockDepth between 0 and 1"
	thread = QtCore.QThread()  
	obj = sqlQueryWorker(dbpath)
	obj.resultsReady.connect(onDataReady)
	obj.dbColumnsReady.connect(OnDBColsReady)

	obj.moveToThread(thread)

	
	obj.finished.connect(thread.quit)

	# time.sleep(10)
	thread.start()

	QtCore.QMetaObject.invokeMethod(obj, 'dbColumnNames', Qt.QueuedConnection)
	QtCore.QMetaObject.invokeMethod(obj, 'queryDB', Qt.QueuedConnection,
									QtCore.Q_ARG(str, q)
									)
	app.exec_()
