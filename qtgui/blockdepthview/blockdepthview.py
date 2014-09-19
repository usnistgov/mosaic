from __future__ import with_statement

import numpy as np
import sys
import os
import gc
import csv
import glob

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt

import pyeventanalysis.sqlite3MDIO as sqlite
import qtgui.autocompleteedit as autocomplete
import qtgui.sqlQueryWorker as sqlworker

import matplotlib.ticker as ticker
# from qtgui.trajview.trajviewui import Ui_Dialog

css = """QLabel {
      color: red;
}"""


class BlockDepthWindow(QtGui.QDialog):
	def __init__(self, parent = None):
		self.v=[]

		super(BlockDepthWindow, self).__init__(parent)

		uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"blockdepthview.ui"), self)
		self._positionWindow()

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(10000)

		self.processeEventsTimer=QtCore.QTimer()
		self.processeEventsTimer.start(500)

		# Set error line edit color to red
		self.errorLabel.setStyleSheet(css)

		self.queryString="select BlockDepth from metadata where ProcessingStatus='normal' and BlockDepth between 0 and 1 and ResTime > 0.025"
		self.queryData=[]
		self.queryError=False
		self.lastGoodQueryString=""
		self.queryRunning=False

		self.qWorker=None
		self.qThread=QtCore.QThread()

		self.queryCompleter=None

		self.nBins=500
		self.binsSpinBox.setValue(self.nBins)

		# Set the default text in the Filter LineEdit
		self.sqlQueryLineEdit.setCompleterValues([])
		self.sqlQueryLineEdit.setText("ResTime > 0.025")


		QtCore.QObject.connect(self.updateButton, QtCore.SIGNAL('clicked()'), self.OnUpdateButton)
		QtCore.QObject.connect(self.sqlQueryLineEdit, QtCore.SIGNAL('textChanged ( const QString & )'), self.OnQueryTextChange)
		QtCore.QObject.connect(self.binsSpinBox, QtCore.SIGNAL('valueChanged ( int )'), self.OnBinsChange)

		# QtCore.QObject.connect(self.processeEventsTimer, QtCore.SIGNAL('timeout()'), self.OnProcessEvents)
		
		

	def openDB(self, dbpath):
		"""
			Open the latest sqlite file in a directory
		"""
		self.openDBFile(glob.glob(dbpath+"/*sqlite")[-1])

	def openDBFile(self, dbfile):
		"""
			Open a specific database file.
		"""
		self.qWorker=sqlworker.sqlQueryWorker(dbfile)
	
		# Connect signals and slots
		self.qWorker.resultsReady.connect(self.OnDataReady)
		self.qWorker.dbColumnsReady.connect(self.OnColDBReady)

		self.qWorker.moveToThread(self.qThread)
	
		self.qWorker.finished.connect(self.qThread.quit)

		self.qThread.start()

		# Query the DB cols
		QtCore.QMetaObject.invokeMethod(self.qWorker, 'dbColumnNames', Qt.QueuedConnection)
		QtCore.QMetaObject.invokeMethod(self.qWorker, 'queryDB', Qt.QueuedConnection, QtCore.Q_ARG(str, self.queryString) )
		self.queryRunning=True

	def closeDB(self):
		pass

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		screen = QtGui.QDesktopWidget().screenGeometry()
		self.setGeometry(405, 0, 500, 400)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )


	def refreshPlot(self):
		try:
			self.dataLoaded=True

			# self.mpl_hist.canvas.ax.set_autoscale_on(True)
			self.update_graph()
		except AttributeError:
			QtGui.QMessageBox.warning(self, "Path Error","Data path not set")
			raise
		except FileNotFoundError:
			QtGui.QMessageBox.warning(self, "Data Error","Files not found")
		except:
			raise

	def update_graph(self):
		try:
			c='#%02x%02x%02x' % (72,91,144)
			self.mpl_hist.canvas.ax.hist( 
						self.queryData, 
						bins=self.nBins, 
						normed=0, 
						histtype='step',
						rwidth=0.1,
						color=c
					)
			# Set limits on the X-axis from 0 to 1
			xmin=max(0, min(self.queryData))
			xmax=min(1, max(self.queryData))
			self.mpl_hist.canvas.ax.set_xlim(xmin,xmax)


			self.mpl_hist.canvas.ax.set_xlabel('<i>/<i0>', fontsize=10)
			self.mpl_hist.canvas.ax.set_ylabel('counts', fontsize=10)
			
			self.mpl_hist.canvas.draw()

			# Once the canvas is updated flag the query as complete
			self.queryRunning=False
			self.updateButton.setEnabled(True)
			self.updateButton.setText("Update")
		except ValueError:
			pass
		except:
			raise

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
		# if self.queryRunning:
		# 	return

		self.qThread.start()
		# print "update query: ", self.queryString
		QtCore.QMetaObject.invokeMethod(self.qWorker, 'queryDB', Qt.QueuedConnection, QtCore.Q_ARG(str, self.queryString) )

		self.queryRunning=True
			
	def OnColDBReady(self, cols):
		self.sqlQueryLineEdit.setCompleterValues(cols)

		# Idle processing
		QtCore.QObject.connect(self.idleTimer, QtCore.SIGNAL('timeout()'), self.OnAppIdle)

	def OnDataReady(self, results, errorstr):
		# print len(results), errorstr
		try:
			if not errorstr:
				self.queryData=np.hstack( np.hstack( np.array( results ) ) )

				self.errorPrefixLabel.setText("")
				self.errorLabel.setText("")

				self.lastGoodQueryString=self.queryString
			else:
				self.errorPrefixLabel.setText("  Query Error: ")
				self.errorLabel.setText(str(errorstr))
				self.queryString=self.lastGoodQueryString
				self.queryError=True

			self.update_graph()
		except IndexError:
			pass

	def OnQueryTextChange(self, text):
		qtext=str(text)
		if qtext:
			self.updateButton.setEnabled(True)			
		else:
			self.updateButton.setEnabled(False)

	def OnUpdateButton(self):
		qtext=str(self.sqlQueryLineEdit.text())
		if qtext:
			self.queryString="select BlockDepth from metadata where ProcessingStatus='normal' and BlockDepth between 0 and 1 and " + qtext
			self.queryError=False

			self.updateButton.setEnabled(False)
			self.updateButton.setText("Updating...")
			self._updatequery()

	def OnBinsChange(self, value):
		self.nBins=int(value)

	def OnAppIdle(self):
		if not self.queryRunning:
			self._updatequery()

	def OnProcessEvents(self):
		pass
		# QtGui.QApplication.sendPostedEvents()

if __name__ == '__main__':
	from os.path import expanduser
	dbpath=expanduser('~')+'/Research/Experiments/Nanoclusters/PW9O34/20140916/m120mV1/'
	# dbpath=expanduser('~')+'/Research/Experiments/PEG29EBSRefData/20120323/singleChan/'

	app = QtGui.QApplication(sys.argv)
	dmw = BlockDepthWindow()
	dmw.openDB(dbpath)
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

