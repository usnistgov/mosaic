# -*- coding: utf-8 -*-
"""
Parse Chimera VC100 settings file for ADC parameters.

	:Created: 5/08/2021
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		5/08/21     AB	Initial version
"""
import csv

class ChimeraSettingsDict(dict):
	def __init__(self, settingsFileName):
		with open(settingsFileName, 'r') as csvfile:
			statereader = csv.reader(csvfile, delimiter='=', quotechar='|')
			
			[ self.update(self.extractParam(row)) for row in statereader if len(row) > 1 ]

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
		d=line[0].split('_')
		if d[0]=='SETUP':
			if d[1]=="ADCSAMPLERATE":
				return {"SamplingFrequency": float(line[1])}
			else:
				return {d[1]: float(line[1])}
		else:
			return {}
	
if __name__ == "__main__":
	s=ChimeraSettingsDict("K439PC - pH 10 1M KCl G 104.5mScm - pH 8 3.6M LiCl G 164.3mScm - -200mV 31nM 750-b-p dsDNA EXP2 .txt")

	print(s)

	print(s["SamplingFrequency"])
	print(s["ADCSAMPLERATE"])

	
