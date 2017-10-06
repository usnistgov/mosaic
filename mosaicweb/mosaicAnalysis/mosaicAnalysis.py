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

import mosaic.settings as settings
from mosaic.utilities.resource_path import resource_path, format_path
import mosaic

import mosaic.apps.SingleChannelAnalysis as sca

import mosaic.trajio.qdfTrajIO as qdf
import mosaic.trajio.abfTrajIO as abf
import mosaic.trajio.binTrajIO as bin

import mosaic.partition.eventSegment as es

import mosaic.process.adept as adept
import mosaic.process.adept2State as a2s
import mosaic.process.cusumPlus as cusum

from mosaic.utilities.ionic_current_stats import OpenCurrentDist
from mosaicweb.plotlyUtils import plotlyWrapper

import datetime
import time
import glob
import json
import numpy as np
import pprint

class DataTypeNotSupportedError(Exception):
	pass

class mosaicAnalysis:
	"""
		A class that can setup and run a MOSAIC analysis.
	"""
	def __init__(self, dataPath, sessionID, **kwargs):
		self.dataPath = dataPath
		self.sessionID=sessionID

		self.returnMessageJSON={
			"warning": ""
		}

		self._loadSettings(**kwargs)

		self.trajIO=''
		self.partitionAlgorithm='eventSegment'
		self.processingAlgorithm=''

		self.trajIOHandle=None
		self.partitionHandle=es.eventSegment
		self.processHandle=None

		self.trajIOObject=None

		self.dbFile=''

		self.analysisObject=None

		self.analysisRunning=False

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
		try:
			fname='eventMD-'+str(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))+'.sqlite'

			self.dbFile=format_path(self.dataPath+"/"+fname)
			# self.dbFile=self.dataPath+"/eventMD-20161208-130302.sqlite"

			self.processHandle=self._processHnd()

			self._writeSettings()

			self.analysisObject=sca.SingleChannelAnalysis(
				self.dataPath,
				self.trajIOHandle,
				None,
				self.partitionHandle,
				self.processHandle,
				dbFilename=fname
			)
			self.analysisObject.Run(forkProcess=True)

			time.sleep(3)

			self.analysisRunning=True
		except:
			raise

	def stopAnalysis(self):
		self.analysisObject.Stop()

		time.sleep(0.3)

		self.analysisRunning=False

	@property
	def analysisStatus(self):
		if self.analysisRunning:
			self.analysisRunning = self.analysisObject.subProc.is_alive()
		
		return self.analysisRunning

	def updateSettings(self, settingsString):
		self._loadSettings(settingsString=settingsString)

	def _writeSettings(self):
		with open(self.dataPath+"/.settings", 'w') as f:
			f.write( json.dumps(self.analysisSettingsDict, indent=4) )

	def _processHnd(self):
		for k in self.analysisSettingsDict.keys():
			if k in mosaicAnalysis.processHandleLookup.keys():
				self.processingAlgorithm=k

				return mosaicAnalysis.processHandleLookup[k]

	def _loadSettings(self, **kwargs):
		try:
			self.analysisSettingsDict=json.loads(kwargs['settingsString'])
			self.defaultSettings=False
		except KeyError:
			sObj=settings.settings(self.dataPath)
			
			self.analysisSettingsDict=sObj.settingsDict
			self.defaultSettings=sObj.defaultSettingsLoaded

	def _configTrajIOObject(self):
		""" 
			Configure a trajIO object from the contents of analysisSettingsDict
		"""		
		trajIOSettings = {}

		try:
			if "qdfTrajIO" in self.analysisSettingsDict.keys():
				self.trajIO="qdfTrajIO"
				self.fileType='QDF'

				try:
					ebsSettings=EBSStateFileDict.EBSStateFileDict(glob.glob(self.dataPath+'/*.txt')[0])

					self.analysisSettingsDict["qdfTrajIO"]["Rfb"]=float(ebsSettings['FB Resistance'])
					self.analysisSettingsDict["qdfTrajIO"]["Cfb"]=float(ebsSettings['FB Capacitance'])
				except:
					self.returnMessageJSON['warning']="Using manually defined Rfb and Cfb values for QDF data."
			elif "abfTrajIO" in self.analysisSettingsDict.keys():
				self.trajIO="abfTrajIO"
				self.fileType='ABF'
			elif "binTrajIO" in self.analysisSettingsDict.keys():
				self.trajIO="binTrajIO"
				self.fileType='BIN'
			else:
				raise DataTypeNotSupportedError("The supplied data type is not supported.")

			self.trajIOHandle = mosaicAnalysis.trajIOHandleLookup[self.trajIO]
			trajIOSettings = self.analysisSettingsDict[self.trajIO]

			self.dcOffset=float(self.analysisSettingsDict[self.trajIO]['dcOffset'])
			self.start=float(self.analysisSettingsDict[self.trajIO]['start'])
			self._dataEnd(self.trajIO)

			self.blockSize=float(self.analysisSettingsDict['eventSegment']['blockSizeSec'])

			self.trajIOObject=self.trajIOHandle(dirname=self.dataPath, **trajIOSettings)
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
			decimate=self._calculateDecimation(len(tdat))
			
			dt=(1/float(FsHz))*decimate
			dataPolarity=float(np.sign(np.mean(tdat)))

			ydat=((dataPolarity*tdat) - self.dcOffset)[::decimate]
			xdat=np.arange(self.start, self.start+self.blockSize, dt)

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

			self.returnMessageJSON['dataPath']=(self.dataPath).replace(str(mosaic.WebServerDataLocation), "<Data Root>")
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

	def _calculateDecimation(self, dataLen):
		d=(self.trajIOObject.FsHz)/10

		if dataLen < d:
			return 1
		else:
			return int(round(dataLen/d))

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
	processHandleLookup={
		"adept":		adept.adept,
		"adept2State":	a2s.adept2State,
		"cusumPlus":	cusum.cusumPlus
	}

if __name__ == '__main__':
	ma=mosaicAnalysis.mosaicAnalysis(s, dataPath, defaultSettings, sessionID) 
