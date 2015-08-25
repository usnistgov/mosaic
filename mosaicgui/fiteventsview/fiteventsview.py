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
import mosaic.stepResponseAnalysis as sra

import matplotlib.ticker as ticker
# from mosaicgui.trajview.trajviewui import Ui_Dialog

class FitEventWindow(QtGui.QDialog):
	def __init__(self, parent = None):
		self.v=[]

		super(FitEventWindow, self).__init__(parent)

		# uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"fiteventsview.ui"), self)
		uic.loadUi(resource_path("fiteventsview.ui"), self)
		self._positionWindow()

		self.eventIndex=0

		# Limit the number of events to 10000
		self.viewerLimit=10000
		self.queryString=""
		self.queryData=[]

		self.queryDatabase=None
		self.EndOfData=False

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(3000)

		self.updateDataOnIdle=True

		# setup hash tables used in this class
		self._setupdict()

		QtCore.QObject.connect(self.nextEventToolButton, QtCore.SIGNAL("clicked()"), self.OnNextButton)
		QtCore.QObject.connect(self.previousEventToolButton, QtCore.SIGNAL("clicked()"), self.OnPreviousButton)
		QtCore.QObject.connect(self.eventIndexLineEdit, QtCore.SIGNAL('editingFinished()'), self.OnEventIndexLineEditChange)
		QtCore.QObject.connect(self.eventIndexLineEdit, QtCore.SIGNAL('editingFinished()'), self.OnEventIndexLineEditChange)
		QtCore.QObject.connect(self.eventIndexHorizontalSlider, QtCore.SIGNAL('valueChanged ( int )'), self.OnEventIndexSliderChange)


	def openDB(self, dbpath, FskHz, updateOnIdle=True):
		"""
			Open the latest sqlite file in a directory
		"""
		self.openDBFile( last_file_in_directory(dbpath, "*sqlite"), FskHz, updateOnIdle)

	def openDBFile(self, dbfile, FskHz, updateOnIdle=True):
		self.queryDatabase=sqlite.sqlite3MDIO()
		self.queryDatabase.openDB(dbfile)

		# self update on idle flag
		self.updateDataOnIdle=updateOnIdle

		# Store the analysis algorithm
		try:
			self.analysisAlgorithm=str(self.queryDatabase.readAnalysisInfo()[3])
		except:
			# If the database doesn't have information on the alogirthm type, 
			# default to stepResponseAnalysis
			self.analysisAlgorithm="stepResponseAnalysis"

		# Generate the query string based on the algorithm in the database
		self.queryString=self.queryStringDict[self.analysisAlgorithm]

		# Setup the fit function based on the algorithm
		try:
			self.fitFuncHnd=self.fitFuncHndDict[self.analysisAlgorithm]
			self.fitFuncArgs=self.fitFuncArgsDict[self.analysisAlgorithm]
		except KeyError:
			self.fitFuncHnd=None
			self.fitFuncArgs="[]"

		try:
			self.stepFuncHnd=self.stepFuncHndDict[self.analysisAlgorithm]
			self.stepFuncArgs=self.stepFuncArgsDict[self.analysisAlgorithm]
		except KeyError:
			self.stepFuncHnd=None
			self.stepFuncArgs="[]"

		self.FskHz=float(FskHz)
		# print self.FskHz
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
		self.setGeometry(1050, 295, 375, 350)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )


	def update_graph(self):
		try:
			q=self.queryData[self.eventIndex]
			fs=self.FskHz

			# time-series data
			datasign=float(np.sign(np.mean(q[1])))
			ydat=datasign*np.array(q[1], dtype='float64')
			xdat=np.arange(0,float((len(q[1]))/fs), float(1/fs))[:len(ydat)]

			np.seterr(invalid='ignore', over='ignore', under='ignore')
			# fit function data
			if str(q[0])=="normal":
				c='#%02x%02x%02x' % (72,91,144)
				cf='#%02x%02x%02x' % (50,50,47)
				cs='#%02x%02x%02x' % (170,41,45)
				self.mpl_hist.canvas.ax.cla()
				self.mpl_hist.canvas.ax.hold(True)
				self.mpl_hist.canvas.ax.plot( xdat, ydat, linestyle='None', marker='o', color=c, markersize=8, markeredgecolor='none', alpha=0.6)
				
				if self.fitFuncHnd:
					xfit=np.arange(0,float((len(q[1]))/fs), float(1/(100*fs)))
					yfit=self.fitFuncHnd( *eval(self.fitFuncArgs) )
					self.mpl_hist.canvas.ax.plot( xfit, yfit, linestyle='-', linewidth='2.0', color=cf)

				if self.stepFuncHnd:
					xstep=np.arange(0,float((len(q[1]))/fs), float(1/(100*fs)))
					ystep=self.stepFuncHnd( *eval(self.stepFuncArgs) )
					self.mpl_hist.canvas.ax.plot( xstep, ystep, linestyle='--', linewidth='2.0', color=cs)

			else:
				self.mpl_hist.canvas.ax.cla()
				self.mpl_hist.canvas.ax.plot( xdat, ydat, linestyle='None', marker='o', color='r', markersize=8, markeredgecolor='none', alpha=0.6)

			self._ticks(5)

			ilabel={-1:'-i', 1:'i'}[int(datasign)]
			self.mpl_hist.canvas.ax.set_xlabel('t (ms)', fontsize=12)
			self.mpl_hist.canvas.ax.set_ylabel(ilabel+' (pA)', fontsize=12)
			
			self.mpl_hist.canvas.draw()

			self.eventIndexLineEdit.setText(str(self.eventIndex))
			if self.EndOfData:
				limittxt=" (at viewer limit)"
			else:
				limittxt=""
			self.setWindowTitle( "Event Viewer - " + str(self.eventIndex) + "/" + str(len(self.queryData)-1) + limittxt)
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
		self.eventIndexHorizontalSlider.setValue( self.eventIndex )
		self.update_graph()

	def OnPreviousButton(self):
		if len(self.queryData) == 0:
			self._updatequery()

		self.eventIndex= max(0, self.eventIndex-1)
		self.eventIndexHorizontalSlider.setValue( self.eventIndex )
		self.update_graph()

	def OnEventIndexLineEditChange(self):
		self.eventIndex=int(self.eventIndexLineEdit.text())
		self.update_graph()

	def OnEventIndexSliderChange(self, value):
		self.eventIndex=int(value)
		self.update_graph()

	def OnAppIdle(self):
		if not self.updateDataOnIdle:
			return

		if not self.EndOfData:
			self._updatequery()
			self.update_graph()

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
				self.queryData=self.queryDatabase.queryDB(self.queryString)

				if len(self.queryData)>=self.viewerLimit: self.EndOfData=True

				# update the QLineEdit validator
				self.eventIndexLineEdit.setValidator( QtGui.QIntValidator(0, len(self.queryData)-1, self) )
				self.eventIndexHorizontalSlider.setMaximum( len(self.queryData)-1 )

		except sqlite3.OperationalError, err:
			if not "RCConstant1" in str(err):
				raise err
		except:
			raise

	def _setupdict(self):
		self.keyDict={
			QtCore.Qt.Key_Right : 	self.OnNextButton,
			QtCore.Qt.Key_Left	:	self.OnPreviousButton
		}

		self.queryStringDict={
			"stepResponseAnalysis" 	: "select ProcessingStatus, TimeSeries, RCConstant1, RCConstant2, EventStart, EventEnd, BlockedCurrent, OpenChCurrent from metadata limit " + str(self.viewerLimit),
			"multiStateAnalysis" 	: "select ProcessingStatus, TimeSeries, RCConstant, EventDelay, CurrentStep, OpenChCurrent from metadata limit " + str(self.viewerLimit),
			"cusumLevelAnalysis" 	: "select ProcessingStatus, TimeSeries, EventDelay, CurrentStep, OpenChCurrent from metadata limit " + str(self.viewerLimit)
		}

		self.fitFuncHndDict={
			"stepResponseAnalysis" 	: fit_funcs.stepResponseFunc,
			"multiStateAnalysis" 	: fit_funcs.multiStateFunc
		}

		self.fitFuncArgsDict={
			"stepResponseAnalysis" 	: "[xfit, q[2], q[3], q[4], q[5], abs(q[7]-q[6]), q[7]]",
			"multiStateAnalysis" 	: "[xfit, q[2], q[3], q[4], q[5], len(q[3])]"
		}

		self.stepFuncHndDict={
			"stepResponseAnalysis" 	: fit_funcs.multiStateStepFunc,
			"multiStateAnalysis" 	: fit_funcs.multiStateStepFunc,
			"cusumLevelAnalysis"	: fit_funcs.multiStateStepFunc
		}

		self.stepFuncArgsDict={
			"stepResponseAnalysis" 	: "[xstep, [q[4], q[5]], [-abs(q[7]-q[6]), abs(q[7]-q[6])], q[7], 2]",
			"multiStateAnalysis" 	: "[xstep, q[3], q[4], q[5], len(q[3])]",
			"cusumLevelAnalysis" 	: "[xstep, q[2], q[3], q[4], len(q[2])]"
		}


if __name__ == '__main__':
	# dbfile=resource_path('eventMD-PEG29-Reference.sqlite')
	dbfile=resource_path('eventMD-tempMSA.sqlite')

	app = QtGui.QApplication(sys.argv)
	dmw = FitEventWindow()
	
	dmw.openDBFile(dbfile, 500)
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

