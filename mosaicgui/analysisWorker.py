# -*- coding: utf-8 -*-
import sys
import time
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt


class analysisWorker(QtCore.QObject):
	analysisFinished = QtCore.pyqtSignal(int)
	finished = QtCore.pyqtSignal()
	
	def __init__(self, analysisobj, **kwargs):
		super(analysisWorker, self).__init__(**kwargs)

		self.analysisObj=analysisobj

		self.idleTimer=QtCore.QTimer()
		self.idleTimer.start(5000)

		QtCore.QObject.connect(self.idleTimer, QtCore.SIGNAL('timeout()'), self.OnThreadIdle)

	def OnThreadIdle(self):
		if not self.analysisObj.subProc.is_alive():
			self.analysisFinished.emit(True)

	@QtCore.pyqtSlot()
	def startAnalysis(self):
		self.analysisObj.Run(forkProcess=True)

	@QtCore.pyqtSlot()
	def stopAnalysis(self):
		self.analysisObj.Stop()
		self.analysisFinished.emit(True)
