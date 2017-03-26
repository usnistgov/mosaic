"""
	A class that manages MOSAIC analyses.

	:Created:	3/19/2017
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		3/19/17		AB 	Initial version
"""
from mosaicgui import EBSStateFileDict
import mosaic.trajio.qdfTrajIO as qdf
import mosaic.trajio.abfTrajIO as abf
import mosaic.trajio.binTrajIO as bin
from mosaic.utilities.ionic_current_stats import OpenCurrentDist
from mosaicweb.plotlyUtils import plotlyWrapper

import glob
import numpy as np
import pprint

class DataTypeNotSupportedError(Exception):
	pass

class mosaicAnalysis:
	"""
		A class that can setup and run a MOSAIC analysis.
	"""
	def __init__(self, settingsDict, dataPath, defaultSettings, sessionID):
		self.analysisSettingsDict = settingsDict #eval(settingsString)
		self.dataPath = dataPath
		self.defaultSettings=defaultSettings
		self.sessionID=sessionID

		self.returnMessageJSON={
			"warning": ""
		}

		self.trajIOObject=None

	def setupAnalysis(self):
		try:
			if self.defaultSettings:
				self._pruneDefaultSettings()

			self._configTrajIOObject()
			self._fastForwardToStart()
			self._finishSetup()

			# Attach the updated settings string to the return message.
			self.returnMessageJSON['settingsString']=self.analysisSettingsDict

			return self.returnMessageJSON
		except:
			raise

	def runAnalysis(self):
		pass

	def analysisStatistics(self):
		pass

	def _configTrajIOObject(self):
		""" 
			Configure a trajIO object from the contents of analysisSettingsDict
		"""		
		trajIOHandle = None
		trajIOSettings = {}

		try:
			if "qdfTrajIO" in self.analysisSettingsDict.keys():
				trajIOHandle = mosaicAnalysis.trajIOHandleLookup["qdfTrajIO"]
				trajIOSettings = self.analysisSettingsDict["qdfTrajIO"]

				try:
					ebsSettings=EBSStateFileDict.EBSStateFileDict(glob.glob(self.dataPath+'/*.txt')[0])

					self.analysisSettingsDict["qdfTrajIO"]["Rfb"]=float(ebsSettings['FB Resistance'])
					self.analysisSettingsDict["qdfTrajIO"]["Cfb"]=float(ebsSettings['FB Capacitance'])
				except:
					self.returnMessageJSON['warning']="Using manually defined Rfb and Cfb values for QDF data."

				self.dcOffset=float(self.analysisSettingsDict['qdfTrajIO']['dcOffset'])
				self.start=float(self.analysisSettingsDict['qdfTrajIO']['start'])
				self._dataEnd("qdfTrajIO")

				self.fileType='QDF'
			elif "abfTrajIO" in self.analysisSettingsDict.keys():
				trajIOHandle = mosaicAnalysis.trajIOHandleLookup["abfTrajIO"]
				trajIOSettings = self.analysisSettingsDict["abfTrajIO"]

				self.dcOffset=float(self.analysisSettingsDict['abfTrajIO']['dcOffset'])
				self.start=float(self.analysisSettingsDict['abfTrajIO']['start'])
				self._dataEnd("abfTrajIO")
				self.fileType='ABF'
			elif "binTrajIO" in self.analysisSettingsDict.keys():
				trajIOHandle = mosaicAnalysis.trajIOHandleLookup["binTrajIO"]
				trajIOSettings = self.analysisSettingsDict["binTrajIO"]

				self.dcOffset=float(self.analysisSettingsDict['binTrajIO']['dcOffset'])
				self.start=float(self.analysisSettingsDict['binTrajIO']['start'])
				self._dataEnd("binTrajIO")
				self.fileType='BIN'
			else:
				raise DataTypeNotSupportedError("The supplied data type is not supported.")

			self.blockSize=float(self.analysisSettingsDict['eventSegment']['blockSizeSec'])

			self.trajIOObject=trajIOHandle(dirname=self.dataPath, **trajIOSettings)
		except:
			raise

	def _fastForwardToStart(self):
		try:
			FsHz=self.trajIOObject.FsHz

			for n in range(0, int( float(self.start)/self.blockSize )):
				self.trajIOObject.popdata(int(self.blockSize*FsHz))
			self.trajIOObject.popdata(int( float(self.start)%float(self.blockSize)*FsHz ))
		except:
			raise

	def _finishSetup(self):
		try:
			FsHz=self.trajIOObject.FsHz
			
			tdat = self.trajIOObject.popdata(int(self.blockSize*FsHz))
			dataPolarity=float(np.sign(np.mean(tdat)))

			ydat=(dataPolarity*tdat) - self.dcOffset
			xdat=np.arange(self.start, self.start+self.blockSize, 1/float(FsHz))

			self._openChanStats(ydat)

			if float(self.analysisSettingsDict["eventSegment"]["meanOpenCurr"])==-1. or float(self.analysisSettingsDict["eventSegment"]["sdOpenCurr"])==-1.:
				mu=self.returnMessageJSON["currMeanAuto"]
				sigma=self.returnMessageJSON["currSigmaAuto"]

			else:
				mu=round(float(self.analysisSettingsDict["eventSegment"]["meanOpenCurr"]),3)
				sigma=round(float(self.analysisSettingsDict["eventSegment"]["sdOpenCurr"]),3)

			currThr=abs(mu)-float(self.analysisSettingsDict["eventSegment"]["eventThreshold"])*sigma

			self.returnMessageJSON['blockSize']=self.blockSize
			self.returnMessageJSON['currThreshold']=round(currThr, 2)
			self.returnMessageJSON['start']=self.start
			try:
				self.returnMessageJSON['end']=self.end
			except:
				pass
			self.returnMessageJSON['saveToDisk']=self.analysisSettingsDict["eventSegment"]["writeEventTS"]

			self.returnMessageJSON['fileType']=self.fileType

			self.returnMessageJSON['dataPath']=self.dataPath
			self.returnMessageJSON['FsHz']=FsHz

			# add plots
			dat={}
			dat['data']=[
							plotlyWrapper.plotlyTrace(list(xdat), list(ydat), "IonicCurrentTimeSeries"), 
							plotlyWrapper.plotlyTrace([self.start, self.start+self.blockSize],[mu, mu], "MeanIonicCurrent"), 
							plotlyWrapper.plotlyTrace([self.start, self.start+self.blockSize],[currThr, currThr], "IonicCurrentThreshold")
						]
			dat['layout']=plotlyWrapper.plotlyLayout("TimeSeriesLayout")
			dat['options']=plotlyWrapper.plotlyOptions()

			self.returnMessageJSON['trajPlot']=dat
		except:
			raise


	def _openChanStats(self, ydat):
		try:
			mu, sigma = OpenCurrentDist(ydat, 0.5)
		except:
			mu=0
			sigma=0

		self.returnMessageJSON['currMeanAuto']=round(mu, 3)
		self.returnMessageJSON['currSigmaAuto']=round(sigma, 3)

	def _dataEnd(self, section):
		try:
			self.end=float(self.analysisSettingsDict[str(section)]['end'])
		except:
			pass

	def _pruneDefaultSettings(self):
		newSettings={}

		newSettings.update({
			"eventSegment": self.analysisSettingsDict["eventSegment"]
			})
		newSettings.update({
			"adept": self.analysisSettingsDict["adept"]
			})

		fileType=self._folderDesc()
		newSettings.update({
			fileType: self.analysisSettingsDict[fileType]
			})

		for k in ["meanOpenCurr", "sdOpenCurr", "slopeOpenCurr", "blockSizeSec", "eventThreshold"]:
			newSettings["eventSegment"][k]=float(newSettings["eventSegment"][k])

		for k in ["start", "dcOffset"]:
			newSettings[fileType][k]=float(newSettings[fileType][k])

		# pp=pprint.PrettyPrinter(indent=4)
		# pp.pprint(newSettings)

		self.analysisSettingsDict=newSettings

	def _folderDesc(self):
		nqdf = len(glob.glob(self.dataPath+'/*.qdf'))
		nbin = len(glob.glob(self.dataPath+'/*.bin'))+len(glob.glob(self.dataPath+'/*.dat'))
		nabf = len(glob.glob(self.dataPath+'/*.abf'))
		
		if nqdf > 0:
			return "qdfTrajIO"
		elif nabf > 0:
			return "abfTrajIO"
		else:		#default
			return "binTrajIO"

	trajIOHandleLookup={
			"qdfTrajIO":	qdf.qdfTrajIO,
			"abfTrajIO":	abf.abfTrajIO,
			"binTrajIO":	bin.binTrajIO	
		}
