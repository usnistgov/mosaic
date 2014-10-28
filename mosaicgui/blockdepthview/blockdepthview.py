from __future__ import with_statement

import numpy as np
import sys
import os
import gc
import csv
import time
import sqlite3
from scipy import signal

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt

import mosaic.sqlite3MDIO as sqlite
import mosaicgui.autocompleteedit as autocomplete
import mosaicgui.sqlQueryWorker as sqlworker
from utilities.resource_path import resource_path, last_file_in_directory
import matplotlib.ticker as ticker
# from mosaicgui.trajview.trajviewui import Ui_Dialog

css = """QLabel {
      color: red;
}"""


class BlockDepthWindow(QtGui.QDialog):
	def __init__(self, parent = None):
		self.v=[]

		super(BlockDepthWindow, self).__init__(parent)


		# uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"blockdepthview.ui"), self)
		uic.loadUi(resource_path("blockdepthview.ui"), self)

		self._positionWindow()

		self.queryInterval=15
		self.lastQueryTime=round(time.time())

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(5000)

		# self.processeEventsTimer=QtCore.QTimer()
		# self.processeEventsTimer.start(500)

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

		self.maxLevel=5
		self.levelHorizontalSlider.setValue(self.maxLevel)

		# add a status bar
		sb=QtGui.QStatusBar()
		self.statusBarHorizontalLayout.addWidget(sb)
		self.statusBarHorizontalLayout.setMargin(0)
		self.statusBarHorizontalLayout.setSpacing(0)

		self.statusbarLine.hide()

		QtCore.QObject.connect(self.updateButton, QtCore.SIGNAL('clicked()'), self.OnUpdateButton)
		QtCore.QObject.connect(self.sqlQueryLineEdit, QtCore.SIGNAL('textChanged ( const QString & )'), self.OnQueryTextChange)
		QtCore.QObject.connect(self.binsSpinBox, QtCore.SIGNAL('valueChanged ( int )'), self.OnBinsChange)
		QtCore.QObject.connect(self.levelHorizontalSlider, QtCore.SIGNAL('valueChanged ( int )'), self.OnlevelSliderChange)
		QtCore.QObject.connect(self.peakDetectCheckBox, QtCore.SIGNAL('clicked(bool)'), self.OnPeakDetect)

		# QtCore.QObject.connect(self.processeEventsTimer, QtCore.SIGNAL('timeout()'), self.OnProcessEvents)		

	def openDB(self, dbpath):
		"""
			Open the latest sqlite file in a directory
		"""
		self.openDBFile( last_file_in_directory(dbpath, "*sqlite") )

	def openDBFile(self, dbfile):
		"""
			Open a specific database file.
		"""
		# Create an index to speed up queries
		self._createDBIndex(dbfile)

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

		self._updateButtonEnabled(False)

	def closeDB(self):
		pass

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		screen = QtGui.QDesktopWidget().screenGeometry()
		if sys.platform=='win32':
			self.setGeometry(425, 30, 640, 400)
		else:
			self.setGeometry(405, 0, 640, 400)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )

	def _createDBIndex(self, dbfile):
		db = sqlite3.connect(dbfile, detect_types=sqlite3.PARSE_DECLTYPES)
		with db:

			db.execute('CREATE INDEX IF NOT EXISTS blockDepthViewIndex ON metadata (BlockDepth, ResTime)')
		db.commit()
		db.close()

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
			self.mpl_hist.canvas.ax.cla()
			self.mpl_hist.canvas.ax.hold(True)

			c='#%02x%02x%02x' % (72,91,144)
			self.blockDepthHist=self.mpl_hist.canvas.ax.hist( 
						self.queryData, 
						bins=self.nBins, 
						normed=0, 
						histtype='step',
						rwidth=0.1,
						color=c
					)

			ylims=self.mpl_hist.canvas.ax.get_ylim()

			# draw peak positions
			if self.peakDetectCheckBox.isChecked():
				h=self.blockDepthHist

				minsnr=max(1,0.2*self.maxLevel)
				self.peakLocations = signal.find_peaks_cwt(h[0], widths=np.arange(1, self.maxLevel), min_snr=minsnr )
				
				peakind=self.peakLocations

				self.mpl_hist.canvas.ax.scatter(h[1][peakind], h[0][peakind], color='red')
					
			self.mpl_hist.canvas.ax.set_xlabel('<i>/<i0>', fontsize=10)
			self.mpl_hist.canvas.ax.set_ylabel('counts', fontsize=10)
			
			self.mpl_hist.canvas.mpl_connect('motion_notify_event', self._mplOnPick)
			# Set limits on the X-axis from 0 to 1
			xmin=max(0, min(self.queryData))
			xmax=min(1, max(self.queryData))
			self.mpl_hist.canvas.ax.set_xlim(xmin,xmax)
			self.mpl_hist.canvas.ax.set_ylim(bottom=0.0, top=ylims[1]) 

			self.mpl_hist.canvas.draw()

			# Once the canvas is updated flag the query as complete
			self.queryRunning=False
			self.lastQueryTime=round(time.time())
			self._updateButtonEnabled(True)
		except ValueError:
			pass
		except IndexError:
			pass
		except:
			raise

	def _mplOnPick(self, event):
		if self.peakDetectCheckBox.isChecked():
			peakind=self.peakLocations
			h=self.blockDepthHist

			if event.xdata is not None and event.ydata is not None:
				xcrit=np.isclose(h[1][peakind], event.xdata, atol=0.02).any()
				ycrit=np.isclose(h[0][peakind], event.ydata, atol=round(max(h[0])/100.) ).any()
				if xcrit and ycrit:
					peakstr='Peak: &lt;i&gt;/&lt;i<sub>0</sub>&gt;={0:0.3f}, counts={1:d}'.format(event.xdata, int(round(event.ydata)))
					self.statusbarLine.show()
					self.peakLabel.setText(peakstr)
				else:
					self.peakLabel.setText('')
					self.statusbarLine.hide()

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

		# print "_updatequery"
		self.queryRunning=True
		self._updateButtonEnabled(False)
			
	def _updateButtonEnabled(self, value):
		if value:
			self.updateButton.setEnabled(True)
			self.updateButton.setText("Update")
		else:
			self.updateButton.setEnabled(False)
			self.updateButton.setText("Updating...")

	def OnlevelSliderChange(self, value):
		self.maxLevel=int(value)
		self.update_graph()

	def OnPeakDetect(self, checked):
		self.update_graph()

	def OnColDBReady(self, cols):
		self.sqlQueryLineEdit.setCompleterValues(cols)

		# Idle processing
		QtCore.QObject.connect(self.idleTimer, QtCore.SIGNAL('timeout()'), self.OnAppIdle)

	def OnDataReady(self, results, errorstr):
		# print len(results), errorstr
		try:
			if not errorstr:
				self.queryData=np.hstack( np.hstack( np.array( results ) ) )

				# self.errorPrefixLabel.setText("")
				self.setWindowTitle("Blockade Depth Histogram")
				self.queryErrorString=""
				self.statusbarLine.hide()
				self.errorLabel.setText(self.queryErrorString)

				self.lastGoodQueryString=self.queryString
				self.queryError=False
			else:
				# self.errorPrefixLabel.setText("  Query Error: ")
				self.setWindowTitle("Blockade Depth Histogram (QUERY ERROR)")
				# Set error line edit color to red
				self.errorLabel.setStyleSheet(css)
				self.queryErrorString=errorstr
				self.statusbarLine.show()
				self.errorLabel.setText(str(self.queryErrorString))
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
		self.update_graph()

	def OnAppIdle(self):
		t1=round(time.time())
		if not self.queryRunning and t1-self.lastQueryTime >= self.queryInterval:
			# self.lastQueryTime=t1
			self._updatequery()

	def OnProcessEvents(self):
		pass
		# QtGui.QApplication.sendPostedEvents()

if __name__ == '__main__':
	from os.path import expanduser
	# dbpath=expanduser('~')+'/Research/Experiments/Nanoclusters/PW9O34/20140916/m120mV1/'
	# dbpath=expanduser('~')+'/Research/Experiments/PEG29EBSRefData/20120323/singleChan/'
	# dbpath='C:\\temp\\'

	app = QtGui.QApplication(sys.argv)
	dmw = BlockDepthWindow()
	dmw.openDBFile('/Users/arvind/Desktop/untitled folder/eventMD-20140923-155414.sqlite')
	# dmw.openDB(dbpath)
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

