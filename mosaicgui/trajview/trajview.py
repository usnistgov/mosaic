from __future__ import with_statement

import numpy as np
import sys
import os
import csv

from PyQt4 import QtCore, QtGui, uic

import mosaic.trajio.abfTrajIO as abf
import mosaic.trajio.qdfTrajIO as qdf
import mosaic.trajio.binTrajIO as bin
import mosaic.trajio.tsvTrajIO as tsv
import mosaic.trajio.chimeraTrajIO as chimera
from mosaic.trajio.metaTrajIO import FileNotFoundError, EmptyDataPipeError
from mosaic.utilities.resource_path import resource_path
from mosaic.utilities.ionic_current_stats import OpenCurrentDist

import matplotlib.ticker as ticker
from matplotlib import pylab as plt
# from mosaicgui.trajview.trajviewui import Ui_Dialog

class TrajectoryWindow(QtGui.QDialog):

	def __init__(self, parent = None):
		self.v=[]

		super(TrajectoryWindow, self).__init__(parent)

		uic.loadUi(resource_path("trajviewui.ui"), self)
		
		# Add a toolbar the matplolib widget
		self.mpl_hist.addToolbar()

		self._positionWindow()

		QtCore.QObject.connect(self.nextBtn, QtCore.SIGNAL("clicked()"), self.OnNextButton)
		self.nextBtn.setArrowType(QtCore.Qt.RightArrow)

		self.trajData=""
		self.trajDataDenoise=""


		# Set a counter for number of updates
		self.blockSize=0.25
		self.nUpdate=0
		self.nPoints=0
		self.dataLoaded=False

		# Temp vars
		self.mu_line = None
		self.thr_line = None

		self.IOObject=None
		self.DenoiseIOObj=None
		self.IOArgs={}


	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		if sys.platform=='win32':
			self.setGeometry(425, 30, 500, 400)
		else:
			self.setGeometry(405, 0, 500, 400)

	@property
	def FskHz(self):
		if self.IOObject:
			return self.IOObject.FsHz/1000.
		else:
			return 0.0
	
	@property 
	def meanCurr(self):
		return self.mu

	@property 
	def sdCurr(self):
		return self.sd

	@property 
	def thrCurr(self):
		return self.thrCurrPicoA

	def refreshPlot(self):
		try:
			path=str(self.datadict["DataFilesPath"])
			if path:
				self.IOArgs['dirname']=path
				if self.datadict["DataFilesType"] == 'QDF':
					self.iohnd=qdf.qdfTrajIO

					self.IOArgs["filter"]=self.datadict["filter"]
					self.IOArgs["Rfb"]=self.datadict["Rfb"]
					self.IOArgs["Cfb"]=self.datadict["Cfb"]
					self.IOArgs["format"]=self.datadict["format"]
				elif self.datadict["DataFilesType"] ==  "BIN":
					self.iohnd=bin.binTrajIO

					self.IOArgs["AmplifierScale"]=self.datadict["AmplifierScale"]
					self.IOArgs["AmplifierOffset"]=self.datadict["AmplifierOffset"]
					self.IOArgs["SamplingFrequency"]=self.datadict["SamplingFrequency"]
					self.IOArgs["ColumnTypes"]=self.datadict["ColumnTypes"]
					self.IOArgs["IonicCurrentColumn"]=self.datadict["IonicCurrentColumn"]
					self.IOArgs["HeaderOffset"]=self.datadict["HeaderOffset"]
					self.IOArgs["filter"]=self.datadict["filter"]
				elif self.datadict["DataFilesType"] ==  "TSV":
					self.iohnd=tsv.tsvTrajIO

					try:
						self.IOArgs["filter"]=self.datadict["filter"]
						self.IOArgs["headers"]=self.datadict["headers"]

						self.IOArgs["nCols"]=self.datadict["nCols"]
						self.IOArgs["timeCol"]=self.datadict["timeCol"]
						self.IOArgs["currCol"]=self.datadict["currCol"]
					except:
						self.IOArgs["Fs"]=self.datadict["Fs"]

					try:
						self.IOArgs["scale"]=self.datadict["scale"]
					except:
						self.IOArgs["scale"]=1
                                elif self.datadict["DataFilesType"] ==  "LOG":
					self.iohnd=chimera.chimeraTrajIO

                                        self.IOArgs["mVoffset"]=self.datadict["mVoffset"]
                                        self.IOArgs["ADCvref"]=self.datadict["ADCvref"]
                                        self.IOArgs["ADCbits"]=self.datadict["ADCbits"]
                                        self.IOArgs["TIAgain"]=self.datadict["TIAgain"]
                                        self.IOArgs["preADCgain"]=self.datadict["preADCgain"]
                                        self.IOArgs["pAoffset"]=self.datadict["pAoffset"]
					self.IOArgs["SamplingFrequency"]=self.datadict["SamplingFrequency"]
					self.IOArgs["ColumnTypes"]=self.datadict["ColumnTypes"]
					self.IOArgs["IonicCurrentColumn"]=self.datadict["IonicCurrentColumn"]
					self.IOArgs["HeaderOffset"]=self.datadict["HeaderOffset"]
					self.IOArgs["filter"]=self.datadict["filter"]
				else:
					self.iohnd=abf.abfTrajIO	
					self.IOArgs["filter"]=self.datadict["filter"]

				self.IOArgs["start"]=int(self.datadict["start"])
				self.IOArgs["dcOffset"]=float(self.datadict["dcOffset"])

				if hasattr(self, 'IOObject'):
					self.IOObject=None

				self.IOObject=self.iohnd(**self.IOArgs)

				# By default display 250 ms second of data
				self.nPoints=int(self.blockSize*self.IOObject.FsHz)
				self.nUpdate=0

				self._loaddata()

				self.dataLoaded=True

				if self.DenoiseIOObj:
  					# set the max level value in the level spinner
					self.waveletLevelSpinBox.setMaximum(int(self.DenoiseIOObj.dataFilterObj.maxWaveletLevel))

				self.update_graph()
		except AttributeError:
			QtGui.QMessageBox.warning(self, "Path Error","Data path not set")
			raise
		except FileNotFoundError:
			print self.IOArgs
			QtGui.QMessageBox.warning(self, "Data Error", "No data files found in " + path)
		except:
			raise

  	def updatePlot(self, datadict):
  		self.datadict=datadict

  		# set block size
  		self.blockSize=self.datadict.pop( "blockSizeSec", 0.25)
  		self.thrCurrPicoA=self.datadict.pop("eventThresholdpA",0.0)

  		self.update_graph()

  	def setTrajdata(self, datadict, denoiseobj):
  		self.datadict=datadict
  		self.DenoiseIOObj=denoiseobj

  		# set block size
  		self.blockSize=self.datadict.pop( "blockSizeSec", 0.25)
  		self.thrCurrPicoA=self.datadict.pop("eventThresholdpA",0.0)

	def update_graph(self):
		try:
			if self.dataLoaded:

				print self.trajData[:10]


				datasign=float(np.sign(np.mean(self.trajData)))
				ydat=datasign*np.array(self.trajData, dtype='float64')
				xdat=np.arange(float(self.nUpdate)*self.blockSize,float(self.nUpdate+1)*self.blockSize,self.decimate/float(self.IOObject.FsHz))[:len(ydat)]
	
				self._calculateThreshold(ydat)

				# display the mean current val and thr
				self.ionicCurrentLabel.setText( 
						"&#12296;<i>i<sub>0</sub></i>&#12297;={0:.1f} pA, \
						&#963;<sub>i<sub>0</sub></sub>={1:.1f} pA<br><br>\
						Threshold={2:.1f} pA ({3:.2f}&#963;<sub>i<sub>0</sub></sub>)".format(self.mu, self.sd, self.mu-self.thr*self.sd, self.thr) 
					)

				# plot data
				if self.DenoiseIOObj:
					c='0.65'
					cd='#%02x%02x%02x' % (72,91,144)
					self.mpl_hist.canvas.ax.cla()
					self.mpl_hist.canvas.ax.hold(True)

					self.mpl_hist.canvas.ax.plot( xdat, ydat, color=c, markersize='1.')

					ydatd=np.abs(self.trajDataDenoise)
					self.mpl_hist.canvas.ax.plot( xdat, ydatd,  markersize='1.')

					self.mpl_hist.canvas.ax2.cla()
					self.mpl_hist.canvas.ax2.hold(True)
					self.mpl_hist.canvas.ax2.hist( 
						ydat, 
						bins=400, 
						normed=1, 
						histtype='step',
						rwidth=0.1,
						color=c,
						orientation='horizontal'
					)
					self.mpl_hist.canvas.ax2.hist( 
						ydatd, 
						bins=200, 
						normed=1, 
						histtype='step',
						rwidth=0.1,
						color=cd,
						orientation='horizontal'
					)
				else:					
					c='#%02x%02x%02x' % (72,91,144)
					self.mpl_hist.canvas.ax.cla()
					self.mpl_hist.canvas.ax.plot( xdat, ydat, markersize='1.')

					self.mpl_hist.canvas.ax2.cla()
					
					hist, bins=np.histogram(
						ydat, 
						bins=200, 
						normed=1
					)
					self.mpl_hist.canvas.ax2.plot ( hist, bins[:-1]	)


				self.mu_line = self.mpl_hist.canvas.ax.axhline(self.mu, color='0.5', linestyle='--', lw=1.5)
				cl='#%02x%02x%02x' % (182,69,71)
				self.mpl_hist.canvas.ax.axhline(self.mu-self.thr*self.sd, color='#DB5E00', lw=1.5)

				self.mu_line = self.mpl_hist.canvas.ax2.axhline(self.mu, color='0.5', linestyle='--', lw=1.5)
				self.mpl_hist.canvas.ax2.axhline(self.mu-self.thr*self.sd, color='#DB5E00', lw=1.5)

				plt.setp( self.mpl_hist.canvas.ax2.get_xticklabels(), visible=False)
				plt.setp( self.mpl_hist.canvas.ax2.get_yticklabels(), visible=False)
				

				ilabel={1:'i', -1:'-i', 0:'i'}[int(datasign)]
				self.mpl_hist.canvas.ax.set_xlabel('t (s)', fontsize=12)
				self.mpl_hist.canvas.ax.set_ylabel(ilabel+' (pA)', fontsize=12)
			
				self.mpl_hist.canvas.draw()

				#update the window title
				self._windowtitle()

		except EmptyDataPipeError:
			pass

	def _calculateThreshold(self, dat):
		if float(self.datadict["meanOpenCurr"]) == -1 or float(self.datadict["sdOpenCurr"]) == -1:
			try:
				self.mu, self.sd = OpenCurrentDist(dat, 0.5)
				if self.thrCurrPicoA==0.:
					self.thr=float(self.datadict["eventThreshold"])

					# if eventThresholdpA is not set, the program was initialized with 
					# baseline auto. Store the threshold current in pA in self.thrCurrPicoA.
					# The settings window will then pick it up on the first controls update.
					self.thrCurrPicoA=self.mu-self.sd*self.thr
				else:
					# If self.thrCurrPicoA is set, then calculate a new threshold in SD 
					# so as to keep self.thrCurrPicoA constant.
					self.thr=(self.mu-self.thrCurrPicoA)/self.sd
			except AttributeError:
				self.mu, self.sd = OpenCurrentDist(dat, 0.5)
				self.thr=(self.mu-self.thrCurrPicoA)/self.sd
		else:
			self.mu=abs(float(self.datadict["meanOpenCurr"]))
			self.sd=float(self.datadict["sdOpenCurr"])
			self.thr=(self.mu-self.thrCurrPicoA)/self.sd

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
				self._loaddata()
				self.nUpdate+=1

				self.update_graph()
			except EmptyDataPipeError:
				pass

	def DenoiseWarning(self):
		denoiseWarnBox = QtGui.QMessageBox(parent=self)
		denoiseWarnBox.setText('Denoising is an experimental feature. Do you want to continue?')
		denoiseWarnBox.setIcon(QtGui.QMessageBox.Warning)
		denoiseWarnBox.addButton(QtGui.QPushButton('Yes'), QtGui.QMessageBox.YesRole)
		denoiseWarnBox.addButton(QtGui.QPushButton('No'), QtGui.QMessageBox.RejectRole)
		
		return denoiseWarnBox.exec_()


	def keyReleaseEvent(self, event):
		if event.key() == QtCore.Qt.Key_Right:
			self.OnNextButton()
		
	def _loaddata(self):
		tdat=self.IOObject.popdata(self.nPoints)
		self.decimate=max(1, int(round(len(tdat)/5e5)))
		
		self.trajData=tdat[::self.decimate]

		if self.DenoiseIOObj:
			tdatdenoise=self.DenoiseIOObj.popdata(self.nPoints)
			self.trajDataDenoise=tdatdenoise[::self.decimate]

	def _windowtitle(self):
		try:
			fname = self.IOObject.LastFileProcessed.split('/')[-1]		# *nixes
		except IndexError:
			fname = self.IOObject.LastFileProcessed.split('\\')[-1]		# windows

		self.setWindowTitle(fname)

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = TrajectoryWindow()
	dmw.show()
	dmw.raise_()
	print dmw.DenoiseWarning()
	sys.exit(app.exec_())

