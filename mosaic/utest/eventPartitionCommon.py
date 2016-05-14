import json
import glob
import os
import mosaic.settings as settings
from mosaic.tsvTrajIO import *
import testutil
import mosaic.adept2State as a2s 

class EventPartitionTest(object):
	def setUp(self):
		self.datapath = 'testdata'

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

		assert testobj.eventcount == prm['nevents']

		testobj.Stop()

		for f in glob.glob('testdata/*.sqlite'):
			os.remove(f)