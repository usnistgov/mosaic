import json

import pyeventanalysis.settings

import pyeventanalysis.SingleChannelAnalysis
import pyeventanalysis.eventSegment

import pyeventanalysis.stepResponseAnalysis
import pyeventanalysis.multiStateAnalysis

import pyeventanalysis.qdfTrajIO
import pyeventanalysis.abfTrajIO

from pyeventanalysis.besselLowpassFilter import *
from pyeventanalysis.metaTrajIO import FileNotFoundError, EmptyDataPipeError

class guiDataModel(dict):
	def __init__(self):
		self["DataFilesType"]="ABF"
		self["DataFilesPath"]=""
		self["start"]=1
		self["dcOffset"]=0.0
		self["Rfb"]=0.0
		self["Cfb"]=0.0

		self._setupModelViews()
		self.UpdateDataModelFromSettings()

	def GenerateSettingsView(self, eventPartitionAlgo, eventProcessingAlgo):
		settingsdict={}
		
		partAlgo=self.eventPartitionAlgoKeys[eventPartitionAlgo]
		procAlgo=self.eventProcessingAlgoKeys[eventProcessingAlgo]

		if partAlgo=="eventSegment":
			settingsdict[partAlgo]={}
			partKeys=self.eventSegmentKeys
		if procAlgo=="stepResponseAnalysis":
			settingsdict[procAlgo]={}
			procKeys=self.stepResponseAnalysisKeys
		elif procAlgo=="multiStateAnalysis":
			settingsdict[procAlgo]={}
			procKeys=self.multiStateAnalysisKeys

		for k in partKeys.keys():
			settingsdict[partAlgo][k]=self[k]
		for k in procKeys.keys():
			settingsdict[procAlgo][k]=self[k]

		return json.dumps(settingsdict, indent=4)

	def GenerateTrajView(self):
		settingsdict={}
		for k, _t in self.trajviewerKeys.iteritems():
			settingsdict[k]=_t(self[k])

		return settingsdict		

	def GenerateAnalysisObject(self, eventPartitionAlgo, eventProcessingAlgo):
		return self.analysisSetupKeys["SingleChannelAnalysis"](
				self.GenerateDataFilesObject(),
				self.analysisSetupKeys[str(eventPartitionAlgo)],
				self.analysisSetupKeys[str(eventProcessingAlgo)]
			)

	def GenerateDataFilesObject(self):
		keys=["start", "dcOffset"]
		dargs={"dirname" : str(self["DataFilesPath"])}

		if self["DataFilesType"]=="QDF":
			keys.extend(["Rfb", "Cfb"])
			dargs.update({"filter"	: "*.qdf"})
		else:
			dargs.update({"filter"	: "*.abf"})

		for k in keys:
			dargs[k]=self.trajviewerKeys[k](self[k])

		return self.analysisSetupKeys[self["DataFilesType"]](**dargs)

	def UpdateDataModelFromSettings(self):
		if self["DataFilesPath"]:
			s=pyeventanalysis.settings.settings(self["DataFilesPath"])
		else:
			s=pyeventanalysis.settings.settings("..")

		for section, vals in s.settingsDict.iteritems():
			# print vals
			self.update(vals)

	def _setupModelViews(self):
		self.eventSegmentKeys={
								"blockSizeSec" 			: float,
								"eventPad" 				: int,
								"minEventLength" 		: int,
								"eventThreshold" 		: float,
								"driftThreshold" 		: float,
								"maxDriftRate" 			: float,
								"meanOpenCurr" 			: float,
								"sdOpenCurr"			: float,
								"slopeOpenCurr"			: float,
								"writeEventTS"			: int,
								"parallelProc"			: int,
								"reserveNCPU" 			: int,
								"plotResults" 			: int
							}
		self.stepResponseAnalysisKeys={
								"FitTol" 				: float,
								"FitIters" 				: int,
								"BlockRejectRatio" 		: float
							}
		self.multiStateAnalysisKeys=self.stepResponseAnalysisKeys

		self.besselLowpassFilterKeys={
								"filterOrder" 			: int,
								"filterCutoff" 			: float,
								"decimate" 				: int
							}

		self.trajviewerKeys={
								"DataFilesType" 		: str,
								"DataFilesPath" 		: str,
								"eventThreshold"		: float,
								"blockSizeSec" 			: float,
								"meanOpenCurr" 			: float,
								"sdOpenCurr" 			: float,
								"dcOffset" 				: float,
								"start" 				: int,
								"Rfb" 					: float,
								"Cfb" 					: float
							}
		self.eventPartitionAlgoKeys={
								"CurrentThreshold" 		: "eventSegment"
							}

		self.eventProcessingAlgoKeys={
								"stepResponseAnalysis" 	: "stepResponseAnalysis",
								"multiStateAnalysis" 	: "multiStateAnalysis"
							}

		self.analysisSetupKeys={
								"QDF" 					: pyeventanalysis.qdfTrajIO.qdfTrajIO,
								"ABF" 					: pyeventanalysis.abfTrajIO.abfTrajIO,
								"SingleChannelAnalysis" : pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis,
								"CurrentThreshold" 		: pyeventanalysis.eventSegment.eventSegment,
								"stepResponseAnalysis" 	: pyeventanalysis.stepResponseAnalysis.stepResponseAnalysis,
								"multiStateAnalysis" 	: pyeventanalysis.multiStateAnalysis.multiStateAnalysis
							}

if __name__ == "__main__":
	g=guiDataModel()

	g["DataFilesPath"]="/Users/arvind/Research/Experiments/PEG29EBSRefData/20120323/singleChan"
	g["DataFilesType"]="QDF"
	g["Rfb"]=9.1E+9
	g["Cfb"]=1.07E-12

	q=g.GenerateDataFilesObject()
	print q.formatsettings()
	print q.popdata(10)


	print g.GenerateSettingsView("CurrentThreshold", "stepResponseAnalysis")
	print g.GenerateTrajView()
	# for k,v in g.iteritems():
	# 	print k, "=", v