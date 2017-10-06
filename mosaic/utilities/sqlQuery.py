"""
	Wrapper function for sqliteMDIO
"""
import mosaic.mdio.sqlite3MDIO as sql

__all__=["query"]

def query(dbname, query_str):
	"""
		Simple wrapper to perform a query on a MOSAIC database.
	"""
	db=sql.sqlite3MDIO()
	db.openDB(dbname)
	q=db.queryDB(query_str)
	db.closeDB()

	return q

def rawQuery(dbname, query_str):
	"""
		Simple wrapper to perform a raw query on a MOSAIC database.
	"""
	db=sql.sqlite3MDIO()
	db.openDB(dbname)
	q=db.rawQuery(query_str)
	db.closeDB()

	return q