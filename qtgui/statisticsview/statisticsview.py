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

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(3000)

		self.queryString="select AbsEventStart from metadata where ProcessingStatus='normal' and BlockDepth > 0 and BlockDepth < 1 order by AbsEventStart ASC"
		self.queryData=[]

	def openDB(self, dbpath):
		self.queryDatabase=sqlite.sqlite3MDIO()
		self.queryDatabase.openDB(glob.glob(dbpath+"/*sqlite")[-1])

		self._updatequery()

		# Idle processing
		QtCore.QObject.connect(self.idleTimer, QtCore.SIGNAL('timeout()'), self.OnAppIdle)

	def closeDB(self):
		self.queryDatabase.closeDB()

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		screen = QtGui.QDesktopWidget().screenGeometry()
		self.setGeometry(1050, 0, 300, 200)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )

	def _updatequery(self):
		try:
			self.queryData=np.array(self.queryDatabase.queryDB(self.queryString)).flatten()
			c=self._caprate()

			self.neventsLabel.setText( str(len(self.queryData)) )
			self.caprateLabel.setText( str(c[0]) + " +/- " + str(c[1]) )
		except:
			raise

	def _caprate(self):
		if len(self.queryData) < 200:
			return [0,0]

		arrtimes=np.diff(self.queryData)
		nbins=100
		binstart, binend = max([min(arrtimes),0.001]), min([max(arrtimes), 1])
		dbin=(binend-binstart)/float(nbins)

		counts, bins = np.histogram(arrtimes, bins=np.arange(*[binstart, binend, dbin]))

		# print counts

		# print counts/float(counts[0])
		popt, pcov = curve_fit(self._fitfunc, bins[:len(counts)], counts/counts[0])
		perr=np.sqrt(np.diag(pcov))

		return self._roundcaprate([ 1/(popt[1]/1000.), 1/(perr[1]/1000. * math.sqrt(len(arrtimes))) ])
	
	def _roundcaprate(self, caprate):
		x,y=caprate

		sigx=int(min(0, math.log10(x)))

		if x<10:
			return [ round(x, sigx), round(y, sigx-1) ]
		else:
			return [ int(round(x, sigx)), int(round(y, sigx)) ]

	def _fitfunc(self, t, a, tau):
		return a * np.exp(-t/tau)

	def OnAppIdle(self):
		self._updatequery()

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = StatisticsWindow()
	dmw.openDB('/Users/arvind/Desktop/POM ph5.45 m120_6/')
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

