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
				tableName   name of database table. Default is 'metadata'
		"""
		if not hasattr(self, 'tableName'):
			self.tableName='metadata'
		if not hasattr(self, 'colNames'):
			raise metaMDIO.InsufficientArgumentsError("Missing arguments: 'colNames' must be supplied to initialize {0}".format(type(self).__name__))
		if not hasattr(self, 'colNames_t'):
			raise metaMDIO.InsufficientArgumentsError("Missing arguments: 'colNames_t' must be supplied to initialize {0}".format(type(self).__name__))

		dbTimeout=kwargs.pop('timeout', 11.0)

		self.dbFilename=self.dbPath+'/'+'eventMD-' +str(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))+'.sqlite'
		self.db = sqlite3.connect(self.dbFilename, detect_types=sqlite3.PARSE_DECLTYPES, timeout=dbTimeout)

		self._setuptables()

	def _opendb(self, dbname, **kwargs):
		if not hasattr(self, 'tableName'):
			self.tableName='metadata'
		try:
			self.colNames=kwargs['colNames']
		except AttributeError, err:
			raise metaMDIO.InsufficientArgumentsError("Missing arguments: 'colNames' must be supplied to initialize {0}".format(type(self).__name__))
		try:
			self.colNames_t=kwargs['colNames_t']
		except AttributeError, err:
			raise metaMDIO.InsufficientArgumentsError("Missing arguments: 'colNames_t' must be supplied to initialize {0}".format(type(self).__name__))
		
		# if not hasattr(self, 'colNames_t'):
		# 	raise metaMDIO.InsufficientArgumentsError("Missing arguments: 'colNames_t' must be supplied to initialize {0}".format(type(self).__name__))
		
		self.db = sqlite3.connect(dbname, detect_types=sqlite3.PARSE_DECLTYPES)
		
		self._setuptables()

	def closeDB(self):
		self.db.commit()
		self.db.close()
		
	def writeRecord(self, data):
		placeholders_list=','.join(['?' for i in range(len(data))])

		with self.db:
			self.db.execute(	'INSERT INTO ' + 
						self.tableName + 
						'('+', '.join(self.colNames)+') VALUES('+
						placeholders_list+')', self._datalist(data)
					)

	def queryDB(self, query):
		try:
			self.db.commit()
			c = self.db.cursor()

			colnames=self._col_names(query, c, self.tableName)
			colnames_t=list(str(c) for c in (c.execute( 'select '+','.join(colnames)+' from '+self.tableName+'_t' ).fetchall())[0])

			c.execute(str(query))
		
			return [ self._decoderecord(colnames, colnames_t, rec) for rec in c.fetchall() ]
		except sqlite3.OperationalError, err:
			print err

	def _col_names(self, query, c, tablename):
			cols=[]
			for word in query.split()[1:]:
				if word == 'from':
					break
				
				cols+=[word]

			c1=[ c.rstrip(',') for c in cols ]
			if c1[0]=='*':
				return [ str(row[1]) for row in c.execute('PRAGMA table_info('+tablename+'_t)').fetchall() ]
			else:
				return c1

	def _setuptables(self):
		c = self.db.cursor()
		
		# check to see if tables exist
		tables=[]
		for row in c.execute("SELECT name FROM sqlite_master WHERE type='table'"):
			tables.append(row)

		
		# create a new table for event meta-data
		if (self.tableName,) not in tables:
			c.execute( 
				'create table ' + self.tableName + 
				' ( recIDX INTEGER PRIMARY KEY AUTOINCREMENT, ' + 
				self._sqltypes() + ' );' 
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
					placeholders_list+')', ('REAL',)+tuple(self.colNames_t)
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
		# recidx=self._generateRecordKey()
		d=data_record( self.colNames, data, self.colNames_t )
		return  tuple( [ d[col] for col in self.colNames ] )
		
	def _decoderecord(self, colnames, colnames_t, rec):
		d=data_record( colnames, rec, colnames_t )
		return [ d[col] for col in colnames ]

if __name__=="__main__":
	c=sqlite3MDIO()
	c.openDB('/Users/arvind/Research/Experiments/PEG29EBSRefData/20120323/singleChan/eventMD2014-05-19 10.50 PM.sqlite')
	
	q=c.queryDB( "select BlockDepth from metadata" )[:10]
	print "results:"
	print q
	
	