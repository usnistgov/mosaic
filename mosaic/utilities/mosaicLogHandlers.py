import logging

__all__=["sqliteHandler"]

class sqliteHandler(logging.Handler):
	def __init__(self, dbHnd, **kwargs):
		self.dbHnd=dbHnd
		super(sqliteHandler,self).__init__(**kwargs)

	def emit(self, record):
		logmsg=self.format( record )
		self.dbHnd.writeAnalysisLog( self.dbHnd.readAnalysisLog()+logmsg )