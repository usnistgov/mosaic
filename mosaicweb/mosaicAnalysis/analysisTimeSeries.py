"""
	A module that plots MOSAIC time-series from a sqlite database.

	:Created:	3/27/2017
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		10/29/18 	AB 	Replace eval statements with static functions.
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
class EmptyEventFilterError(Exception):
	pass
class EndOfDataError(Exception):
	pass

class analysisTimeSeries(dict):
	"""
		A class that plots MOSAIC time-series from a sqlite database.
	"""
	def __init__(self, analysisDB, index, eventFilter):
		self.analysisDB = analysisDB
		self.eventFilter=eventFilter

		if len(eventFilter)==0:
			raise EmptyEventFilterError

		self.FsHz, self.procAlgorithm = rawQuery(self.analysisDB, "select FsHz, ProcessingAlgorithm from analysisinfo")[0]
		self.errTextObject=errors.errors()
		self.recordCount=0

		# setup hash tables and funcs used in this class
		self.qstr=self._generateQueryString(index)
		
		self.returnMessageJSON={
			"warning": "",
			"recordCount": self.recordCount,
			"eventNumber": index,
			"errorText": ""
		}


	def timeSeries(self):
		try:
			q=query(self.analysisDB, self.qstr)[0]
			decimate=self._calculateDecimation(len(q[1]))

			dt=(1./self.FsHz)*decimate

			ydat=np.array(q[1]).astype(np.float64)
			polarity=float(np.sign(np.mean(ydat)))

			ydat=polarity*ydat[::decimate]
			xdat=np.arange(0, dt*len(ydat), dt)

			dat={}
			if q[0]=='normal': 
				if self.procAlgorithm!="cusumPlus":
					xfit=np.arange(0, dt*len(ydat), dt)
					yfit=self._evalFitFunction(xdat*1000, q)

				xstep=np.arange(0, dt*len(ydat), dt)
				ystep=self._evalStepFunction(xdat*1000, q)

				if self.procAlgorithm!="cusumPlus":
					dat['data'] = [ 
							plotlyWrapper.plotlyTrace(list(xdat), list(ydat), "NormalEvent"),
							plotlyWrapper.plotlyTrace(list(xfit), list(yfit), "NormalEventFit"),
							plotlyWrapper.plotlyTrace(list(xstep), list(ystep), "NormalEventStep")
						]
				else:
					dat['data'] = [ 
							plotlyWrapper.plotlyTrace(list(xdat), list(ydat), "NormalEvent"),
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

			self.returnMessageJSON['parameterTable']=self._paramTable(q)

			return self.returnMessageJSON
		except IndexError:
			raise EndOfDataError

	def _calculateDecimation(self, dataLen):
		if dataLen < 1000:
			return 1
		else:
			return int(round(dataLen/500.))

	def _evalFitFunction(self, xdat, q):
		if self.procAlgorithm=="adept2State":
			return fit_funcs.stepResponseFunc(xdat, q[2], q[3], q[4], q[5], abs(q[7]-q[6]), q[7])
		elif self.procAlgorithm=="adept":
			return fit_funcs.multiStateFunc(xdat, q[2], q[3], q[4], q[5], len(q[3]))
		else:
			return None

	def _evalStepFunction(self, xdat, q):
		if self.procAlgorithm=="adept2State":
			return fit_funcs.multiStateStepFunc(xdat, [q[4], q[5]], [-abs(q[7]-q[6]), abs(q[7]-q[6])], q[7], 2)
		elif self.procAlgorithm=="adept":
			return fit_funcs.multiStateStepFunc(xdat, q[3], q[4], q[5], len(q[3]))
		elif self.procAlgorithm=="cusumPlus":
			return fit_funcs.multiStateStepFunc(xdat, q[2], q[3], q[4], len(q[2]))
		else:
			return None

	def _generateQueryString(self, eventNumber):
		# Generate the query string based on the algorithm in the database
		queryStringDict={
			"adept2State" 	: "select ProcessingStatus, TimeSeries, RCConstant1, RCConstant2, EventStart, EventEnd, BlockedCurrent, OpenChCurrent from metadata",
			"adept" 		: "select ProcessingStatus, TimeSeries, RCConstant, EventDelay, CurrentStep, OpenChCurrent from metadata",
			"cusumPlus" 	: "select ProcessingStatus, TimeSeries, EventDelay, CurrentStep, OpenChCurrent from metadata"
		}
		
		eventFilterCode={
			"normal"		: "normal",
			"warning"		: "w%",
			"error"			: "e%"
		}

		typeClause=" or ".join([ "ProcessingStatus like '{0}'".format(eventFilterCode[eventType]) for eventType in self.eventFilter ])

		self.recordCount=rawQuery(self.analysisDB, "select COUNT(recIDX) from metadata where "+typeClause)[0][0]

		qstr=queryStringDict[self.procAlgorithm]+ " where " + typeClause +" limit 1 offset {0}".format(eventNumber-1)

		return qstr

	def _paramTable(self, q):
		if self.procAlgorithm=="adept2State":
			[currentStep, openChCurr, eventDelay, nStates]=[[-abs(q[7]-q[6])], q[7], [q[4],q[5]], 1]
		elif self.procAlgorithm=="adept":
			[currentStep, openChCurr, eventDelay, nStates]=[q[4], q[5], q[3], len(q[3])-1]
		elif self.procAlgorithm=="cusumPlus":
			[currentStep, openChCurr, eventDelay, nStates]=[q[3], q[4], q[2], len(q[2])-1]


		paramList=[]

		# nStates=[ str(i) for i in range(1, nStates+1)]
		blockDepth=[ str(round(bd, 4)) for bd in (np.cumsum(np.array([openChCurr]+currentStep))[1:])/openChCurr][:nStates]
		resTimes=[ str(round(rt, 2)) for rt in np.diff(eventDelay)*1000. ]

		for i in range(nStates):
			paramList.append(
				{
					"index" : i+1,
					"blockDepth" : blockDepth[i],
					"resTime" : resTimes[i]
				}
			)

		return paramList

if __name__ == '__main__':
	import mosaic
	import time

	for i in range(1,10):
		a=analysisTimeSeries(mosaic.WebServerDataLocation+"/Google Drive File Stream/My Drive/ReferenceData/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite", i, ['normal'])
		t=a.timeSeries()
		print(t["eventNumber"], t["parameterTable"],t["eventViewPlot"])
		if t["errorText"] != "":
			print( i, t["errorText"] )

	# times=np.array([], dtype=np.float)
	# for i in range(1,10):
	# 	t1=time.time()
	# 	a=analysisTimeSeries(mosaic.WebServerDataLocation+"/Google Drive File Stream/My Drive/ReferenceData/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite",i, ['normal'])
	# 	t=a.timeSeries()
	# 	times=np.append(times, [(time.time()-t1)*1e3]) 

	# print( round(np.mean(times), 2), "+/-", round(np.std(times), 2), "ms" )