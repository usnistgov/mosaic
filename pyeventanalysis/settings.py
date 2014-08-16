"""
	Load settings for the system from a JSON file. 

	Author: 	Arvind Balijepalli
	Created:	9/24/2012

	ChangeLog:
		8/6/14		AB 	Add a function to parse a settings string.
		9/5/13		AB 	Check for either .settings or settings in data directory
						and code root. Warn when using default settings
		8/24/12		AB	Initial version	
"""
import json
import os
import os.path

class settings:
	def __init__(self, datpath):
		"""
			Initialize a settings object. Look for a settings/.settings file first
			in the directory where the data is stored passed by datpath and
			then in the current working directory. If a settings/.settings file is not
			found in either location return without an error
		"""
		if os.path.isfile(datpath+'/.settings'):
			self.settingsFile=datpath+"/.settings"
		elif os.path.isfile(datpath+'/settings'):
			self.settingsFile=datpath+"/settings"
		elif os.path.isfile('.settings'):
			print "Settings file not found in data directory. Default settings will be used."
			self.settingsFile=os.getcwd()+"/settings"
		elif os.path.isfile('settings'):
			print "Settings file not found in data directory. Default settings will be used."
			self.settingsFile=os.getcwd()+"/.settings"

		self.parseSettingsString( "".join((open(self.settingsFile, 'r').readlines())) )

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
