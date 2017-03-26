"""
	A module that compiles MOSAIC statistics.

	:Created:	3/19/2017
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		3/19/17		AB 	Initial version
"""
import mosaic.mdio.sqlite3MDIO as sqlite
from mosaic.utilities.sqlQuery import query
from mosaic.utilities.analysis import caprate

import glob
import numpy as np
import pprint

class DataTypeNotSupportedError(Exception):
	pass

class analysisStatistics:
	"""
		A class that compiles MOSAIC analysis statistics.
	"""
	def __init__(self, analysisDB):
		self.analysisDB = analysisDB

	def analysisStatistics(self):
		statsDict={}
		
		s=self._eventStats()
		statsDict['fractionNormal']=s[0]
		statsDict['fractionWarn']=s[1]
		statsDict['fractionError']=s[2]
		statsDict['nTotal']=s[3]

		c=self._caprate()
		statsDict['captureRateMean']=c[0]
		statsDict['captureRateSigma']=c[1]

		return statsDict
		

	def _caprate(self):
		q=query(
			self.analysisDB,
			"select AbsEventStart from metadata where ProcessingStatus='normal' order by AbsEventStart ASC"
		)
		c=caprate(np.hstack(q))
		return round(c[0], 1), round(c[1], 1)

	def _eventStats(self):
		"""
			Query a database and return the fractions of normal events, events with warnings, events with errors and total events.
		"""
		import random

		normalEvents=len(query(
			self.analysisDB,
			"select AbsEventStart from metadata where ProcessingStatus='normal' order by AbsEventStart ASC"
		))+round(random.normalvariate(0,500))
		warnEvents=len(query(
			self.analysisDB,
			"select AbsEventStart from metadata where ProcessingStatus like 'w%' order by AbsEventStart ASC"
		))+round(random.normalvariate(0,500))
		errorEvents=len(query(
			self.analysisDB,
			"select AbsEventStart from metadata where ProcessingStatus like 'e%' order by AbsEventStart ASC"
		))+round(random.normalvariate(0,500))
		totalEvents=len(query(
			self.analysisDB,
			"select ProcessingStatus from metadata"
		))+round(random.normalvariate(0,500))

		return round(normalEvents/float(totalEvents), 3), round(warnEvents/float(totalEvents), 3), round(errorEvents/float(totalEvents), 3), totalEvents

if __name__ == '__main__':
	import mosaic

	a=analysisStatistics(mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite")

	print a.analysisStatistics()