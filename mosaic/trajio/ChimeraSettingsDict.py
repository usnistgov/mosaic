# -*- coding: utf-8 -*-
"""
Parse Chimera VC100 settings file for ADC parameters.

	:Created: 5/08/2021
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		5/08/21		AB 	Add a check to verify version entry to ensure it is a valid settings file.
		5/08/21     AB	Initial version
"""
import csv

class ChimeraSettingsDict(dict):
	def __init__(self, settingsFileName):
		with open(settingsFileName, 'r') as csvfile:
			statereader = csv.reader(csvfile, delimiter='=', quotechar='|')
			
			[ self.update(self.extractParam(row)) for row in statereader if len(row) > 1 ]

		try:
			if self.__version__>=1:
				pass
			else:
				self.clear()
		except:
			self.clear()

	def __getitem__(self, key):
		try:
			val = dict.__getitem__(self, key)

			return val
		except KeyError as err:
			print("Key {0} was not found.".format(err))

	def pop(self, key, default):
		try:
			return self[key]
		except KeyError:
			return default
	
	def extractParam(self, line):
		try:
			if line[0]=='__version__':
				self.__version__=float(line[1])
				return {}
		except:
			return {}

		d=line[0].split('_')
		if d[0]=='SETUP':
			if d[1]=="ADCSAMPLERATE":
				return {"SamplingFrequency": float(line[1])}
			else:
				return {d[1]: float(line[1])}
		else:
			return {}
	
