import json
import glob
import os
from nose.tools import raises
import mosaic
import mosaic.settings as settings
from mosaic.trajio.tsvTrajIO import *
from . import testutil
import mosaic.process.adept2State as a2s 

class EventPartitionTest(object):
	def setUp(self):
		self.datapath = 'mosaic/tests/testdata'

	def runTestCase(self, datfile, prmfile, eventPartHnd, parallel):
		prm=testutil.readparams(prmfile)
		dat=tsvTrajIO(fnames=[datfile], Fs=prm['Fs'], separator=',')

		sett = (settings.settings('.', defaultwarn=False).settingsDict)

		epartsettings = sett[eventPartHnd.__name__]

		epartsettings['blockSizeSec'] = 0.006
		epartsettings['meanOpenCurr'] = 1
		epartsettings['sdOpenCurr'] = 0.03 
		epartsettings['slopeOpenCurr'] = 0
		epartsettings['driftThreshold'] = 1000
		epartsettings['maxDriftRate'] = 9999.0
		epartsettings['eventThreshold'] = 5.0

		if parallel:
			epartsettings['parallelProc'] = 1

		testobj=eventPartHnd(
							dat, 
							a2s.adept2State, 
							epartsettings,
							sett["adept2State"],
							json.dumps(sett, indent=4)
						)
		testobj.PartitionEvents()

		assert testobj.eventcount == prm['nevents'] or testobj.eventcount == prm['nevents']-1

		testobj.Stop()

		for f in glob.glob('mosaic/tests/testdata/*.sqlite'):
			os.remove(f)

	@raises(mosaic.commonExceptions.SettingsTypeError)
	def runTestError(self, datfile, param, eventPartHnd, parallel):
		dat=tsvTrajIO(fnames=[datfile], Fs=50000, separator=',')

		sett = (settings.settings('.', defaultwarn=False).settingsDict)

		epartsettings = sett[eventPartHnd.__name__]

		epartsettings[param] = 'param'

		testobj=eventPartHnd(
							dat, 
							a2s.adept2State, 
							epartsettings,
							sett["adept2State"],
							json.dumps(sett, indent=4)
						)
		