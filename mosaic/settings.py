"""
	Load analysis settings from a JSON file. 

	:Created:	8/24/2012
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		6/24/15 	AB 	Added an option to unlink the RC constants in stepResponseAnalysis.
		3/20/15 	AB 	Added MaxEventLength to multiStateAnalysis settings
		3/6/15		JF	Corrected formatting on cusumLevelAnalysis and multiStateAnalysis dictionary file
		3/6/15		AB 	Added MinStateLength parameter for multiStateAnalysis to dictionary
		2/14/15 	AB 	Added default settings for cusumLevelAnalysis.
		8/20/14		AB 	Changed precedence of settings file search to datpath/.settings,
						datpath/settings, coderoot/.settings and coderoot/settings
		8/6/14		AB 	Add a function to parse a settings string.
		9/5/13		AB 	Check for either .settings or settings in data directory
						and code root. Warn when using default settings
		8/24/12		AB	Initial version	
"""
import json
import os
import os.path

class settings:
	"""
			Initialize a settings object. 

			:Args: 
				- `datpath` :	Specify the location of the settings file. If a settings file is not found, return default settings.
				- `defaultwarn` :	If `True` warn the user if a settings file was not found in the path specified by `datpath`.
	"""
	def __init__(self, datpath, defaultwarn=True):
		"""
		"""	
		self.settingsFile=None

		if os.path.isfile(datpath+'/.settings'):
			self.settingsFile=datpath+"/.settings"
			settingstr="".join((open(self.settingsFile, 'r').readlines()))
		elif os.path.isfile(datpath+'/settings'):
			self.settingsFile=datpath+"/settings"
			settingstr="".join((open(self.settingsFile, 'r').readlines()))
		# elif os.path.isfile('.settings'):
		# 	print "Settings file not found in data directory. Default settings will be used."
		# 	self.settingsFile=os.getcwd()+"/.settings"
		# elif os.path.isfile('settings'):
		# 	print "Settings file not found in data directory. Default settings will be used."
		# 	self.settingsFile=os.getcwd()+"/settings"
		else:
			if defaultwarn:
				print "Settings file not found in data directory. Default settings will be used."
			settingstr=__settings__


		self.parseSettingsString( settingstr )

	def parseSettingsString(self, settingstring):
		self.settingsDict=json.loads( settingstring )

	def getSettings(self, section):
		"""
			Return settings for a specified section as a Python dict.

			:Args:
				- `section` : 	specifies the section for which settings are requested. Returns an empty dictionary if the settings file doesn't exist the section is not found.
		"""
		try:
			return self.settingsDict[section]
		except KeyError, AttributeError:
			return {}

__settings__="""
	{
		"eventSegment" : {
			"blockSizeSec" 			: "0.5",
			"eventPad" 				: "50",
			"minEventLength" 		: "5",
			"eventThreshold" 		: "6.0",
			"driftThreshold" 		: "999.0",
			"maxDriftRate" 			: "999.0",
			"meanOpenCurr"			: "-1",
			"sdOpenCurr"			: "-1",
			"slopeOpenCurr"			: "-1",
			"writeEventTS"			: "1",
			"parallelProc"			: "0",
			"reserveNCPU"			: "2"
		},
		"singleStepEvent" : {
			"binSize" 				: "1.0",
			"histPad" 				: "10",
			"maxFitIters"			: "5000",
			"a12Ratio" 				: "1.e4",
			"minEvntTime" 			: "10.e-6",
			"minDataPad" 			: "75"
		},
		"stepResponseAnalysis" : {
			"FitTol"				: "1.e-7",
			"FitIters"				: "50000",
			"UnlinkRCConst" 		: "1"
		},
		"multiStateAnalysis" : {
            "FitTol"				: "1.e-7",
            "FitIters"				: "50000",
            "InitThreshold"			: "2.5",
            "MinStateLength"		: "10",
            "MaxEventLength" 		: "10000",
            "UnlinkRCConst" 		: "1"
	     },
	     "cusumLevelAnalysis": {
			"StepSize": 3.0, 
			"MinThreshold": 3.0,
			"MaxThreshold": 10.0,
			"MinLength" : 10
    	}, 
		"besselLowpassFilter" : {
			"filterOrder"			: "6",
			"filterCutoff"			: "10000",
			"decimate"				: "1"	
		},
		"waveletDenoiseFilter" : {
			"wavelet"				: "sym5",
			"level"					: "5",
			"thresholdType"			: "soft",
			"thresholdSubType"		: "sqtwolog"
		},
		"abfTrajIO" : {
			"filter"				: "*.abf", 
			"start"					: 0.0, 
			"dcOffset"				: 0.0
		},
		"qdfTrajIO": {
			"Rfb": 9.1e+12, 
			"Cfb": 1.07e-12, 
			"dcOffset": 0.0, 
			"filter": "*.qdf", 
			"start": 0.0
		},
		"binTrajIO": {
			"AmplifierScale": "1.0", 
			"AmplifierOffset": "0.0", 
			"SamplingFrequency": "50000",
			"HeaderOffset": "0",
			"ColumnTypes": "[('curr_pA', 'float64')]",
			"IonicCurrentColumn" : "curr_pA",
			"dcOffset": "0.0", 
			"filter": "*.bin", 
			"start": "0.0"
		}
	}
"""