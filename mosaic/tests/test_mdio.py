import os
import copy
import sqlite3
import pytest
import mosaic.mdio.metaMDIO as metaMDIO
import mosaic.mdio.sqlite3MDIO as sqlite3MDIO
from mosaic.utilities.resource_path import resource_path, format_path
from mosaic.utilities.ionic_current_stats import OpenCurrentDist
import numpy as np

class MDIOTest(object):
	def runTestErrors(self, sdict):
		with pytest.raises( (metaMDIO.InsufficientArgumentsError, sqlite3.OperationalError) ):
			s=sqlite3MDIO.sqlite3MDIO()
			s.initDB(**sdict)

	def runTestAttributes(self, dbname, attr):
		s=sqlite3MDIO.sqlite3MDIO()
		s.openDB(dbname)

		assert len(str(getattr(s, attr))) > 0

	def runTestdatarecord(self, data_label, data, data_t):
		d=sqlite3MDIO.data_record(data_label, data, data_t)

		assert len(list(d.keys())) > 0

	def runTestSQLQuery(self, dbname, q):
		s=sqlite3MDIO.sqlite3MDIO()
		s.openDB(dbname)

		d=s.executeSQL(q)

		s.closeDB()
		assert len(d) > 0

	def runTestCSVExport(self, dbname, q):
		s=sqlite3MDIO.sqlite3MDIO()
		s.openDB(dbname)

		d=s.exportToCSV(q)

		os.remove(format_path( s.dbFile.split('.')[0]+'.csv' ))

		s.closeDB()

@pytest.fixture
def mdioTestObject():
	return MDIOTest()

def test_mdioerror(mdioTestObject):
	for sdict in [
			{"dbPath": "dbpath", "colNames" : []},
			{"dbPath": "dbpath", "colNames_t" : []},
			{"colNames": [], "colNames_t" : []},
			{"dbPath": "dbpath", "colNames": [], "colNames_t" : []}
		]:
		mdioTestObject.runTestErrors(sdict)

def test_mdioattr(mdioTestObject):
	for attr in ['mdColumnNames', 'mdColumnTypes', 'dbFile', '_generateRecordKey']:
		mdioTestObject.runTestAttributes(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), attr)

def test_sqlquery(mdioTestObject):
	mdioTestObject.runTestSQLQuery(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), """select name from sqlite_master where type='table';""")

def test_csvexport(mdioTestObject):
	mdioTestObject.runTestCSVExport(resource_path("eventMD-PEG28-ADEPT2State.sqlite"), """select ProcessingStatus from metadata""")

def test_datarecord(mdioTestObject):
	for dat_t in ["REAL_LIST", "INTEGER_LIST"]:
		mdioTestObject.runTestdatarecord(['data'], [[0,1,2]], [dat_t])