from __future__ import with_statement

import numpy as np
import sys
import os
import csv
import glob
import sqlite3
import time

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
		self.totalEvents=0
		self.eventCacheStart=1

		self.queryData=[]

		self.queryDatabase=None
		self.EndOfData=False
		self.DataInitialized=False
		

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(5000)

		# setup hash tables used in this class
		self._setupdict()

		QtCore.QObject.connect(self.nextEventToolButton, QtCore.SIGNAL("clicked()"), self.OnNextButton)
		QtCore.QObject.connect(self.previousEventToolButton, QtCore.SIGNAL("clicked()"), self.OnPreviousButton)
		QtCore.QObject.connect(self.eventIndexLineEdit, QtCore.SIGNAL('editingFinished()'), self.OnEventIndexLineEditChange)
		QtCore.QObject.connect(self.eventIndexLineEdit, QtCore.SIGNAL('editingFinished()'), self.OnEventIndexLineEditChange)
		QtCore.QObject.connect(self.eventIndexHorizontalSlider, QtCore.SIGNAL('valueChanged ( int )'), self.OnEventIndexSliderChange)


	def openDB(self, dbpath, FskHz):
		self.openDBFile(glob.glob(dbpath+"/*sqlite")[-1], FskHz)

	def openDBFile(self, dbfile, FskHz):
		self.DataInitialized=False
		
		self.queryDatabase=sqlite.sqlite3MDIO()
		self.queryDatabase.openDB(dbfile)

		self.FskHz=float(FskHz)

		self._updatequery()
		self.update_graph(self._eventdata())

		self._getrecordcount()
		self._updatewindowtitle()

		self.eventIndexLineEdit.setText(str(self.eventIndex+1))

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


	def update_graph(self, edat):
		try:
			# q=self.queryData[self.eventIndex]
			# q=self._eventdata()
			q=edat
			fs=self.FskHz

			# print len(edat)
			# print len(edat[1])
			# print fs
			# # time-series data
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

			self._ticks(5)

			self.mpl_hist.canvas.ax.set_xlabel('t (ms)', fontsize=10)
			self.mpl_hist.canvas.ax.set_ylabel('|i| (pA)', fontsize=10)
			
			self.mpl_hist.canvas.draw()

			self.eventIndexLineEdit.setText( str( int(self.eventIndex) + 1 ) )
			self._updatewindowtitle()
		except ValueError:
			self.EndOfData=True
			raise
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
		# print "next button"
		self.eventIndex += 1
		self.update_graph(self._eventdata())

		self.eventIndexHorizontalSlider.setValue( self.eventIndex )

	def OnPreviousButton(self):
		# print "prev button"
		self.eventIndex -= 1
		self.update_graph(self._eventdata())

		self.eventIndexHorizontalSlider.setValue( self.eventIndex )

	def OnEventIndexLineEditChange(self):
		# "print line edit change"
		self.eventIndex=int(self.eventIndexLineEdit.text())-1
		self.update_graph(self._eventdata())

	def OnEventIndexSliderChange(self, value):
		self.eventIndex=int(value)
		# print "slider change", value, self.eventIndex, self.totalEvents
		self.update_graph(self._eventdata())

	def OnAppIdle(self):
		# if len(self.queryData) == 0:
		# 	self._updatequery()
		# 	self.update_graph()

		self._getrecordcount()
		self._updatewindowtitle()

		# update the QLineEdit validator
		self.eventIndexLineEdit.setValidator( QtGui.QIntValidator(0, self.totalEvents-1, self) )

		# update slider max
		if self.totalEvents>0:
			self.eventIndexHorizontalSlider.setMaximum( self.totalEvents-1 )
		
	def _ticks(self, nticks):
		axes=self.mpl_hist.canvas.ax

		start, end = axes.get_xlim()
		dx=(end-start)/(nticks-1)
		axes.xaxis.set_ticks( np.arange( start, end+dx, dx ) )
		axes.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.2f'))

		# set the y-axis limits from 0 to ymax
		start, end = axes.get_ylim()
		dy=end/(nticks-1)
		axes.yaxis.set_ticks( np.arange( 0, end+dy, dy ) ) 
		axes.yaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))

	def _updatequery(self):
		
		try:
			if not self.EndOfData:
				t1=time.time()
				q=self._generatequery()
				self.queryData=self.queryDatabase.queryDB(q)
				t2=time.time()
				# print "_updatequery ({0:0.2f} ms)".format(1000*(t2-t1))
		except sqlite3.OperationalError, err:
			raise err
		except:
			raise

	def _sraFunc(self, t, tau, mu1, mu2, a, b):
		try:
			np.seterr(over='ignore', invalid='ignore')
			return a*( (np.exp((mu1-t)/tau)-1)*self._heaviside(t-mu1)+(1-np.exp((mu2-t)/tau))*self._heaviside(t-mu2) ) + b
		except RuntimeWarning:
			# print self.eventIndex
			pass
		except:
			raise

	def _heaviside(self, x):
		out=np.array(x)

		out[out==0]=0.5
		out[out<0]=0
		out[out>0]=1

		return out

	def _eventdata(self):
		try:
			lidx=self.eventIndex-self.eventCacheStart
			if lidx>=0:
				return self.queryData[lidx]
			else:
				# print "_eventdata Lower limit reached (lidx={0}, eventIndex={1}, eventCacheStart={2}, len(queryData)={3})".format(lidx, self.eventIndex, self.eventCacheStart, len(self.queryData) )
				if self.eventIndex < 0:
					self.eventIndex=0
					return self.queryData[0]
				else:
					self._updatequery()
					return self._eventdata()
		except IndexError:
			# print "_eventdata Upper limit reached (lidx={0}, eventIndex={1}, eventCacheStart={2}, len(queryData)={3}, totalEvents={4})".format(lidx, self.eventIndex, self.eventCacheStart, len(self.queryData), self.totalEvents )
			if self.totalEvents == 0:
				return []

			# If end of data
			if self.eventIndex >= self.totalEvents:
				self.eventIndex -= 1
				return self.queryData[-1]
			else:
				self._updatequery()
				return self._eventdata()

	def _generatequery(self):
		self.eventCacheStart=max(0, self.eventIndex-101)
		return "select ProcessingStatus, TimeSeries, RCConstant, EventStart, EventEnd, BlockedCurrent, OpenChCurrent from metadata limit {0}, 200".format(self.eventCacheStart)

	def _getrecordcount(self):
		tempRecCount=self.queryDatabase.queryDB("select count(*) from metadata")[0][0]

		if not self.DataInitialized and tempRecCount-self.totalEvents > 0:
			self._updatequery()
			self.update_graph(self._eventdata())
			self.DataInitialized=True

		self.totalEvents=tempRecCount

	def _updatewindowtitle(self):
		self.setWindowTitle( "Event Viewer - " + str(self.eventIndex+1) + "/" + str(self.totalEvents) )

	def _setupdict(self):
		self.keyDict={
			QtCore.Qt.Key_Right : 	self.OnNextButton,
			QtCore.Qt.Key_Left	:	self.OnPreviousButton
		}

if __name__ == '__main__':
	from os.path import expanduser
	dbpath=expanduser('~')+'/Research/Experiments/PEG29EBSRefData/20120323/singleChan/'

	app = QtGui.QApplication(sys.argv)
	dmw = FitEventWindow()
	
	dmw.openDB(dbpath, 500)

	print dmw._generatequery()

	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

