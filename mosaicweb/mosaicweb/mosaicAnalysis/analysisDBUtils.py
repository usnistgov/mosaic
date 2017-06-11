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
from mosaic.utilities.sqlQuery import query, rawQuery
from mosaic.utilities.resource_path import path_separator
import mosaic.errors as errors

class analysisDBUtils:
	def __init__(self, dbfile, qstr):
		self.AnalysisDBFile=dbfile 
		self.queryString=qstr 

		self.responseDict={}

	def csv(self):
		dbHnd=sqlite.sqlite3MDIO()
		dbHnd.openDB(self.AnalysisDBFile)

		self.responseDict["dbName"]=self.AnalysisDBFile.split(path_separator())[-1].split('.')[0]
		self.responseDict["dbData"]=base64.b64encode(dbHnd.csvString(self.queryString))

		return self.responseDict

if __name__ == '__main__':
	import mosaic
	
	a=analysisDBUtils(mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite", "select ProcessingStatus, BlockDepth, ResTime from metadata limit 5")
	r=a.csv()

	print r
	print base64.b64decode(r['dbData'])

