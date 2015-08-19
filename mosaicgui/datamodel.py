"""
	A class that stores and formats the data for mosaicGUI.

	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
		.. line-block::
			6/24/15 	AB 	Added an option to unlink the RC constants in stepResponseAnalysis.
			3/20/15		AB 	Added MaxEventLength to multiStateAnalysis settings
			3/6/15 		JF 	Added MinStateLength to multiStateAnalysis setup model
"""	
import json
import os

import mosaic.settings

import mosaic.sqlite3MDIO

import mosaic.SingleChannelAnalysis
import mosaic.eventSegment

import mosaic.stepResponseAnalysis
import mosaic.multiStateAnalysis
import mosaic.cusumLevelAnalysis

import mosaic.qdfTrajIO
import mosaic.abfTrajIO
import mosaic.binTrajIO

from mosaic.besselLowpassFilter import *
import mosaic.waveletDenoiseFilter
from mosaic.metaTrajIO import FileNotFoundError, EmptyDataPipeError
from mosaic.utilities.resource_path import resource_path
from sqlite3 import OperationalError

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
		if key == "meanOpenCurr":
			if dat != -1: dat=abs(self.keyTypesDict[key](val))
		if key == "sdOpenCurr":
			if dat != -1: dat=abs(self.keyTypesDict[key](val))


		try:
			dict.__setitem__(self, key, self.keyTypesDict[key](dat) )
		except KeyError:
			dict.__setitem__(self, key, dat )

	def __getitem__(self, key):
		try:
			return dict.__getitem__(self, key)
		except KeyError:
			# If a key doesn't exist, set its initial value to -1
			self[key]=-1
			return self[key]


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
		elif procAlgo=="multiStateAnalysis":
			settingsdict[procAlgo]={}
			procKeys=self.multiStateAnalysisKeys
		elif procAlgo=="cusumLevelAnalysis":
			settingsdict[procAlgo]={}
			procKeys=self.cusumLevelAnalysisKeys

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
		# dargs={"dirname" : str(self["DataFilesPath"])}
		dargs={}

		if self["DataFilesType"]=="QDF":
			keys.extend(["Rfb", "Cfb"])
			dargs.update({"filter"	: self["filter"]})
		elif self["DataFilesType"]=="BIN":
			keys.extend(["AmplifierScale", "AmplifierOffset", "SamplingFrequency", "HeaderOffset", "ColumnTypes", "IonicCurrentColumn"])
			dargs.update({"filter"	: self["filter"]})
		else:
			dargs.update({"filter"	: self["filter"]})

		if self["end"]!=-1.:
			dargs["end"]=self["end"]

		for k in keys:
			dargs[k]=self.trajviewerKeys[k](self[k])

		return dargs

	def GenerateAnalysisObject(self, eventPartitionAlgo, eventProcessingAlgo, dataFilterAlgo):
		try:
			filterHnd=self.analysisSetupKeys[str(dataFilterAlgo)]
		except KeyError:
			filterHnd=None

		return self.analysisSetupKeys["SingleChannelAnalysis"](
				self["DataFilesPath"],
				self.analysisSetupKeys[self["DataFilesType"]], 	#self.GenerateDataFilesObject(dataFilterAlgo),
				filterHnd,
				self.analysisSetupKeys[str(eventPartitionAlgo)],
				self.analysisSetupKeys[str(eventProcessingAlgo)]
			)

	def GenerateDataFilesObject(self, dataFilterAlgo):
		dargs=self.GenerateDataFilesView()

		if dataFilterAlgo:
			dargs["datafilter"]=self.analysisSetupKeys[str(dataFilterAlgo)]

		return self.analysisSetupKeys[self["DataFilesType"]](dirname=self["DataFilesPath"], **dargs)

	def UpdateDataModelFromSettings(self, dbfile=None):
		# Load settings from the data directory
		if self["DataFilesPath"]:
			self.jsonSettingsObj=mosaic.settings.settings(self["DataFilesPath"])
		else:
			# print "res_path", 
			# self.jsonSettingsObj=mosaic.settings.settings(resource_path(".settings"))
			self.jsonSettingsObj=mosaic.settings.settings('', defaultwarn=False)

		# if a dbfile
		if dbfile:
			try:
				db=mosaic.sqlite3MDIO.sqlite3MDIO()
				db.openDB(dbfile)
				self.jsonSettingsObj=mosaic.settings.settings(self["DataFilesPath"])
				self.jsonSettingsObj.parseSettingsString( db.readSettings() )
			except OperationalError:
				print "Settings not found in ", dbfile, "\n"

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
			elif section in self.dataTypeKeys.values():
				self["filter"]=vals["filter"]

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
								"FitTol" 				: float,
								"FitIters" 				: int,
								"BlockRejectRatio" 		: float,
								"filterOrder" 			: int,
								"filterCutoff" 			: float,
								"decimate" 				: int,
								"DataFilesType" 		: str,
								"DataFilesPath" 		: str,
								"eventThreshold"		: float,
								"eventThresholdpA"		: float,
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
								"lastMeanOpenCurr"		: float,
								"lastSDOpenCurr"		: float,
								"wavelet"				: str,
								"level"					: int,
								"thresholdType"			: str,
								"thresholdSubType"		: str,
								"decimate"				: int,
								"AmplifierScale"		: str,
								"AmplifierOffset"		: str,
								"SamplingFrequency"		: int,
								"HeaderOffset"			: int,
								"ColumnTypes"			: str,
								"IonicCurrentColumn"	: str,
								"filter"				: str,
								"MinStateLength"		: int,
								"MaxEventLength" 		: int
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
								"reserveNCPU" 			: int
							}
		self.stepResponseAnalysisKeys={
								"FitTol" 				: float,
								"FitIters" 				: int,
								"BlockRejectRatio" 		: float,
								"UnlinkRCConst" 			: bool
							}
		self.multiStateAnalysisKeys={
								"FitTol" 				: float,
								"FitIters" 				: int,
								"BlockRejectRatio" 		: float,
								"InitThreshold"			: float,
								"MinStateLength"		: int,
								"MaxEventLength" 		: int,
								"UnlinkRCConst"			: bool
							}
		self.cusumLevelAnalysisKeys={
								"StepSize"				: float, 
								"MinThreshold"			: float,
								"MaxThreshold"			: float,
								"MinLength" 			: int
		}
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
								"eventThresholdpA"		: float,
								"blockSizeSec" 			: float,
								"meanOpenCurr" 			: float,
								"sdOpenCurr" 			: float,
								"dcOffset" 				: float,
								"start" 				: float,
								"Rfb" 					: float,
								"Cfb" 					: float,
								"AmplifierScale"		: str,
								"AmplifierOffset"		: str,
								"SamplingFrequency"		: int,
								"HeaderOffset"			: int,
								"ColumnTypes"			: str,
								"IonicCurrentColumn"	: str,
								"filter"				: str
							}
		self.eventPartitionAlgoKeys={
								"CurrentThreshold" 		: "eventSegment"
							}

		self.eventProcessingAlgoKeys={
								"stepResponseAnalysis" 	: "stepResponseAnalysis",
								"multiStateAnalysis"	: "multiStateAnalysis",
								"cusumLevelAnalysis"	: "cusumLevelAnalysis"
							}

		self.filterAlgoKeys={
								"waveletDenoiseFilter"	: "waveletDenoiseFilter"
		}
		self.dataTypeKeys={
								"QDF" 					: "qdfTrajIO",
								"ABF" 					: "abfTrajIO",
								"BIN" 					: "binTrajIO"
							}
		self.analysisSetupKeys={
								"QDF" 					: mosaic.qdfTrajIO.qdfTrajIO,
								"ABF" 					: mosaic.abfTrajIO.abfTrajIO,
								"BIN" 					: mosaic.binTrajIO.binTrajIO,
								"SingleChannelAnalysis" : mosaic.SingleChannelAnalysis.SingleChannelAnalysis,
								"CurrentThreshold" 		: mosaic.eventSegment.eventSegment,
								"stepResponseAnalysis" 	: mosaic.stepResponseAnalysis.stepResponseAnalysis,
								"multiStateAnalysis"	: mosaic.multiStateAnalysis.multiStateAnalysis,
								"cusumLevelAnalysis"	: mosaic.cusumLevelAnalysis.cusumLevelAnalysis,
								"waveletDenoiseFilter"	: mosaic.waveletDenoiseFilter.waveletDenoiseFilter
							}

if __name__ == "__main__":
	g=guiDataModel()

	# g["DataFilesPath"]=resource_path('eventMD-PEG29-Reference.sqlite')
	# g["DataFilesType"]="QDF"
	# g["Rfb"]=9.1E+9
	# g["Cfb"]=1.07E-12

	# q=g.GenerateDataFilesObject(None)
	# print q.formatsettings()
	# print q.popdata(10)


	print g.GenerateSettingsView("CurrentThreshold", "stepResponseAnalysis", None)
	# print g.GenerateTrajView()
	# for k,v in g.iteritems():
	# 	print k, "=", v