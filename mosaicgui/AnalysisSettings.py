import json

class AnalysisSettings(dict):
	def __init__(self, blSize=0.5, eventThr=4.0, meanOpenCurr=-1, sdOpenCurr=-1, writeEventTS=1, parallel=0, reserveCPU=2, eventProcAlgo="stepResponseAnalysis"):
		# populate the keys that are defaults
		self.eventPartitionDefaults(blSize, eventThr, meanOpenCurr, sdOpenCurr, writeEventTS, parallel, reserveCPU)
		self.eventProcDefaults(eventProcAlgo)

	def __str__(self):
		return json.dumps(self, indent=4)

	def eventPartitionDefaults(self, blSize, eventThr, meanOpenCurr, sdOpenCurr, writeEventTS, parallel, reserveCPU):
		self["eventSegment"] = {
			"blockSizeSec" 		: str(blSize),
			"eventPad" 			: "50",
			"minEventLength" 	: "5",
			"eventThreshold" 	: str(eventThr),
			"driftThreshold" 	: "999",
			"maxDriftRate" 		: "999",
			"meanOpenCurr"		: str(meanOpenCurr),
			"sdOpenCurr"		: str(sdOpenCurr),
			"slopeOpenCurr"		: "0",
			"writeEventTS"		: str(writeEventTS),
			"parallelProc"		: str(parallel),
			"reserveNCPU"		: str(reserveCPU),
			"plotResults"		: "0"
		}

	def eventProcDefaults(self, algo):
		self[str(algo)]={
			"FitTol" : "1.e-7", 
			"FitIters" : "50000", 
			"BlockRejectRatio" : "0.9"
		}
