import testutil
import mosaic.settings as settings
import numpy as np

class Base2StateTest(object): 
	def _setupTestCase(self, datfile, prmfile, algoHnd):
		[self.Fs, self.dat]=testutil.readcsv(datfile)
		self.prm=testutil.readparams(prmfile)

		self.sett = (settings.settings('.', defaultwarn=False).settingsDict)[algoHnd.__name__]

		self.dt=int(1e6/self.dat[0])

	def runTestCase(self, datfile, prmfile, algoHnd):
		self._setupTestCase(datfile, prmfile,algoHnd)

		self.testobj=algoHnd(
							self.dat, 
							self.Fs,
							eventstart=int(self.prm['tau1']/self.dt),			# event start point
							eventend=int(self.prm['tau2']/self.dt),    		# event end point
							baselinestats=[ 1.0, 0.01, 0.0 ],
							algosettingsdict=self.sett,
							savets=0,
							absdatidx=0.0,
							datafileHnd=None
						)
		self.testobj.processEvent()

		assert self.testobj.mdProcessingStatus == 'normal' 
		assert round(self.testobj.mdBlockDepth,1) == 1.0-abs(self.prm['a']) 
		assert round(self.testobj.mdResTime,1) == (self.prm['tau2']-self.prm['tau1'])/1000. 


class BaseMultiStateTest(object):
	def almostEqual(self, a, b, tol):
		return abs(a - b) <= tol

	def _setupTestCase(self, datfile, prmfile, algoHnd):
		self.dat=testutil.readDataRAW(datfile)
		self.prm=testutil.readParametersJSON(prmfile)
		self.Fs=int(self.prm['FsKHz']*1000)

		self.dt=1./self.prm['FsKHz']

		self.noiseRMS=self.prm['noisefArtHz']*np.sqrt(self.prm['BkHz']*1000.)/1000.
				
		self.sett = (settings.settings('.', defaultwarn=False).settingsDict)[algoHnd.__name__]
		# self.sett={}

		# self.sett["InitThreshold"] = 4.5
		# self.sett["MinStateLength"] = 10
		# self.sett["FitIters"] = 5000
		# self.sett["FitTol"] = 1.0e-7
		# self.sett["MaxEventLength"] = 100000
		# self.sett["UnlinkRCConst"] = 0
	
	def runTestCase(self, datfile, prmfile, algoHnd):
		self._setupTestCase(datfile, prmfile,algoHnd)
			
		testobj=algoHnd(
					self.dat, 
					self.Fs,
					eventstart=int(self.prm['eventDelay'][0]/self.dt),			# event start point
					eventend=int(self.prm['eventDelay'][-1]/self.dt),    		# event end point
					baselinestats=[ self.prm['OpenChCurrent'], self.noiseRMS, 0.0 ],
					algosettingsdict=self.sett,
					savets=0,
					absdatidx=0.0,
					datafileHnd=None
				)
		testobj.processEvent()

		assert testobj.mdProcessingStatus == 'normal'
		assert self.almostEqual( testobj.mdNStates, self.prm['n'], 1)
		assert self.almostEqual( testobj.mdOpenChCurrent, self.prm['OpenChCurrent'], 1.0)