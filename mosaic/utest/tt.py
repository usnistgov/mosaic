import json
import testutil
import stepResponseAnalysis as sra
import singleStepEvent as sse

def runTestCase(datfile, prmfile, algoHnd):
	dat=testutil.readcsv(datfile)
	prm=testutil.readparams(prmfile)

	sett=json.loads( "".join((open('../.settings', 'r').readlines())) )[algoHnd.__name__]

	dt=int(1e6/dat[0])

	testobj=algoHnd(
						dat[1], 
						dat[0],
						eventstart=int(prm['tau1']/dt),			# event start point
						eventend=int(prm['tau2']/dt),    		# event end point
						baselinestats=[ 1.0, 0.01, 0.0 ],
						algosettingsdict=sett,
						savets=0
					)
	testobj.processEvent()

	return [ testobj, prm ]


[ testobj, prm ]=runTestCase('testdata/test1.csv', 'testdata/test1.prm', sse.singleStepEvent)

print testobj.mdProcessingStatus
print testobj.mdBlockDepth
print testobj.mdResTime