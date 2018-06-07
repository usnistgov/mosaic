import copy
from nose.tools import raises
import mosaic.mdio.metaMDIO as metaMDIO
import mosaic.mdio.sqlite3MDIO as sqlite3MDIO
from mosaic.utilities.resource_path import resource_path
from mosaic.utilities.ionic_current_stats import OpenCurrentDist
import numpy as np

class MDIOTest(object):
	@raises(metaMDIO.InsufficientArgumentsError)
	def runTestErrors(self, sdict):
		s=sqlite3MDIO.sqlite3MDIO()
		s.initDB(**sdict)

	def runTestAttributes(self, dbname, attr):
		s=sqlite3MDIO.sqlite3MDIO()
		s.openDB(dbname)

		assert len(str(getattr(s, attr))) > 0


class MDIOTest_TestSuite(MDIOTest):
	def test_mdioerror(self):
		for sdict in [
				{"dbPath": "dbpath", "colNames" : []},
				{"dbPath": "dbpath", "colNames_t" : []},
				{"colNames": [], "colNames_t" : []}
			]:
			yield self.runTestErrors, sdict


	def test_mdioattr(self):
		for attr in ['mdColumnNames', 'mdColumnTypes', 'dbFile', '_generateRecordKey']:
			yield self.runTestAttributes, resource_path("eventMD-PEG28-ADEPT2State.sqlite"), attr