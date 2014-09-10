import json

import pyeventanalysis.settings

import pyeventanalysis.SingleChannelAnalysis
import pyeventanalysis.eventSegment

import pyeventanalysis.stepResponseAnalysis
# import pyeventanalysis.multiStateAnalysis

import pyeventanalysis.qdfTrajIO
import pyeventanalysis.abfTrajIO

from pyeventanalysis.besselLowpassFilter import *
import pyeventanalysis.waveletDenoiseFilter
from pyeventanalysis.metaTrajIO import FileNotFoundError, EmptyDataPipeError

class guiDataModel(dict):
	def __init__(self):
		self._setupModelViews()


		self["DataFilesType"]="ABF"
		self["DataFilesPath"]=""
		self["start"]=0.
		self["end"]=-1
		self["dcOffset"]=0.0
		self["Rfb"]=0.0
		self["Cfb"]=0.0

		self.jsonSettingsObj=None

		self.UpdateDataModelFromSettings()

	def __setitem__(self, key, val):
		dat=val

		# Add special rules to modify data here
		# if key == "start":		# the start index cannot be set to 0
		# 	if val == 0:
		# 		dat=1

		try:
			dict.__setitem__(self, key, self.keyTypesDict[key](dat) )
		except KeyError:
			dict.__setitem__(self, key, dat )

	def __getitem__(self, key):
		return dict.__getitem__(self, key)

	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v

	def GenerateSettingsView(self, eventPartitionAlgo, eventProcessingAlgo, dataFilterAlgo):
		settingsdict={}
		
		partAlgo=self.eventPartitionAlgoKeys[eventPartitionAlgo]
		procAlgo=self.eventProcessingAlgoKeys[eventProcessingAlgo]

		if partAlgo=="eventSegment":
			settingsdict[partAlgo]={}
			partKeys=self.eventSegmentKeys

		if procAlgo=="stepResponseAnalysis":
			settingsdict[procAlgo]={}
			procKeys=self.stepResponseAnalysisKeys
		# elif procAlgo=="multiStateAnalysis":
		# 	settingsdict[procAlgo]={}
		# 	procKeys=self.multiStateAnalysisKeys

		# Add a section for data files
		settingsdict[self.dataTypeKeys[self["DataFilesType"]]]=self.GenerateDataFilesView()
		# print self.dataTypeKeys[self["DataFilesType"]]
		# print self.GenerateDataFilesView(dataFilterAlgo)
		# print settingsdict

		for k in partKeys.keys():
			settingsdict[partAlgo][k]=self[k]
		for k in procKeys.keys():
			settingsdict[procAlgo][k]=self[k]

		# Lastly check if data filtering is enabled
		if dataFilterAlgo:
			filterAlgo=self.filterAlgoKeys[dataFilterAlgo]
			if filterAlgo=="waveletDenoiseFilter":
				settingsdict[filterAlgo]={}
				for k in self.denoiseFilterKeys.keys():
					settingsdict[filterAlgo][k]=self[k]
		
		return json.dumps(settingsdict, indent=4)

	def GenerateTrajView(self):
		settingsdict={}
		for k in self.trajviewerKeys.keys():
			settingsdict[k]=self[k]

		return settingsdict		

	def GenerateDataFilesView(self):
		keys=["start", "dcOffset"]
		dargs={"dirname" : str(self["DataFilesPath"])}

		if self["DataFilesType"]=="QDF":
			keys.extend(["Rfb", "Cfb"])
			dargs.update({"filter"	: "*.qdf"})
		else:
			dargs.update({"filter"	: "*.abf"})

		if self["end"]!=-1.:
			dargs["end"]=self["end"]

		for k in keys:
			dargs[k]=self.trajviewerKeys[k](self[k])

		return dargs

	def GenerateAnalysisObject(self, eventPartitionAlgo, eventProcessingAlgo, dataFilterAlgo):
		return self.analysisSetupKeys["SingleChannelAnalysis"](
				self.GenerateDataFilesObject(dataFilterAlgo),
				self.analysisSetupKeys[str(eventPartitionAlgo)],
				self.analysisSetupKeys[str(eventProcessingAlgo)]
			)

	def GenerateDataFilesObject(self, dataFilterAlgo):
		dargs=self.GenerateDataFilesView()

		if dataFilterAlgo:
			dargs["datafilter"]=self.analysisSetupKeys[str(dataFilterAlgo)]

		return self.analysisSetupKeys[self["DataFilesType"]](**dargs)

	def UpdateDataModelFromSettings(self):
		if self["DataFilesPath"]:
			self.jsonSettingsObj=pyeventanalysis.settings.settings(self["DataFilesPath"])
		else:
			self.jsonSettingsObj=pyeventanalysis.settings.settings(".")

		self._updateSettings()

	def UpdateDataModelFromSettingsString(self, settingsstr):
		if not self.jsonSettingsObj:
			self.UpdateDataModelFromSettings()

		self.jsonSettingsObj.parseSettingsString(settingsstr)

		self._updateSettings()

	def _updateSettings(self):
		sd=self.jsonSettingsObj.settingsDict
		
		for section, vals in sd.iteritems():
			if section in self.eventPartitionAlgoKeys.values():
				self["PartitionAlgorithm"]=section
			elif section in self.eventProcessingAlgoKeys.values():
				self["ProcessingAlgorithm"]=section
			elif section in self.filterAlgoKeys.values():
				self["FilterAlgorithm"]=section

			# print vals
			self.update(vals)

	def _setupModelViews(self):
		self.keyTypesDict={
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
								"plotResults" 			: int,
								"FitTol" 				: float,
								"FitIters" 				: int,
								"BlockRejectRatio" 		: float,
								"filterOrder" 			: int,
								"filterCutoff" 			: float,
								"decimate" 				: int,
								"DataFilesType" 		: str,
								"DataFilesPath" 		: str,
								"eventThreshold"		: float,
								"blockSizeSec" 			: float,
								"meanOpenCurr" 			: float,
								"sdOpenCurr" 			: float,
								"dcOffset" 				: float,
								"start" 				: float,
								"end"	 				: float,
								"Rfb" 					: float,
								"Cfb" 					: float,
								"ProcessingAlgorithm"	: str,
								"PartitionAlgorithm"	: str,
								"FilterAlgorithm"		: str,
								"lastMeanOpenCurr"		: str,
								"lastSDOpenCurr"		: str,
								"wavelet"				: str,
								"level"					: int,
								"thresholdType"			: str,
								"thresholdSubType"		: str,
								"decimate"				: int
							}
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
		# self.multiStateAnalysisKeys=self.stepResponseAnalysisKeys

		self.besselLowpassFilterKeys={
								"filterOrder" 			: int,
								"filterCutoff" 			: float,
								"decimate" 				: int
							}
		self.denoiseFilterKeys={
								"wavelet"				: str,
								"level"					: int,
								"thresholdType"			: str,
								"thresholdSubType"		: str,
								"decimate"				: int
							}
		self.trajviewerKeys={
								"DataFilesType" 		: str,
								"DataFilesPath" 		: str,
								"eventThreshold"		: float,
								"blockSizeSec" 			: float,
								"meanOpenCurr" 			: float,
								"sdOpenCurr" 			: float,
								"dcOffset" 				: float,
								"start" 				: float,
								"Rfb" 					: float,
								"Cfb" 					: float
							}
		self.eventPartitionAlgoKeys={
								"CurrentThreshold" 		: "eventSegment"
							}

		self.eventProcessingAlgoKeys={
								"stepResponseAnalysis" 	: "stepResponseAnalysis"
							}

		self.filterAlgoKeys={
								"waveletDenoiseFilter"	: "waveletDenoiseFilter"
		}
		self.dataTypeKeys={
								"QDF" 					: "qdfTrajIO",
								"ABF" 					: "abfTrajIO"
							}
		self.analysisSetupKeys={
								"QDF" 					: pyeventanalysis.qdfTrajIO.qdfTrajIO,
								"ABF" 					: pyeventanalysis.abfTrajIO.abfTrajIO,
								"SingleChannelAnalysis" : pyeventanalysis.SingleChannelAnalysis.SingleChannelAnalysis,
								"CurrentThreshold" 		: pyeventanalysis.eventSegment.eventSegment,
								"stepResponseAnalysis" 	: pyeventanalysis.stepResponseAnalysis.stepResponseAnalysis,
								"waveletDenoiseFilter"	: pyeventanalysis.waveletDenoiseFilter.waveletDenoiseFilter
							}

# ,
# 								"multiStateAnalysis" 	: "multiStateAnalysis"
# "multiStateAnalysis" 	: pyeventanalysis.multiStateAnalysis.multiStateAnalysis,

if __name__ == "__main__":
	g=guiDataModel()

	g["DataFilesPath"]="/Users/arvind/Research/Experiments/PEG29EBSRefData/20120323/singleChan"
	g["DataFilesType"]="QDF"
	g["Rfb"]=9.1E+9
	g["Cfb"]=1.07E-12

	q=g.GenerateDataFilesObject(None)
	print q.formatsettings()
	print q.popdata(10)


	print g.GenerateSettingsView("CurrentThreshold", "stepResponseAnalysis", None)
	# print g.GenerateTrajView()
	# for k,v in g.iteritems():
	# 	print k, "=", v