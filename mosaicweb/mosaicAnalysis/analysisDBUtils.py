"""
	A module that converts a MOSAIC sqlite database to CSV or other formats.

	:Created:	6/11/2017
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		6/11/17		AB 	Initial version
"""
import base64

import mosaic.mdio.sqlite3MDIO as sqlite
from mosaic.utilities.sqlQuery import rawQuery
from mosaic.utilities.resource_path import path_separator
from mosaic.utilities.util import bytes_, str_
import mosaic.errors as errors

class analysisDBUtils:
	def __init__(self, dbfile, qstr):
		self.AnalysisDBFile=dbfile 
		# self.queryString=qstr 

		# Always export all columns except the RecIdx and TimeSeries. Ignore a user provided qstr for now.
		self.queryString = "select "+", ".join([ col[1] for col in rawQuery(self.AnalysisDBFile, "PRAGMA table_info(metadata);") ][1:-1])+" from metadata"

		self.responseDict={}

	def csv(self):
		dbHnd=sqlite.sqlite3MDIO()
		dbHnd.openDB(self.AnalysisDBFile)

		self.responseDict["dbName"]=self.AnalysisDBFile.split(path_separator())[-1].split('.')[0]
		self.responseDict["dbData"]=str_(base64.b64encode(bytes_(dbHnd.csvString(self.queryString))))

		return self.responseDict

if __name__ == '__main__':
	import mosaic

	a=analysisDBUtils(mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite", "select ProcessingStatus, BlockDepth, ResTime from metadata limit 5")
	r=a.csv()

	print(r)
	print(base64.b64decode(r['dbData']))

