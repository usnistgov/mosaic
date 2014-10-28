# """
# 	Load settings for the system from a JSON file. 

# 	Author: 	Arvind Balijepalli
# 	Created:	9/24/2012

# 	ChangeLog:
# 		8/20/14		AB 	Changed precedence of settings file search to datpath/.settings,
# 						datpath/settings, coderoot/.settings and coderoot/settings
# 		8/6/14		AB 	Add a function to parse a settings string.
# 		9/5/13		AB 	Check for either .settings or settings in data directory
# 						and code root. Warn when using default settings
# 		8/24/12		AB	Initial version	
# """
import json
import os
import os.path

class settings:
	def __init__(self, datpath, defaultwarn=True):
		"""
			Initialize a settings object. Look for a settings/.settings file first
			in the directory where the data is stored passed by datpath and
			then in the current working directory. If a settings/.settings file is not
			found in either location return without an error
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
			Get settings for a specified section as a Python dict.
			Return an empty dictionary if the settings file doesn't exist
			the section is not found.
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
			"reserveNCPU"			: "2",
			"plotResults"			: "0"
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
			"BlockRejectRatio"		: "0.9"
		},
		"multiStateAnalysis" : {
	                "FitTol"		: "1.e-7",
	                "FitIters"		: "50000",
	                "InitThreshold"	: "5.0"
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
		}
	}
"""