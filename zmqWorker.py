import zmqIO
import cPickle


class InvalidFunctionName(Exception):
	pass

def zmqWorker(inchdict, outchdict, workfuncname):
	"""
		Setup two zmq channels, one to receive data and another to return results. Run an
		infinite loop waiting for work. Processing stopped when the message 'STOP' is received
		over the input channel.
	"""
	# setup the input and output channels
	outchan=zmqIO.zmqIO(zmqIO.PUSH, outchdict)
	inchan=zmqIO.zmqIO(zmqIO.PULL, inchdict)

	outchanname=outchdict.keys()[0]
	try:
		while True:
			data=inchan.zmqReceiveData()
			if data != "":
				if data=='STOP':
					break

				# unpickle the object
				procObj=cPickle.loads( data )

				# get a handle to the function to call
				func = getattr(procObj, workfuncname)
				if not func:
					raise InvalidFunctionName("Function %s not implemented" % workfuncname)
				
				# process the object
				func()
				#print procObj.mdProcessingStatus
				# pickle and return the results
				outchan.zmqSendData(outchanname, cPickle.dumps(procObj))

	except KeyboardInterrupt:
		pass

	inchan.zmqShutdown()
	outchan.zmqShutdown()