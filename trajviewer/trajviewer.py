from __future__ import with_statement

import numpy as np
import sys
import os
import csv

from PyQt4 import QtCore
from PyQt4 import QtGui

import abfTrajIO as abf
import qdfTrajIO as qdf
from metaTrajIO import FileNotFoundError, EmptyDataPipeError

from trajviewerui import Ui_mplWindow

class DesignerMainWindow(QtGui.QMainWindow, Ui_mplWindow):

	def __init__(self, parent = None):
		self.v=[]

		super(DesignerMainWindow, self).__init__(parent)

		self.setupUi(self)

		QtCore.QObject.connect(self.startBtn, QtCore.SIGNAL("clicked()"), self.load_data)
		QtCore.QObject.connect(self.nextBtn, QtCore.SIGNAL("clicked()"), self.update_graph)
		QtCore.QObject.connect(self.pathBtn, QtCore.SIGNAL('clicked()'), self.select_path)

		self.nextBtn.setArrowType(QtCore.Qt.RightArrow)
		self.loadSettings()

		self.IOArgs={}


	def load_data(self):
		try:
			if self.path:
				if self.ftypeBox.currentText() == 'QDF':
					self.iohnd=qdf.qdfTrajIO
				else:
					self.iohnd=abf.abfTrajIO

				self.IOArgs['dirname']=str(self.path)
				self.IOArgs.update(self.parseFileOpts(str(self.fileoptsEdit.text())))

				if hasattr(self, 'IOObject'):
					self.IOOBject=None

				self.IOObject=self.iohnd(**self.IOArgs)
			
				# By default display 1 second of data
				self.nPoints=int(self.IOObject.FsHz)
				# Set a counter for number of updates
				self.nUpdate=0

				# save settings on load
				self.saveSettings()

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
			xdat=np.arange(float(self.nUpdate),float(self.nUpdate)+1.0,1/float(self.nPoints))
			ydat=self.IOObject.popdata(self.nPoints)

			self.mpl_hist.canvas.ax.set_xlabel('t (s)')
			self.mpl_hist.canvas.ax.set_ylabel('|i| (pA)')
			
			self.mpl_hist.canvas.ax.plot( xdat, ydat, 'b', markersize='1.')
			self.mpl_hist.canvas.draw()

			self.nUpdate+=1
		except EmptyDataPipeError:
			pass

	def select_path(self):
		fd=QtGui.QFileDialog()
		
		if self.pathEdit.text() != "":
			fd.setDirectory( self.pathEdit.text() )

		self.path=fd.getExistingDirectory()
		if self.path:
			self.pathEdit.setText(self.path)

	def parseFileOpts(self, str):
		if str=="":
			return {}

		d={}
		s=[ s.split('=') for s in str.split(',') ]
		[ d.update({ item[0].replace(' ','') : item[1].replace('\'','') }) for item in s ]
		return d

	def loadSettings(self):
		if os.path.isfile('.trajviewersettings'):
			with open('.trajviewersettings', 'rb') as csvfile:
				for row in csv.reader(csvfile, delimiter=','):
					if row[0] == "dataPath":
						self.path=str(row[1]).replace(' ', '')
						self.pathEdit.setText(self.path)
					elif row[0] == "fileOpts":
						if len(row) > 1:
							self.fileoptsEdit.setText( ','.join(row[1:]) )

	def saveSettings(self):
		settingsstr=""
		
		settingsstr+="dataPath,"+str(self.pathEdit.text())+"\n"
		settingsstr+="fileOpts,"+str(self.fileoptsEdit.text())

		with open('.trajviewersettings', "w") as settingsfile:
			settingsfile.write(settingsstr)

	def keyReleaseEvent(self, event):
		if event.key() == QtCore.Qt.Key_Right:
			if hasattr(self,'IOObject'):
				self.update_graph()
		
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = DesignerMainWindow()
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

