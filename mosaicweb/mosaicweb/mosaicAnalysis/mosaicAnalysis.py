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
	def __init__(self, settingsDict, dataPath, defaultSettings):
		self.analysisSettingsDict = settingsDict #eval(settingsString)
		self.dataPath = dataPath
		self.defaultSettings=defaultSettings

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

		pp=pprint.PrettyPrinter(indent=4)
		pp.pprint(newSettings)

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

if __name__ == '__main__':
	ma=mosaicAnalysis(s, "/Users/arvind/Research/Experiments/AnalysisTools/ReferenceData/m40_0916_RbClPEG/")

	ma.setupAnalysis()

	print ma.returnMessageJSON

def _trajPlot(settingsDict, datPath):
	s=settingsDict

	retMsg={'warning': ''}
	dat={}

	try:
		ebsSettings=EBSStateFileDict.EBSStateFileDict(glob.glob(datPath+'/*.txt')[0])

		Rfb=float(ebsSettings['FB Resistance'])
		Cfb=float(ebsSettings['FB Capacitance'])
	except:
		retMsg['warning']="Rfb and Cfb values were not found for QDF data."
		Rfb=0.
		Cfb=0.

	q=qdf.qdfTrajIO(dirname=datPath, filter='*.qdf', Rfb=Rfb, Cfb=Cfb)
	Fs=q.FsHz

	blkSize=float(s['eventSegment']['blockSizeSec'])
	currThreshold=float(s['eventSegment']['eventThreshold'])
	dcOffset=float(s['qdfTrajIO']['dcOffset'])
	start=float(s['qdfTrajIO']['start'])
	saveToDisk=bool(s['eventSegment']['writeEventTS'])

	for n in range(0, int( float(start)/float(blkSize) )):
		q.popdata(int(blkSize*Fs))
	q.popdata(int( float(start)%float(blkSize)*Fs ))

	ydat=(-1.*q.popdata(int(blkSize*Fs))) - dcOffset
	xdat=np.arange(start, start+blkSize, 1/float(Fs))

	mu, sigma = OpenCurrentDist(ydat, 0.5)
	currThr=abs(mu)-currThreshold*sigma

	
	#time-series
	trace1={};
	trace1['x']=list(xdat)
	trace1['y']=list(ydat)
	trace1['mode']='scatter'
	trace1['line']= { 'color': 'rgb(40, 53, 147)', 'width': '1' }
	trace1['name']='ionic current'

	trace2={};
	trace2['x']=[start, start+blkSize]
	trace2['y']=[currThr, currThr]
	trace2['mode']='scatter'
	trace2['line']= { 'color': 'rgb(255, 80, 77)', 'width': '2' }
	trace2['name']='ionic current threshold'

	trace3={};
	trace3['x']=[start, start+blkSize]
	trace3['y']=[mu, mu]
	trace3['mode']='scatter'
	trace3['line']= { 'color': 'rgb(120, 120, 120)', 'width': '2', 'dash': 'dash' }
	trace3['name']='mean current'

	#hist
	# trace4={};
	# trace4['x']=list([ random.gauss(mu, sigma) for i in range(len(np.arange(0, mu, 0.1))) ])
	# trace4['y']=list(np.arange(0, mu, 0.1))
	# trace4['mode']='scatter'
	# trace4['line']= { 'color': 'rgb(40, 53, 147)', 'width': '1' }
	# trace4['xaxis']='x2'
 #  	trace4['yaxis']='y'

	layout={}
	# layout['title']='Blockade Depth Histogram'
	layout['xaxis']= { 'title': 't (s)', 'domain': '[0, 0.75]' }
	layout['yaxis']= { 'title': 'i (pA)'} # , 'domain': '[0, 1]'
	# layout['xaxis4']= { 'title': 'counts', 'domain': '[0.85, 1]'}
	# layout['yaxis2']= { 'domain': '[0, 1]'}
	layout['paper_bgcolor']='rgba(0,0,0,0)'
	layout['plot_bgcolor']='rgba(0,0,0,0)'
	layout['margin']={'l':'50', 'r':'50', 't':'0', 'b':'50'}
	layout['showlegend']=False
	layout['autosize']=True
	layout['height']=300
	layout['side']='right'


	dat['data']=[trace1, trace2, trace3]
	# dat['data']=[trace1, trace4]
	dat['layout']=layout
	dat['options']={'displayLogo': False}
	
	retMsg['trajPlot']=dat
	retMsg['blockSize']=blkSize
	retMsg['currMeanAuto']=round(mu, 3)
	retMsg['currSigmaAuto']=round(sigma, 3)
	retMsg['currThreshold']=round(currThr, 2)
	retMsg['start']=start
	retMsg['saveToDisk']=saveToDisk

	retMsg['fileType']='QDF'

	retMsg['settingsString']=s

	return retMsg

