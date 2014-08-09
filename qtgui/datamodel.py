import json
import pyeventanalysis.settings

class guiDataModel(dict):
	def __init__(self):
		self["DataFilesType"]="ABF"
		self["DataFilesPath"]=""
		self["start"]=0
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
								"blockSizeSec" : float,
								"eventPad" : int,
								"minEventLength" : int,
								"eventThreshold" : float,
								"driftThreshold" : float,
								"maxDriftRate" : float,
								"meanOpenCurr" : float,
								"sdOpenCurr": float,
								"slopeOpenCurr" : float,
								"writeEventTS" : int,
								"parallelProc" : int,
								"reserveNCPU" : int,
								"plotResults" : int
							}
		self.stepResponseAnalysisKeys={
								"FitTol" : float,
								"FitIters" : int,
								"BlockRejectRatio" : float
							}
		self.multiStateAnalysisKeys=self.stepResponseAnalysisKeys

		self.besselLowpassFilterKeys={
								"filterOrder" : int,
								"filterCutoff" : float,
								"decimate" : int
							}

		self.trajviewerKeys={
								"DataFilesType" : str,
								"DataFilesPath" : str,
								"eventThreshold" : float,
								"blockSizeSec" : float,
								"meanOpenCurr" : float,
								"sdOpenCurr" : float,
								"dcOffset" : float,
								"start" : int,
								"Rfb" : float,
								"Cfb" : float
							}
		self.eventPartitionAlgoKeys={
								"CurrentThreshold" : "eventSegment"
							}

		self.eventProcessingAlgoKeys={
								"stepResponseAnalysis" : "stepResponseAnalysis",
								"multiStateAnalysis" : "multiStateAnalysis"
							}

if __name__ == "__main__":
	g=guiDataModel()
	print g.GenerateSettingsView("CurrentThreshold", "stepResponseAnalysis")

	print g.GenerateTrajView()
	# for k,v in g.iteritems():
	# 	print k, "=", v