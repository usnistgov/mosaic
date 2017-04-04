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
import mosaic.errors as errors
import mosaic.utilities.fit_funcs as fit_funcs

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
		self.qstr=""

		self.errTextObject=errors.errors()

		self.returnMessageJSON={
			"warning": "",
			"recordCount": rawQuery(self.analysisDB, "select COUNT(recIDX) from metadata")[0][0],
			"eventNumber": index,
			"errorText": ""
		}

		# setup hash tables and funcs used in this class
		self._setupDict(index)
		self._setupFitFuncs()



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
			if self.fitFuncHnd:
				# xfit=np.arange(0,float((len(q[1]))/self.FsHz), float(1/(100*self.FsHz)))
				xfit=np.arange(0, dt*len(ydat), dt)
				yfit=self.fitFuncHnd( *eval(self.fitFuncArgs) )

			if self.stepFuncHnd:
				# xstep=np.arange(0,float((len(q[1]))/self.FsHz), float(1/(100*self.FsHz)))
				xstep=np.arange(0, dt*len(ydat), dt)
				ystep=self.stepFuncHnd( *eval(self.stepFuncArgs) )

			dat['data'] = [ 
						plotlyWrapper.plotlyTrace(list(xdat), list(ydat), "NormalEvent"),
						plotlyWrapper.plotlyTrace(list(xfit), list(yfit), "NormalEventFit"),
						plotlyWrapper.plotlyTrace(list(xstep), list(ystep), "NormalEventStep")
					]
		elif q[0].startswith('w'):
			dat['data'] = [ plotlyWrapper.plotlyTrace(list(xdat), list(ydat), "WarnEvent") ]
			self.returnMessageJSON['errorText']="WARNING: "+self.errTextObject[q[0]]
		else:
			dat['data'] = [ plotlyWrapper.plotlyTrace(list(xdat), list(ydat), "ErrorEvent") ]
			self.returnMessageJSON['errorText']="ERROR: "+self.errTextObject[q[0]]

		dat['layout']=plotlyWrapper.plotlyLayout("EventViewLayout")
		dat['options']=plotlyWrapper.plotlyOptions()


		self.returnMessageJSON['eventViewPlot']=dat

		return self.returnMessageJSON

	def _calculateDecimation(self, dataLen):
		if dataLen < 500:
			return 1
		else:
			return int(round(dataLen/500.))

	def _setupFitFuncs(self):	
		# Generate the query string based on the algorithm in the database
		self.qstr=self.queryStringDict[self.procAlgorithm]

		# Setup the fit function based on the algorithm
		self.fitFuncHnd=self.fitFuncHndDict[self.procAlgorithm]
		self.fitFuncArgs=self.fitFuncArgsDict[self.procAlgorithm]

		self.stepFuncHnd=self.stepFuncHndDict[self.procAlgorithm]
		self.stepFuncArgs=self.stepFuncArgsDict[self.procAlgorithm]

		self.bdFuncArgs=self.blockDepthArgsDict[self.procAlgorithm]

	def _setupDict(self, eventNumber):
		self.queryStringDict={
			"adept2State" 	: "select ProcessingStatus, TimeSeries, RCConstant1, RCConstant2, EventStart, EventEnd, BlockedCurrent, OpenChCurrent from metadata  where RecIdx is {0}".format(eventNumber),
			"adept" 		: "select ProcessingStatus, TimeSeries, RCConstant, EventDelay, CurrentStep, OpenChCurrent from metadata  where RecIdx is {0}".format(eventNumber),
			"cusumPlus" 	: "select ProcessingStatus, TimeSeries, EventDelay, CurrentStep, OpenChCurrent from metadata  where RecIdx is {0}".format(eventNumber)
		}

		self.fitFuncHndDict={
			"adept2State" 	: fit_funcs.stepResponseFunc,
			"adept" 		: fit_funcs.multiStateFunc,
			"cusumPlus" 	: None
		}

		self.fitFuncArgsDict={
			"adept2State" 	: "[xfit*1000, q[2], q[3], q[4], q[5], abs(q[7]-q[6]), q[7]]",
			"adept" 		: "[xfit*1000, q[2], q[3], q[4], q[5], len(q[3])]",
			"cusumPlus" 	: "[]"
		}

		self.stepFuncHndDict={
			"adept2State" 	: fit_funcs.multiStateStepFunc,
			"adept" 		: fit_funcs.multiStateStepFunc,
			"cusumPlus"		: fit_funcs.multiStateStepFunc
		}

		self.stepFuncArgsDict={
			"adept2State" 	: "[xstep*1000, [q[4], q[5]], [-abs(q[7]-q[6]), abs(q[7]-q[6])], q[7], 2]",
			"adept" 		: "[xstep*1000, q[3], q[4], q[5], len(q[3])]",
			"cusumPlus" 	: "[xstep*1000, q[2], q[3], q[4], len(q[2])]"
		}

		self.blockDepthArgsDict={
			"adept2State" 	: "[[-abs(q[7]-q[6])], q[7], [q[4],q[5]], 1]",
			"adept" 		: "[q[4], q[5], q[3], len(q[3])-1]",
			"cusumPlus" 	: "[q[3], q[4], q[2], len(q[2])-1]"
		}

if __name__ == '__main__':
	import mosaic
	import time

	for i in range(1,1000):
		a=analysisTimeSeries(mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite", i)
		t=a.timeSeries()
		if t["errorText"] != "":
			print i, t["errorText"]

	times=np.array([], dtype=np.float)
	for i in range(1,1000):
		t1=time.time()
		a=analysisTimeSeries(mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite",i)
		t=a.timeSeries()
		times=np.append(times, [(time.time()-t1)*1e3]) 

	print round(np.mean(times), 2), "+/-", round(np.std(times), 2), "ms"