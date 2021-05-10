# -*- coding: utf-8 -*-
"""
Parse Chimera VC100 settings file for ADC parameters.

	:Created: 5/08/2021
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		5/09/21		AB 	Add support for MAT settings file
		5/08/21		AB 	Add a check to verify version entry to ensure it is a valid settings file.
		5/08/21     AB	Initial version
"""
import csv
import scipy.io
import mosaic.utilities.mosaicLogging as mlog

class ChimeraSettingsDict(dict):
	def __init__(self, settingsFileName):
		self.chimeraSettingsLogger=mlog.mosaicLogging().getLogger(name=__name__)
		self._setupSettingsKeys()

		try:
			if settingsFileName.split('/')[-1].split('.')[-1]=='mat':
				self._readMATSettingsFile(settingsFileName)
			else:
				self._readTextSettingsFile(settingsFileName)
		except FileNotFoundError as err:
			self.chimeraSettingsLogger.error(err)
			self.clear()

		try:
			if self.__version__>=1:
				pass
			else:
				self.clear()
		except:
			self.chimeraSettingsLogger.error("Invalid version number. Cannot verify valid Chimera settings.")
			self.clear()

		self["ColumnTypes"]=[('curr_pA', '<u2')]
		self["IonicCurrentColumn"]="curr_pA"

		for key, value in self.items():
			self.chimeraSettingsLogger.info("{0}  : {1}".format(key, value))


	def __getitem__(self, key):
		try:
			val = dict.__getitem__(self, key)

			return val
		except KeyError as err:
			self.chimeraSettingsLogger.error("Key {0} was not found.".format(err))

	def pop(self, key, default):
		try:
			return self[key]
		except KeyError:
			return default
	
	def extractParam(self, line):
		try:
			if line[0]=='__version__':
				self.__version__=float(line[1])
				self.chimeraSettingsLogger.info("Chimera settings version={0}".format(self.__version__))
				return {}
			if line[0]=='__header__':
				self.__header__=line[1]
				self.chimeraSettingsLogger.info("Chimera settings header={0}".format(self.__header__))
				return {}
		except:
			return {}

		d=line[0].split('_')
		if d[0]=='SETUP':
			return {self.settingsKeys[d[1]] : float(line[1])}
		else:
			return {}
	
	def _readTextSettingsFile(self, settingsFileName):
		with open(settingsFileName, 'r') as csvfile:
			statereader = csv.reader(csvfile, delimiter='=', quotechar='|')
			
			[ self.update(self.extractParam(row)) for row in statereader if len(row) > 1 ]

	def _readMATSettingsFile(self, settingsFileName):
		sett=scipy.io.loadmat(settingsFileName)

		try:
			self.__version__=float(sett["__version__"])
			self.chimeraSettingsLogger.info("Chimera settings version={0}".format(self.__version__))
			self.__header__=str(sett["__header__"])
			self.chimeraSettingsLogger.info("Chimera settings header={0}".format(self.__header__))

			for key, val in sett.items():
				if key.startswith("SETUP"):
					self.update({ self.settingsKeys[key.split('_')[-1]] : val[0][0]})

		except KeyError as err:
			self.chimeraSettingsLogger.error("Key {0} was not found.".format(err))

	def _setupSettingsKeys(self):
		self.settingsKeys={
			"ADCSAMPLERATE"	:	"SamplingFrequency",
			"mVoffset"		:	"mVoffset",
			"biasvoltage"	:	"biasvoltage",
			"pAoffset"		:	"pAoffset",
			"TIAgain"		:	"TIAgain",
			"ADCVREF"		:	"ADCvref",
			"ADCBITS"		:	"ADCbits",
			"preADCgain"	:	"preADCgain"

		}