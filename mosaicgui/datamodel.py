"""
	A class that stores and formats the data for mosaicGUI.

	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
		.. line-block::
			03/30/16 	AB 	Change UnlinkRCConst to LinkRCConst.
			3/16/16 	AB 	Migrate InitThreshold setting to CUSUM StepSize.
			8/24/15 	AB 	Updated algorithm names to ADEPT and CUSUM+
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

import mosaic.adept2State
import mosaic.adept
import mosaic.cusumPlus

import mosaic.qdfTrajIO
import mosaic.abfTrajIO
import mosaic.binTrajIO
import mosaic.tsvTrajIO

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
		self["format"]="V"
		self["scale"]=1.0

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

		if procAlgo=="adept2State":
			settingsdict[procAlgo]={}
			procKeys=self.adept2StateKeys
		elif procAlgo=="adept":
			settingsdict[procAlgo]={}
			procKeys=self.adeptKeys
		elif procAlgo=="cusumPlus":
			settingsdict[procAlgo]={}
			procKeys=self.cusumPlusKeys

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
			keys.extend(["Rfb", "Cfb", "format"])
			dargs.update({
				"filter"	: self["filter"]
				})
		elif self["DataFilesType"]=="BIN":
			keys.extend(["AmplifierScale", "AmplifierOffset", "SamplingFrequency", "HeaderOffset", "ColumnTypes", "IonicCurrentColumn"])
			dargs.update({"filter"	: self["filter"]})
		elif self["DataFilesType"]=="TSV":
			if self["nCols"]==-1:
				keys.extend(["Fs", "scale"])
			else:
				keys.extend(["nCols", "timeCol", "currCol", "scale"])
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
				self.analysisSetupKeys[str(self.eventProcessingAlgoKeys[eventProcessingAlgo])]
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

			try:
				self["dbInfoFsHz"]=db.readAnalysisInfo()[7]
			except:
				pass

		self._updateSettings()

	def UpdateDataModelFromSettingsString(self, settingsstr):
		if not self.jsonSettingsObj:
			self.UpdateDataModelFromSettings()

		self.jsonSettingsObj.parseSettingsString(settingsstr)

		self._updateSettings()

	def EventProcessingAlgorithmLabel(self):
		try:
			return dict([v,k] for k,v in self.eventProcessingAlgoKeys.items())[self["ProcessingAlgorithm"]]
		except KeyError:
			return self["ProcessingAlgorithm"]

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
								"dbInfoFsHz"			: float,
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
								"format"				: str,
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
								"MaxEventLength" 		: int,
								"headers"				: bool,
								"Fs"					: int,
								"nCols"					: int,
								"timeCol"				: int,
								"currCol"				: int
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
		self.adept2StateKeys={
								"FitTol" 				: float,
								"FitIters" 				: int,
								"BlockRejectRatio" 		: float,
								"LinkRCConst" 		: bool
							}
		self.adeptKeys={
								"FitTol" 				: float,
								"FitIters" 				: int,
								"BlockRejectRatio" 		: float,
								"StepSize"			: float,
								"MinStateLength"		: int,
								"MaxEventLength" 		: int,
								"LinkRCConst"			: bool
							}
		self.cusumPlusKeys={
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
								"format"				: str,
								"AmplifierScale"		: str,
								"AmplifierOffset"		: str,
								"SamplingFrequency"		: int,
								"HeaderOffset"			: int,
								"ColumnTypes"			: str,
								"IonicCurrentColumn"	: str,
								"filter"				: str,
								"headers"				: bool,
								"Fs"					: int,
								"nCols"					: int,
								"timeCol"				: int,
								"currCol"				: int,
								"scale"					: float
							}
		self.eventPartitionAlgoKeys={
								"CurrentThreshold" 		: "eventSegment"
							}

		self.eventProcessingAlgoKeys={
								"ADEPT 2-state" 		: "adept2State",
								"ADEPT"					: "adept",
								"CUSUM+"				: "cusumPlus"
							}

		self.filterAlgoKeys={
								"waveletDenoiseFilter"	: "waveletDenoiseFilter"
		}
		self.dataTypeKeys={
								"QDF" 					: "qdfTrajIO",
								"ABF" 					: "abfTrajIO",
								"BIN" 					: "binTrajIO",
								"TSV"					: "tsvTrajIO"
							}
		self.analysisSetupKeys={
								"QDF" 					: mosaic.qdfTrajIO.qdfTrajIO,
								"ABF" 					: mosaic.abfTrajIO.abfTrajIO,
								"BIN" 					: mosaic.binTrajIO.binTrajIO,
								"TSV" 					: mosaic.tsvTrajIO.tsvTrajIO,
								"SingleChannelAnalysis" : mosaic.SingleChannelAnalysis.SingleChannelAnalysis,
								"CurrentThreshold" 		: mosaic.eventSegment.eventSegment,
								"adept2State" 			: mosaic.adept2State.adept2State,
								"adept"					: mosaic.adept.adept,
								"cusumPlus"				: mosaic.cusumPlus.cusumPlus,
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


	print g.GenerateSettingsView("CurrentThreshold", "ADEPT 2-state", None)
	print g.GenerateTrajView()
	# for k,v in g.iteritems():
	# 	print k, "=", v