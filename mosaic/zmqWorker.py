import zmqIO
import cPickle
import sqlite3MDIO

__all__ = ["zmqWorker", "InvalidFunctionName"]

class InvalidFunctionName(Exception):
	pass

def zmqWorker(inchdict, outchdict, workfuncname, dbSpec):
	"""
		Setup two zmq channels, one to receive data and another to return results. Run an
		infinite loop waiting for work. Processing stopped when the message 'STOP' is received
		over the input channel.
	"""
	# setup the input and output channels
	outchan=zmqIO.zmqIO(zmqIO.PUSH, outchdict)
	inchan=zmqIO.zmqIO(zmqIO.PULL, inchdict)

	outchanname=outchdict.keys()[0]

	# setup MDIO
	if dbSpec[0]=="sqlite3MDIO":
		db=sqlite3MDIO.sqlite3MDIO()
		db.openDB(dbSpec[1], colNames=dbSpec[2], colNames_t=dbSpec[3])
	
	while True:
		try:
			data=inchan.zmqReceiveData()
			if data != "":
				if data=='STOP':
					break

				# unpickle the object
				procObj=cPickle.loads( data )

				# First set the meta-data IO object in eventobj
				procObj.dataFileHnd=db

				# get a handle to the function to call
				func = getattr(procObj, workfuncname)
				if not func:
					raise InvalidFunctionName("Function %s not implemented" % workfuncname)
				
				# process the object
				func()
				#print procObj.mdProcessingStatus
				# pickle and return the results
				# outchan.zmqSendData(outchanname, cPickle.dumps(procObj))
				outchan.zmqSendData(outchanname, 'DONE')

		except KeyboardInterrupt:
			break

	inchan.zmqShutdown()
	outchan.zmqShutdown()

	db.closeDB()