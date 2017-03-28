"""
	A module that plots MOSAIC time-series from a sqlite database.

	:Created:	3/27/2017
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		3/27/17		AB 	Initial version
"""
import mosaic.mdio.sqlite3MDIO as sqlite
from mosaic.utilities.sqlQuery import query, rawQuery

from mosaicweb.plotlyUtils import plotlyWrapper

import glob
import numpy as np
import pprint

class DataTypeNotSupportedError(Exception):
	pass

class analysisTimeSeries(dict):
	"""
		A class that plots MOSAIC time-series from a sqlite database.
	"""
	def __init__(self, analysisDB, index):
		self.analysisDB = analysisDB

		self.FsHz, self.procAlgorithm = rawQuery(self.analysisDB, "select FsHz, ProcessingAlgorithm from analysisinfo")[0]
		self.qstr="select ProcessingStatus, TimeSeries from metadata where RecIdx is {0}".format(index)

		self.returnMessageJSON={
			"warning": "",
			"recordCount": rawQuery(self.analysisDB, "select COUNT(recIDX) from metadata")[0][0],
			"eventNumber": index
		}

	def timeSeries(self):
		q=query(self.analysisDB, self.qstr)[0]
		decimate=self._calculateDecimation(len(q[1]))

		dt=(1./self.FsHz)*decimate

		ydat=np.array(q[1])
		polarity=float(np.sign(np.mean(ydat)))

		ydat=polarity*ydat[::decimate]
		xdat=np.arange(0, dt*len(ydat), dt)

		dat={}
		if q[0]=='normal':
			dat['data'] = [ plotlyWrapper.plotlyTrace(list(xdat), list(ydat), "NormalEvent") ]
		else:
			dat['data'] = [ plotlyWrapper.plotlyTrace(list(xdat), list(ydat), "ErrorEvent") ]

		dat['layout']=plotlyWrapper.plotlyLayout("EventViewLayout")
		dat['options']=plotlyWrapper.plotlyOptions()


		self.returnMessageJSON['eventViewPlot']=dat

		return self.returnMessageJSON

	def _calculateDecimation(self, dataLen):
		if dataLen < 500:
			return 1
		else:
			return int(round(dataLen/500.))

if __name__ == '__main__':
	import mosaic
	import time

	times=np.array([], dtype=np.float)
	for i in range(1,5000):
		t1=time.time()
		a=analysisTimeSeries(mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite",i)
		t=a.timeSeries()
		times=np.append(times, [(time.time()-t1)*1e3]) 

	print round(np.mean(times), 2), "+/-", round(np.std(times), 2), "ms"