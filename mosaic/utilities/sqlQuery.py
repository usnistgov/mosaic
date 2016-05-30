"""
	Wrapper function for sqliteMDIO
"""
import mosaic.sqlite3MDIO as sql

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