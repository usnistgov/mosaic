from __future__ import with_statement

import numpy as np
import sys
import os
import csv
import sqlite3

from PyQt4 import QtCore, QtGui, uic

import mosaic.sqlite3MDIO as sqlite
import mosaic.errors as err
import mosaicgui.autocompleteedit as autocomplete
from mosaic.utilities.resource_path import resource_path, last_file_in_directory
import mosaic.utilities.fit_funcs as fit_funcs

import matplotlib.ticker as ticker
# from mosaicgui.trajview.trajviewui import Ui_Dialog

css = """QLabel {
      color: FireBrick;
}"""
css_warning = """QLabel {
      color: OrangeRed;
}"""

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

		# setup error descriptions
		self.errText=err.errors()

		# setup hash tables used in this class
		self._setupdict()

		self._columnhead=[u"\u3008i\u2C7C\u27E9/\u3008i\u2080\u27E9", u"t\u2C7C (\u00B5s)"]

		self.tableModel = FitViewModel(self, [['N/A'], ['N/A']], [self._columnhead,['1']])
		self.fitStatesTableView.setModel(self.tableModel)		

		QtCore.QObject.connect(self.nextEventToolButton, QtCore.SIGNAL("clicked()"), self.OnNextButton)
		QtCore.QObject.connect(self.previousEventToolButton, QtCore.SIGNAL("clicked()"), self.OnPreviousButton)
		QtCore.QObject.connect(self.eventIndexLineEdit, QtCore.SIGNAL('editingFinished()'), self.OnEventIndexLineEditChange)
		QtCore.QObject.connect(self.eventIndexLineEdit, QtCore.SIGNAL('editingFinished()'), self.OnEventIndexLineEditChange)
		QtCore.QObject.connect(self.eventIndexHorizontalSlider, QtCore.SIGNAL('valueChanged ( int )'), self.OnEventIndexSliderChange)
		QtCore.QObject.connect(self.eventParamsCheckBox, QtCore.SIGNAL('stateChanged( int )'), self.OnEventParamsCheckboxState)

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
			# default to adept2State
			self.analysisAlgorithm="adept2State"

		
		try:
			# Generate the query string based on the algorithm in the database
			self.queryString=self.queryStringDict[self.analysisAlgorithm]

			# Setup the fit function based on the algorithm
			self.fitFuncHnd=self.fitFuncHndDict[self.analysisAlgorithm]
			self.fitFuncArgs=self.fitFuncArgsDict[self.analysisAlgorithm]

			self.stepFuncHnd=self.stepFuncHndDict[self.analysisAlgorithm]
			self.stepFuncArgs=self.stepFuncArgsDict[self.analysisAlgorithm]

			self.bdFuncArgs=self.blockDepthArgsDict[self.analysisAlgorithm]
		except KeyError:
			from mosaic.settings import __legacy_settings__
		
			legacyAlgo=__legacy_settings__[self.analysisAlgorithm]
		
			self.queryString=self.queryStringDict[legacyAlgo]
			
			self.fitFuncHnd=self.fitFuncHndDict[legacyAlgo]
			self.fitFuncArgs=self.fitFuncArgsDict[legacyAlgo]

			self.stepFuncHnd=self.stepFuncHndDict[legacyAlgo]
			self.stepFuncArgs=self.stepFuncArgsDict[legacyAlgo]

			self.bdFuncArgs=self.blockDepthArgsDict[legacyAlgo]

			# self.fitFuncHnd=None
			# self.fitFuncArgs="[]"

			# self.stepFuncHnd=None
			# self.stepFuncArgs="[]"

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
		self.setGeometry(1050, 295, 375, 510)
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
			if str(q[0])=="normal" or str(q[0]).startswith('w'):
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

				if str(q[0]).startswith('w'):
					# Set error line edit color to orange
					# self.errLabel.setStyleSheet(css_warning)
					# self.errLabel.setText("Warning: "+ self.errText[str(q[0])] )
					self.errIcon.setText("<html><img height='24' width='24' src='"+resource_path("icons/warning-128.png")+"'></html>")
					self.errLabel.setText(self.errText[str(q[0])])
				else:
					self.errIcon.setText(str(""))
					self.errLabel.setText(str(""))

				header, data=self._bdTable(*eval(self.bdFuncArgs))
				self.tableModel.update( header, data ) 
				self.fitStatesTableView.resizeColumnsToContents()
			else:
				self.mpl_hist.canvas.ax.cla()
				self.mpl_hist.canvas.ax.plot( xdat, ydat, linestyle='None', marker='o', color='r', markersize=8, markeredgecolor='none', alpha=0.6)
				
				# Set error line edit color to red
				# self.errLabel.setStyleSheet(css)
				# self.errLabel.setText("Error: "+ self.errText[str(q[0])] )
				self.errIcon.setText("<html><img height='24' width='24' src='"+resource_path("icons/error-128.png")+"'></html>")
				self.errLabel.setText(self.errText[str(q[0])])

				self.tableModel.update( [self._columnhead,['1']], [['N/A'], ['N/A']] )

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

	def OnEventParamsCheckboxState(self, state):
		if state:
			self.setGeometry(1050, 295, 375, 470)
		else:
			self.setGeometry(1050, 295, 375, 370)

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

	def _bdTable(self, currentStep, openChCurr, eventDelay, nStates):
		header=[ str(i) for i in range(1, nStates+1)]
		blockDepth=[ str(round(bd, 4)) for bd in (np.cumsum(np.array([openChCurr]+currentStep))[1:])/openChCurr][:nStates]
		resTimes=[ str(round(rt, 2)) for rt in np.diff(eventDelay)*1000. ]

		return [ [self._columnhead, header], [ blockDepth, resTimes] ]

	def _setupdict(self):
		self.keyDict={
			QtCore.Qt.Key_Right : 	self.OnNextButton,
			QtCore.Qt.Key_Left	:	self.OnPreviousButton
		}

		self.queryStringDict={
			"adept2State" 	: "select ProcessingStatus, TimeSeries, RCConstant1, RCConstant2, EventStart, EventEnd, BlockedCurrent, OpenChCurrent from metadata limit " + str(self.viewerLimit),
			"adept" 		: "select ProcessingStatus, TimeSeries, RCConstant, EventDelay, CurrentStep, OpenChCurrent from metadata limit " + str(self.viewerLimit),
			"cusumPlus" 	: "select ProcessingStatus, TimeSeries, EventDelay, CurrentStep, OpenChCurrent from metadata limit " + str(self.viewerLimit)
		}

		self.fitFuncHndDict={
			"adept2State" 	: fit_funcs.stepResponseFunc,
			"adept" 		: fit_funcs.multiStateFunc,
			"cusumPlus" 	: None
		}

		self.fitFuncArgsDict={
			"adept2State" 	: "[xfit, q[2], q[3], q[4], q[5], abs(q[7]-q[6]), q[7]]",
			"adept" 		: "[xfit, q[2], q[3], q[4], q[5], len(q[3])]",
			"cusumPlus" 	: "[]"
		}

		self.stepFuncHndDict={
			"adept2State" 	: fit_funcs.multiStateStepFunc,
			"adept" 		: fit_funcs.multiStateStepFunc,
			"cusumPlus"		: fit_funcs.multiStateStepFunc
		}

		self.stepFuncArgsDict={
			"adept2State" 	: "[xstep, [q[4], q[5]], [-abs(q[7]-q[6]), abs(q[7]-q[6])], q[7], 2]",
			"adept" 		: "[xstep, q[3], q[4], q[5], len(q[3])]",
			"cusumPlus" 	: "[xstep, q[2], q[3], q[4], len(q[2])]"
		}

		self.blockDepthArgsDict={
			"adept2State" 	: "[[-abs(q[7]-q[6])], q[7], [q[4],q[5]], 1]",
			"adept" 		: "[q[4], q[5], q[3], len(q[3])-1]",
			"cusumPlus" 	: "[q[3], q[4], q[2], len(q[2])-1]"
		}

class FitViewModel(QtCore.QAbstractTableModel):
	def __init__(self, parent, data, header, *args):
		QtCore.QAbstractTableModel.__init__(self, parent, *args)

		self.data=data
		self.header=header

	def rowCount(self, parent):
		try:
			return len(self.data)
		except IndexError:
			return 0

	def columnCount(self, parent):
		try:
			return len(self.data[0])
		except IndexError:
			return 0

	def data(self, index, role):
		if not index.isValid():
			return None
		elif role != QtCore.Qt.DisplayRole:
			return None

		return self.data[index.row()][index.column()]

	def headerData(self, idx, orientation, role):
		try:
			if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
				return self.header[0][idx]
			elif orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
				return self.header[1][idx]
		except IndexError:
			return None

	def sort(self, col, order):
		self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
		self.data = sorted(self.data, key=operator.itemgetter(col))

		if order == QtCore.Qt.DescendingOrder:
			self.data.reverse()
		
		self.emit(QtCore.SIGNAL("layoutChanged()"))

	def update(self, header, data):
		self.header=header
		self.data=data

		self.emit(QtCore.SIGNAL("layoutChanged()"))

if __name__ == '__main__':
	dbfile=resource_path('eventMD-PEG28-cusumLevelAnalysis.sqlite')
	# dbfile=resource_path('eventMD-PEG28-ADEPT2State.sqlite')
	# dbfile=resource_path('eventMD-tempMSA.sqlite')

	app = QtGui.QApplication(sys.argv)
	dmw = FitEventWindow()
	
	dmw.openDBFile(dbfile, 500)
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

