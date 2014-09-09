from __future__ import with_statement

import sys
import math
import os
import csv
import glob
import sqlite3

import numpy as np
from scipy.optimize import curve_fit
from PyQt4 import QtCore, QtGui, uic

import pyeventanalysis.sqlite3MDIO as sqlite

css = """QLabel {
      color: black;
}"""


class StatisticsWindow(QtGui.QDialog):
	def __init__(self, parent = None):
		self.v=[]

		super(StatisticsWindow, self).__init__(parent)

		uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"statisticsview.ui"), self)
		self._positionWindow()

		self.queryDatabase=None

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(3000)

		self.queryString="select AbsEventStart from metadata where ProcessingStatus='normal'"
		self.queryData=[]
		self.totalEvents=0

		# Set QLabel properties
		self.neventsLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
		self.errorrateLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
		self.caprateLabel.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

	def openDB(self, dbpath):
		"""
			Open the latest sqlite file in a directory
		"""
		self.openDBFile(glob.glob(dbpath+"/*sqlite")[-1])

	def openDBFile(self, dbfile):
		"""
			Open a specific database file.
		"""
		self.queryDatabase=sqlite.sqlite3MDIO()
		self.queryDatabase.openDB(dbfile)

		# Idle processing
		QtCore.QObject.connect(self.idleTimer, QtCore.SIGNAL('timeout()'), self.OnAppIdle)

	def closeDB(self):
		if self.queryDatabase:
			self.queryDatabase.closeDB()

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		screen = QtGui.QDesktopWidget().screenGeometry()
		self.setGeometry(1050, 0, 375, 200)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )

	def _updatequery(self):
		try:
			self.queryData=np.array(self.queryDatabase.queryDB(self.queryString)).flatten()

			self.totalEvents=len( self.queryDatabase.queryDB("select ProcessingStatus from metadata") )
			c=self._caprate()

			self.neventsLabel.setText( str(self.totalEvents) )
			self.errorrateLabel.setText( str(round(100.*(1 - len(self.queryData)/float(self.totalEvents)), 2)) + ' %' )
			self.caprateLabel.setText( str(c[0]) + " &#177; " + str(c[1]) + " s<sup>-1</sup>" )
			self.elapsedtimeLabel.setText( self._formatelapsedtime() )
		except ZeroDivisionError:
			pass
		except:
			raise

	def _caprate(self):
		if len(self.queryData) < 200:
			return [0,0]

		arrtimes=np.diff(self.queryData)/1000.		
		counts, bins = np.histogram(arrtimes, bins=100, density=True)
		
		try:
			popt, pcov = curve_fit(self._fitfunc, bins[:len(counts)], counts, p0=[1, np.mean(arrtimes)])
			perr=np.sqrt(np.diag(pcov))
		except:
			return [0,0]

		return self._roundcaprate([ 1/popt[1], 1/(popt[1]*math.sqrt(len(self.queryData))) ])
	
	def _roundcaprate(self, caprate):
		try:
			x,y=caprate

			sigx=int(min(0, math.log10(x)))

			if x<10:
				return [ round(x, sigx), round(y, sigx-1) ]
			else:
				return [ int(round(x, sigx)), int(round(y, sigx)) ]
		except:
			return [0,0]

	def _formatelapsedtime(self):
		etime=self.queryData[-1]/1000.

		if etime <= 60:
			elaptime=str(round(etime, 2)) + " s"
		elif etime > 60 and etime < 600:
			m=int(round(etime/60))
			s=int(round(etime%60))
			elaptime=str(m) + " min " + str(s) + " s"
		else:
			elaptime=str(round(etime/60.)) + " min"

		return elaptime
		
	def _fitfunc(self, t, a, tau):
		return a * np.exp(-t/tau)

	def OnAppIdle(self):
		self._updatequery()

if __name__ == '__main__':
	from os.path import expanduser
	dbpath=expanduser('~')+'/Research/Experiments/PEG29EBSRefData/20120323/singleChan/'

	app = QtGui.QApplication(sys.argv)
	dmw = StatisticsWindow()
	dmw.openDB(dbpath)
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

