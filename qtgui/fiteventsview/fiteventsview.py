from __future__ import with_statement

import numpy as np
import sys
import os
import csv
import glob
import sqlite3

from PyQt4 import QtCore, QtGui, uic

import pyeventanalysis.sqlite3MDIO as sqlite
import qtgui.autocompleteedit as autocomplete

import matplotlib.ticker as ticker
# from qtgui.trajview.trajviewui import Ui_Dialog

class FitEventWindow(QtGui.QDialog):
	def __init__(self, parent = None):
		self.v=[]

		super(FitEventWindow, self).__init__(parent)

		uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"fiteventsview.ui"), self)
		self._positionWindow()

		self.eventIndex=0

		self.queryString="select ProcessingStatus, TimeSeries, RCConstant, EventStart, EventEnd, BlockedCurrent, OpenChCurrent from metadata"
		self.queryData=[]

		self.queryDatabase=None
		self.EndOfData=False

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(3000)

		# setup hash tables used in this class
		self._setupdict()

		QtCore.QObject.connect(self.nextEventToolButton, QtCore.SIGNAL("clicked()"), self.OnNextButton)
		QtCore.QObject.connect(self.previousEventToolButton, QtCore.SIGNAL("clicked()"), self.OnPreviousButton)
		QtCore.QObject.connect(self.eventIndexLineEdit, QtCore.SIGNAL('editingFinished()'), self.OnEventIndexLineEditChange)
		

	def openDB(self, dbpath, FskHz):
		self.queryDatabase=sqlite.sqlite3MDIO()
		self.queryDatabase.openDB(glob.glob(dbpath+"/*sqlite")[-1])

		self.FskHz=float(FskHz)

		self._updatequery()
		self.update_graph()

		self.eventIndexLineEdit.setText(str(self.eventIndex))

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
		self.setGeometry(1050, 275, 375, 350)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )


	def update_graph(self):
		try:
			q=self.queryData[self.eventIndex]
			fs=self.FskHz

			# time-series data
			ydat=np.abs(q[1])
			xdat=np.arange(0,float((len(q[1]))/fs), float(1/fs))[:len(ydat)]

			# fit function data
			# ProcessingStatus, TimeSeries, RCConstant, EventStart, EventEnd, CurrentStep, OpenChCurrent
			xfit=np.arange(0,float((len(q[1]))/fs), float(1/(100*fs)))
			yfit=self._sraFunc( xfit, q[2], q[3], q[4], abs(q[6]-q[5]), q[6])

			if str(q[0])=="normal":
				c='#%02x%02x%02x' % (72,91,144)
				self.mpl_hist.canvas.ax.cla()
				self.mpl_hist.canvas.ax.hold(True)
				self.mpl_hist.canvas.ax.plot( xdat, ydat, linestyle='None', marker='o', color=c, markersize=8, markeredgecolor='none', alpha=0.6)
				self.mpl_hist.canvas.ax.plot( xfit, yfit, 'k-')
			else:
				self.mpl_hist.canvas.ax.cla()
				self.mpl_hist.canvas.ax.plot( xdat, ydat, linestyle='None', marker='o', color='r', markersize=8, markeredgecolor='none', alpha=0.6)


			self.mpl_hist.canvas.ax.set_xlabel('t (ms)', fontsize=10)
			self.mpl_hist.canvas.ax.set_ylabel('|i| (pA)', fontsize=10)
			
			self.mpl_hist.canvas.draw()

			self.eventIndexLineEdit.setText(str(self.eventIndex))
			self.setWindowTitle( "Event Viewer - " + str(self.eventIndex) + "/" + str(len(self.queryData)-1))
		except ValueError:
			self.EndOfData=True
		except IndexError:
			pass
		except:
			raise


	def keyPressEvent(self, event):
		try:
			if event.isAutoRepeat():
				self.keyDict[ event.key() ]()
		except KeyError:
			pass

	def keyReleaseEvent(self, event):
		try:
			self.keyDict[ event.key() ]()
		except KeyError:
			pass

	def OnNextButton(self):
		# If we run out of data query the DB again
		if self.eventIndex ==  len(self.queryData)-1 or len(self.queryData) == 0:
			self._updatequery()

		self.eventIndex+=1
		self.update_graph()

	def OnPreviousButton(self):
		if len(self.queryData) == 0:
			self._updatequery()

		self.eventIndex= max(0, self.eventIndex-1)
		self.update_graph()

	def OnEventIndexLineEditChange(self):
		self.eventIndex=int(self.eventIndexLineEdit.text())
		self.update_graph()

	def OnAppIdle(self):
		if len(self.queryData) == 0:
			self._updatequery()
			self.update_graph()

	def _ticks(self, nticks):
		axes=self.mpl_hist.canvas.ax

		start, end = axes.get_xlim()
		dx=(end-start)/(nticks-1)
		axes.xaxis.set_ticks( np.arange( start, end+dx, dx ) )
		axes.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.2f'))

		start, end = axes.get_ylim()
		dy=(end-start)/(nticks-1)
		axes.yaxis.set_ticks( np.arange( start, end+dy, dy ) ) 
		axes.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

	def _updatequery(self):
		try:
			if not self.EndOfData:
				self.queryData=self.queryDatabase.queryDB(self.queryString)

				# update the QLineEdit validator
				self.eventIndexLineEdit.setValidator( QtGui.QIntValidator(0, len(self.queryData)-1, self) )
		except sqlite3.OperationalError, err:
			raise err
		except:
			raise

	def _sraFunc(self, t, tau, mu1, mu2, a, b):
		try:
			return a*( (np.exp((mu1-t)/tau)-1)*self._heaviside(t-mu1)+(1-np.exp((mu2-t)/tau))*self._heaviside(t-mu2) ) + b
		except:
			raise

	def _heaviside(self, x):
		out=np.array(x)

		out[out==0]=0.5
		out[out<0]=0
		out[out>0]=1

		return out

	def _setupdict(self):
		self.keyDict={
			QtCore.Qt.Key_Right : 	self.OnNextButton,
			QtCore.Qt.Key_Left	:	self.OnPreviousButton
		}

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = FitEventWindow()
	# d='/Users/arvind/Desktop/POM ph5.45 m120_6'
	d='/Users/arvind/Research/Experiments/PEG29EBSRefData/20120323/singleChan/'
	dmw.openDB(d, 500)
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

