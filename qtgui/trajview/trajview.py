from __future__ import with_statement

import numpy as np
import sys
import os
import csv

from PyQt4 import QtCore, QtGui, uic

import pyeventanalysis.abfTrajIO as abf
import pyeventanalysis.qdfTrajIO as qdf
from pyeventanalysis.metaTrajIO import FileNotFoundError, EmptyDataPipeError

import matplotlib.ticker as ticker
# from qtgui.trajview.trajviewui import Ui_Dialog

class TrajectoryWindow(QtGui.QDialog):

	def __init__(self, parent = None):
		self.v=[]

		super(TrajectoryWindow, self).__init__(parent)

		uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"trajviewui.ui"), self)
		# self.setupUi(self)
		self._positionWindow()

		QtCore.QObject.connect(self.nextBtn, QtCore.SIGNAL("clicked()"), self.OnNextButton)
		self.nextBtn.setArrowType(QtCore.Qt.RightArrow)

		self.trajData=""


		# Set a counter for number of updates
		self.blockSize=0.25
		self.nUpdate=0
		self.nPoints=0
		self.dataLoaded=False

		# Temp vars
		self.mu_line = None
		self.thr_line = None

		self.IOObject=None
		self.IOArgs={}


	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		screen = QtGui.QDesktopWidget().screenGeometry()
		self.setGeometry(405, 0, 500, 350)
		# self.move( (-screen.width()/2)+200, -screen.height()/2 )


	def refreshPlot(self):
		try:
			path=str(self.datadict["DataFilesPath"])
			if path:
				self.IOArgs['dirname']=path
				if self.datadict["DataFilesType"] == 'QDF':
					self.iohnd=qdf.qdfTrajIO

					self.IOArgs["filter"]="*qdf"
					self.IOArgs["Rfb"]=self.datadict["Rfb"]
					self.IOArgs["Cfb"]=self.datadict["Cfb"]
				else:
					self.iohnd=abf.abfTrajIO	

					self.IOArgs["filter"]="*abf"

				# self.IOArgs["start"]=int(self.datadict["start"])
				self.IOArgs["dcOffset"]=float(self.datadict["dcOffset"])

				if hasattr(self, 'IOObject'):
					self.IOOBject=None

				# if self.IOObject:
				# 	del self.IOObject

				# print self.IOArgs
				# print self.iohnd
				self.IOObject=self.iohnd(**self.IOArgs)

				# By default display 250 ms second of data
				self.nPoints=int(self.blockSize*self.IOObject.FsHz)
				self.nUpdate=0
				self.trajData=self.IOObject.popdata(self.nPoints)

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

  	def updatePlot(self, datadict):
  		self.datadict=datadict
  		# print self.datadict
  		# set block size
  		self.blockSize=self.datadict.pop( "blockSizeSec", 0.25)

  		# self.mpl_hist.canvas.ax.set_autoscale_on(False)
  		self.update_graph()

  	def setTrajdata(self, datadict):
  		self.datadict=datadict

  		# set block size
  		self.blockSize=self.datadict.pop( "blockSizeSec", 0.25)

	def update_graph(self):
		try:
			if self.dataLoaded:
				ydat=np.abs(self.trajData)
				xdat=np.arange(float(self.nUpdate)*self.blockSize,float(self.nUpdate+1)*self.blockSize,1/float(self.IOObject.FsHz))[:len(ydat)]
	
				c='#%02x%02x%02x' % (72,91,144)
				self.mpl_hist.canvas.ax.plot( xdat, ydat, color=c, markersize='1.')
				if float(self.datadict["meanOpenCurr"]) == -1 and float(self.datadict["sdOpenCurr"]) == -1:
					mu=np.mean(ydat)
					sd=np.std(ydat)
				else:
					mu=abs(float(self.datadict["meanOpenCurr"]))
					sd=float(self.datadict["sdOpenCurr"])

				thr=float(self.datadict["eventThreshold"])

				# display the mean current val and thr
				self.ionicCurrentLabel.setText(
					"Mean: {0:.2f} pA\tStd. Dev: {1:.2f} pA\tThreshold: {2:.2f} pA".format(mu, sd, mu-thr*sd)
					)

				self.mu_line = self.mpl_hist.canvas.ax.axhline(mu, color='0.75', linestyle='--', lw=1.5)
				c='#%02x%02x%02x' % (182,69,71)
				self.mpl_hist.canvas.ax.axhline(mu-thr*sd, color=c, lw=1.5)

				self._ticks(5)

				self.mpl_hist.canvas.ax.set_xlabel('t (s)', fontsize=10)
				self.mpl_hist.canvas.ax.set_ylabel('|i| (pA)', fontsize=10)
			
				self.mpl_hist.canvas.draw()

				#update the window title
				self._windowtitle()

		except EmptyDataPipeError:
			pass

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

	def OnNextButton(self):
		if hasattr(self,'IOObject'):
			# pop more data on key press
			try:
				self.trajData=self.IOObject.popdata(self.nPoints)
				self.nUpdate+=1

				# self.mpl_hist.canvas.ax.set_autoscale_on(False)
				self.update_graph()
			except EmptyDataPipeError:
				pass

	def keyReleaseEvent(self, event):
		if event.key() == QtCore.Qt.Key_Right:
			self.OnNextButton()
		
	def _windowtitle(self):
		try:
			fname = self.IOObject.LastDataFile.split('/')[-1]		# *nixes
		except IndexError:
			fname = self.IOObject.LastDataFile.split('\\')[-1]		# windows

		self.setWindowTitle(fname)

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = TrajectoryWindow()
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

