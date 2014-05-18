import sqlite3
import base64
import struct
import datetime

import numpy
import metaMDIO

class data_record(dict):
	"""
		Smart data record structure that automatically encodes/decodes data for storage
		in a sqlite3 DB.
	"""
	def __init__(self, data_label, data, data_t):
		self.update( dict(zip( data_label, zip(data_t, data))) )

		self.dtypes=dict( zip(data_label, data_t) )

	def __setitem__(self, key, val):
		dat=val[1]

		if val[0].endswith('_LIST'):
			if val[0]=='REAL_LIST':
				(packstr, bytes) = ('%sd', 8)
			elif val[0]=='INTEGER_LIST':
				(packstr, bytes) = ('%si', 4)

			if isinstance(val[1], unicode):
				decoded_data=base64.b64decode(val[1])
				dat = list(struct.unpack( packstr % int(len(decoded_data)/bytes), decoded_data ))
			else:
				dat = base64.b64encode(struct.pack( packstr % len(val[1]), *val[1] ))
		
		dict.__setitem__(self, key, dat)

	def __getitem__(self, key):
		return dict.__getitem__(self, key)

	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v

class sqlite3MDIO(metaMDIO.metaMDIO):
	"""
	"""
	def _initdb(self, **kwargs):
		"""
			Initialize the database tables
			
			Args:
				colNames 	list of text names for the columns in the tables
				colNames_t	list of data types for each column. 
				tableName   name of database table. Default is 'metadata'
		"""
		if not hasattr(self, 'tableName'):
			self.tableName='metadata'
		if not hasattr(self, 'colNames'):
			raise metaMDIO.InsufficientArgumentsError("Missing arguments: 'colNames' must be supplied to initialize {0}".format(type(self).__name__))
		if not hasattr(self, 'colNames_t'):
			raise metaMDIO.InsufficientArgumentsError("Missing arguments: 'colNames_t' must be supplied to initialize {0}".format(type(self).__name__))

		self.recIdx=0
		self.dbFilename='eventMD' +str(datetime.datetime.now().strftime('%Y-%m-%d %I.%M %p'))+'.sqlite'
		self.db = sqlite3.connect(self.dbPath+'/'+self.dbFilename, detect_types=sqlite3.PARSE_DECLTYPES)

		self._setuptables()

	def _opendb(self, dbname, **kwargs):
		if not hasattr(self, 'tableName'):
			self.tableName='metadata'

		self.db = sqlite3.connect(dbname, detect_types=sqlite3.PARSE_DECLTYPES)


	def closeDB(self):
		self.db.commit()
		self.db.close()
		
	def writeRecord(self, data):
		c=self.db.cursor()

		placeholders_list=','.join(['?' for i in range(len(data)+1)])

		c.execute(	'INSERT INTO ' + 
					self.tableName + 
					'(recIDX, '+', '.join(self.colNames)+') VALUES('+
					placeholders_list+')', self._datalist(data)
				)

		if self.recIdx % 10000 == 0:
			self.db.commit()

		self.recIdx+=1

	def queryDB(self, query):
		try:
			self.db.commit()

			c = self.db.cursor()

			colnames=[ str(row[1]) for row in c.execute('PRAGMA table_info('+self.tableName+'_t)').fetchall() ]
			colnames_t=list(str(c) for c in (c.execute( 'select * from '+self.tableName+'_t' ).fetchall())[0])

			c.execute(str(query))
		
			return [ self._decoderecord(colnames, colnames_t, rec) for rec in c.fetchall() ]
		except sqlite3.OperationalError, err:
			print err

	def _setuptables(self):
		c = self.db.cursor()
		
		# check to see if tables exist
		tables=[]
		for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
			tables.append(row)

		
		# create a new table for event meta-data
		if (self.tableName,) not in tables:
			c.execute('create table '+
				self.tableName+
				' ('+'recIDX INTEGER, '+ 
				self._sqltypes() +
				', PRIMARY KEY (recIDX)'+')'
			)
			# create a second table with native types and store them
			c.execute('create table '+
				self.tableName+'_t'+
				' ('+'recIDX TEXT, '+ 
				','.join(k+' TEXT' for k in self.colNames) +
				', PRIMARY KEY (recIDX)'+')'
			)
			placeholders_list=','.join(['?' for i in range(len(self.colNames)+1)])
			c.execute(	'INSERT INTO ' + 
					self.tableName+'_t' + 
					'(recIDX, '+', '.join(self.colNames)+') VALUES('+
					placeholders_list+')', ('INTEGER',)+tuple(self.colNames_t)
				)

		self.db.commit()

	def _sqltypes(self):
		sqlstring=[]
		for (k,v) in zip(self.colNames, self.colNames_t):
			if v.endswith('_LIST'):
				sqlstring.append( str(k)+' BLOB' )
			else:
				sqlstring.append( str(k)+' '+str(v) )

		return ', '.join(sqlstring)

	def _datalist(self, data):
		d=data_record( self.colNames, data, self.colNames_t )
		return  (self.recIdx,)+tuple( [ d[col] for col in self.colNames ] )
		
	def _decoderecord(self, colnames, colnames_t, rec):
		d=data_record( colnames, rec, colnames_t )
		return [ d[col] for col in colnames ]

if __name__=="__main__":
	c=sqlite3MDIO()
	c.initDB(
				dbPath='.', 
				tableName='metadata',
				colNames=['status', 'blockdepth', 'restime','timeseries'], 
				colNames_t=['TEXT','REAL','REAL','REAL_LIST']
			)
	for i in range(100):
		c.writeRecord( ["normal", i/12.0, i*12.0+6.8, numpy.array([1.,2.,3.,4.])*i/12.] )
	
	q=c.queryDB( "select * from metadata where ( blockdepth > 0.2 and status = 'normal')" )[:10]
	print "results:"
	print q
	
	