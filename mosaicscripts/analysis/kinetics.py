#!/usr/bin/env python
""" 
	Functions to extract kinectics from analysis database.

	:Created:	12/26/2015
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		12/26/15		AB	Initial version
"""
# -*- coding: utf-8 -*-
import mosaic.sqlite3MDIO as sql
import numpy as np

from mosaic.utilities.analysis import caprate

def query1Col(
        dbname, 
        query_str="select AbsEventStart from metadata where ProcessingStatus='normal' and ResTime > 0.02 order by AbsEventStart ASC"
	):
	"""
		Simple wrapper to perform a single column query on a MOSAIC database.
	"""
	db=sql.sqlite3MDIO()
	db.openDB(dbname)
	q=db.queryDB(query_str)
	db.closeDB()

	return np.hstack(q)

def CaptureRate(dbname, queryString):
	"""
		A wrapper for `mosaic.utilities.analysis.caprate` that calculates the capture rate from the `AbsEventStart` column of a MOSAIC database.

		:Args:
			- `dbname` :		Valid path to a sqlite database file
			- `queryString` :	SQL query string.

	"""
	return caprate(	query1Col( dbname, queryString ) )