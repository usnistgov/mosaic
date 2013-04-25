import zmq
import time
import sys
import os
import logging
import traceback

# enumerated types
PUBLISH		= 0
SUBSCRIBE	= 1
PUSH		= 2
PULL		= 3
	
###########################################################################
# Alternative dictionary-based zmqIO class that uses named channels when 
# sending/ publishing data.
#
###########################################################################

class IllegalConnectionType(Exception):
	pass
	
class zmqIO():
	# Constructor that replicates the functionality of C++ code
	#	zmqIO(int moduleID, int type, std::vector< std::string > url)
	#		moduleID must be an integer starting at 1001
	#		type is either PUBLISH, SUBSCRIBE, REQUEST or REPLY
	#		url is a list of strings with the format "host:port"
	def __init__(self, type, urldict, transport="tcp"):
		self.mContext = zmq.Context()
		self.mSocketType = type;
		
		self.mURLDict=urldict
		try:
			if( self.mSocketType == SUBSCRIBE or self.mSocketType == PULL ):
				if( self.mSocketType == SUBSCRIBE):
					self.mSockets = self.mContext.socket(zmq.SUB)
				else:
					self.mSockets = self.mContext.socket(zmq.PULL)
				
				# connect all subscribe sockets
				for (k,v) in urldict.iteritems():
					self.mSockets.connect( transport+"://" + v )

				# turn off any filtering on subscribe sockets
				if( self.mSocketType == SUBSCRIBE):
					self.mSockets.setsockopt(zmq.SUBSCRIBE, "")	
				
				self.mPoller=zmq.Poller()
				self.mPoller.register(self.mSockets, zmq.POLLIN)
				
			elif( self.mSocketType == PUBLISH or self.mSocketType == PUSH ):
				self.mSockets={}
				for (k,v) in urldict.iteritems():
					if (self.mSocketType == PUBLISH):
						s = self.mContext.socket(zmq.PUB)
					else:
						s = self.mContext.socket(zmq.PUSH)

					s.bind( transport+"://" + v )
					
					# allow the socket to handshake with subscribers. This should be fixed later
					time.sleep(0.25)
					self.mSockets[k] = s
			else:
				raise IllegalConnectionType("Unknown socket type.")
		except IllegalConnectionType, e:
			print( "{0}, IllegalConnectionType: {1}\n. Exiting!".format(os.path.basename(sys.argv[0]),e) )
			exit(-1)
		except:
			raise
			
	# publish data on a selected channel. this function
	# replicates the C++ function
	#	zmqPublishData( int chan, const std::string &data )
	#		chan is an integer that corresponds to the 
	#			 socket position in url (see above)
	#		data is a string
	def zmqSendData( self, chan, data ):
		try:
			if self.mSocketType==PUBLISH or self.mSocketType==PUSH:
				self.mSockets[chan].send( data )
				time.sleep(2e-6)
		except KeyboardInterrupt:
			raise
	# receive data on any channel. This is a non-blocking receive
	# which returns the message on any 0MQ channel or a 
	# blank string when there is no message. It is complementary
	# to the C++ function
	#	zmqSubscribeData( std::string &data )
	#		However, the python version takes no arguemnts
	def zmqReceiveData( self, timeout=0 ):
		try:
			socks = dict(self.mPoller.poll(timeout))

			if socks and socks.get(self.mSockets) == zmq.POLLIN:
				return self.mSockets.recv()
			else:
				return ""
		except KeyboardInterrupt:
			raise
			
	def zmqShutdown( self, exitproc=False ):
		# first close and/or unbind all the sockets
		#print "Closing network connections...",
		sys.stdout.flush()
		if( self.mSocketType==PUBLISH or self.mSocketType==PUSH):
			for (k,v) in self.mSockets.iteritems():
				self.mSockets[k].close()
		else:
			self.mSockets.close()
		time.sleep(1)
		#print "done."
		if exitproc is True: 
			exit()
		