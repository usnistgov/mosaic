#!/usr/bin/env python
"""
	Query a MOSAIC database

	:Created:	3/23/2015
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.txt
	:ChangeLog:
	.. line-block::
		3/23/15		AB	Initial version
		7/5/16 		AB 	Updated code to use new module layout
"""

import argparse
import os
import mosaic.mdio.sqlite3MDIO as sqlite3MDIO
import sqlite3

def parseCLArgs():
	parser = argparse.ArgumentParser(description='Query a MOSAIC database')
	parser.add_argument('dbname', help='database name')
	parser.add_argument('query', help='SQL query')
	parser.add_argument('--raw', help='run a raw query', action='store_true')
	
	return parser.parse_args()


def main():
	args=parseCLArgs()

	db=sqlite3MDIO.sqlite3MDIO()
	db.openDB(args.dbname)

	if args.raw:
		return [ list(l) for l in db.rawQuery(args.query) ]
	else:
		return db.queryDB(args.query)


if __name__ == '__main__':
	try:
		print str(main())
	except sqlite3.OperationalError, err:
		print err
	except:
		print "Error when querying the database."
