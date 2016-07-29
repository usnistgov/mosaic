import math
from struct import unpack
from numpy import * #arange,array,append, concatenate, fromfile, tofile, where, putmask, zeros, average, ravel, nonzero, ceil, mean, transpose
from operator import itemgetter

# Exception definitions
class QDFError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


class QDFNode:
#	Description:	Single node for a .qdf file.
#	Author: 		Daniel Lathrop
#	Methods:
#			read_node - reads a single node from a .qdf file
#			read_datafile_child - reads and processes a single node that is
#					the child of the DataFile node from a .qdf file
#			read_segment_node - reads and processes a single segment node
#					from a .qdf file
#			read_segment_child - reads and processes a single node that is
#					the child of a Segment node from a .qdf file
	def read_node(self, file, offset):
		file.seek(offset)
		(flag0,flag1,flag2,type,size,count) = unpack('BBBBII',file.read(12))
		(pos,child,sibling,res0,res1,res2,len) = unpack('IIIIHBB',file.read(20))
		self.name = file.read(len)
		if count > 0 :
			file.seek(pos)
			if type == 7:
				if size != 2:
					raise QDFError('Node Type and Size Mismatched: '+self.name)
				code = 'h'
			elif type == 9:
				if size != 4:
					raise QDFError('Node Type and Size Mismatched: '+self.name)
				code = 'i'
			elif type == 13:
				if size != 8:
					raise QDFError('Node Type and Size Mismatched: '+self.name)
				code = 'd'
			else:
				raise QDFError('Node Type Incorrect: '+self.name)
			if (count > 1):
				self.data = fromfile(file, code, count)
			else:
				self.data = unpack(code,file.read(size))
		else:
			if type != 0:
				QDFError('Node Type Incorrect: '+self.name)
			self.data = None
		# Set count, child, and sibling
		self.flag = flag0
		self.type = type
		self.size = size
		self.count = count
		self.child = child
		self.sibling = sibling
		#print self.name, self.flag,self.type,self.size,self.count,
		#print self.child,self.sibling,self.data

	def read_datafile_child(self, qdfobj, file, offset):
		self.read_node(file, offset)
		if self.name == 'Segments':
			if qdfobj.segmentcount == None:
				qdfobj.segmentcount = 0
			else:
				raise QDFError('Duplicate Node: '+self.name)
		else:
			if self.name == 'Sampling':
				if qdfobj.dt == None:
					qdfobj.dt = self.data[0]
				else:
					raise QDFError('Duplicate Node: '+self.name)
			elif self.name == 'Scaling':
				if qdfobj.scale == None:
					qdfobj.scale = self.data[0]
				else:
					raise QDFError('Duplicate Node: '+self.name)
			elif self.name == 'ADChannelCount':
				if qdfobj.channelcount == None:
					qdfobj.channelcount = self.data[0]
					if qdfobj.channelcount != 1:
						raise QDFError('Channel Count Must Be 1')
				else:
					raise QDFError('Duplicate Node: '+self.name)
			elif self.name == 'ADDataSize':
				if qdfobj.datasize == None:
					qdfobj.datasize = self.data[0]
				else:
					raise QDFError('Duplicate Node: '+self.name)
			elif self.name == 'ADDataType':
				if qdfobj.datatype == None:
					qdfobj.datatype = self.data[0]
				else:
					raise QDFError('Duplicate Node: '+self.name)
			else:
				raise QDFError('Node Not Recognized A: '+self.name)
			if self.child:
				raise QDFError('Unexcepted Child: '+self.name)

	def read_segment_node(self, qdfobj, file, offset, t_range):
		self.read_node(file, offset)
		if self.name != 'Segment':
			raise QDFError('Node Not Recognized B: '+self.name)
		qdfobj.segmentcount += 1
		if self.sibling:
			#print "making recursive call!!" #DEBUG
			node = QDFNode()
			node.read_segment_node(qdfobj, file, self.sibling, t_range)
			del node
		dfoffset = self.child
		while dfoffset:
			node = QDFNode()
			node.read_segment_child(qdfobj, file, dfoffset, t_range)
			dfoffset = node.sibling
			del node
# 		if qdfobj.starttime == None:
# 			raise QDFError('Node Missing: StartTime')
# 		if qdfobj.data == None:
# 			raise QDFError('Node Missing: Channels')

	def read_single_segment_node(self, qdfobj, file, offset):
		qdfobj.starttime = None
		qdfobj.data = None
		self.read_node(file, offset)
		if self.name != 'Segment':
			raise QDFError('Node Not Recognized B: '+self.name)
		## store pointer to next data segment
		qdfobj.thisSegmentOffset = qdfobj.nextSegmentOffset
		if self.sibling:
			qdfobj.nextSegmentOffset = self.sibling
		else:
			qdfobj.nextSegmentOffset = None
		dfoffset = self.child
		## fetch data
		while dfoffset:
			node = QDFNode()
			node.read_segment_child(qdfobj, file, dfoffset, None)
			dfoffset = node.sibling
			del node

	def read_segment_child(self, qdfobj, file, offset, t_range):
		self.read_node(file, offset)
		if self.name == 'StartTime':
 			if qdfobj.starttime == None:
				qdfobj.starttime = [self.data[0],]
			else:
				qdfobj.starttime.insert(0,self.data[0])
		elif self.name == 'Channels':
			if t_range:
				if qdfobj.starttime[0] > t_range[1] or (qdfobj.starttime[0] + (len(self.data) * qdfobj.dt) < t_range[0]):
					qdfobj.starttime = qdfobj.starttime[1:]
					return
				#handle central and rhs sections
				if qdfobj.starttime[0] > t_range[0]:
					n_points_right = int(float(t_range[1] - qdfobj.starttime[0]) / qdfobj.dt)
					self.data = self.data[:n_points_right]
				#handle left hand end
				if qdfobj.starttime[0] < t_range[0] and (qdfobj.starttime[0] + (len(self.data) * qdfobj.dt)) > t_range[0]:
					n_points_left = int(float(t_range[0] - qdfobj.starttime[0]) / qdfobj.dt)
					qdfobj.starttime[0] = float(t_range[0])
					self.data = self.data[n_points_left:]
  			if qdfobj.data != None:
				qdfobj.data = concatenate((self.data/qdfobj.scale, qdfobj.data))	
			else:
				qdfobj.data = self.data/qdfobj.scale
			del self.data
		else:
			raise QDFError('Node Not Recognized C: '+self.name)
	
	
class QDFDataFile(object):
#	Description:	Read and Write .qdf files
#	Author: 		Daniel Lathrop
#	Methods:
#			set_size - sets the integer size for writing (2 or 4 bytes)
#			read - reads a .qdf file
#			set_data - adds or replaces data
#			write - writes a .qdf file
	def __init__(self,filename, t_range = None, readData=1):
	#	Description:	Initialize class QDFDataFile
	#	Author: 		Daniel Lathrop
	#	Inputs:
	#			filename - if present, the file with this name is read
	#			readData - a flag indicating whether data is to be read.
	#						if readData=0, only  header information is read.
		if filename:
			self.read(filename, t_range, readData)
		else:
			self.datatype = 9
			self.datasize = 4
			self.scale = 0
			self.channelcount = 1
			self.segmentcount = 0
			self.filename = ''

	def set_size(self,datasize):
	#	Description:	Set the size of integers to write to the .qdf file
	#	Author: 		Daniel Lathrop
	#	Inputs:
	#			datasize - the size in bytes of the integers to write
	#						valid values are 2 and 4
		if datasize == 2:
			self.datasize = 2
			self.datatype = 7
		elif datasize == 4:
			self.datasize = 4
			self.datatype = 9
		else:
			print 'Invalid Integer Size'
	
	def read(self,filename, t_range=None, readData=1):
	#	Description:	Read class QDFDataFile from a .qdf file
	#	Author: 		Daniel Lathrop
	#	Inputs:
	#			filename - the file to read
	#			readData - a flag to indicate whether data is to be read from file
		# open file
		file = open(filename,mode = 'r+b')
		self.segmentcount = None
		self.dt = None
		self.scale = None
		self.channelcount = None
		self.datasize = None
		self.datatype = None
		self.starttime = None
		self.data = None
		try:
			# read and verify magic string
			magic = file.read(12)
			if magic != 'QUB_(;-)_QFS':
				raise QDFError('Magic String Incorrect: '+magic)

			# read DataFile node
			node = QDFNode()
			node.read_node(file, 12)
			if node.name != 'DataFile':
				raise QDFError('Node Not Recognized: '+node.name)
			if node.sibling > 0:
				raise QDFError('Unexpected Sibling: '+node.name)
			if node.child == 0:
				raise QDFError('Node Missing: DataFile Child')

			# read children of DataFile
			offset = node.child
			del node
			while offset :
				node = QDFNode()
				node.read_datafile_child(self, file, offset)
				if node.name == 'Segments' :
					self.lastSegmentOffset = node.child
					self.thisSegmentOffset = node.child
					segmentoffset = node.child
				offset = node.sibling
				del node


			# verify all children read
			if self.dt == None:
				raise QDFError('Missing Node: Sampling')
			if self.scale == None:
				raise QDFError('Missing Node: Scaling')
			if self.channelcount == None:
				raise QDFError('Missing Node: ADChannelCount')
			if self.datasize == None:
				raise QDFError('Missing Node: ADDataSize')
			if self.datatype == None:
				raise QDFError('Missing Node: ADDataType')
			if self.segmentcount == None:
				raise QDFError('Missing Node: Segments')
			if segmentoffset == 0:
				raise QDFError('Missing Node: Segment')

			# read segment
			if readData:
				node = QDFNode()
				node.read_segment_node(self, file, segmentoffset, t_range)
				del node
				file.close()
			else:
				self.filehandle = file
				self.nextSegmentOffset = segmentoffset

		# exceptions
		except QDFError, inst:
			print inst
		self.filename = filename
		
def qdf_V2I(fileList, Cfb, Rfb, scale_data=0, time_scale=0):
#	Description:	Performs a conversion of voltage to current for a list of qdf data files.
#	Author: 		Ryan Dunnam
#	Inputs:
#			data0 - the original voltage data
#			Cfb - the feedback capaciatance
#			Rfb - the feedback resistance
#			scale_data
#			time_scale

	if (fileList == 0):
		sys.exit("File list is empty")
	
	# Counter to use in for loop
	ncount = 0

	if (scale_data == 0):
		scale_idata = 10**12		# default is to convert to pA
	else:
		scale_idata = scale_data		# can apply other scaling factors (e.g. to mV or fA)
	
	if (time_scale == 0):
		itime_scale = 10**3			# default is time in ms
	else:
		itime_scale = time_scale
		
	# number of files
	nfiles = len(fileList)
	data=array([])
	dt=array([])
	sampleCount=int(0)
	
	for filename in fileList:
		#print "read " + filename
		file0 = QDFDataFile(filename)
		data0 = array(file0.data)
		dt=append(dt,file0.dt)
		
		# Handle cases of last and not last file
		if (ncount + 1 < nfiles):	# not on last file
			# open next file
			file1 = QDFDataFile(fileList[ncount + 1])
			# read in 1st point
			firstPoint = []
			firstPoint.append(file1.data[0])
			# make data1 array - time shift forward by 1
			data1 = concatenate([file0.data[1:],firstPoint])
			del file1
			
		else:	# on last file (or there is only 1) - final output will be 1 point shorter
			data1 = file0.data[1:]
			data0 = file0.data[0:-1]

		file0.data = (((-1.0 * data1/Rfb) - (Cfb * (data1 - data0)/(file0.dt))) * scale_idata)

		# get the number of data points
		n = int(file0.data.size)
		sampleCount+=n
		
		data=append(data, file0.data)

		del file0, data0, data1

	if (mean(dt/dt[0])!=1.0):
		sys.exit("Input files have different sampling rates")
	
	return transpose([(array(range(0, sampleCount))*dt[0]*itime_scale), data])

def qdf_I(fileList, Cfb, Rfb, scale_data=0, time_scale=0):
#	Description:	Performs a conversion of voltage to current for a list of qdf data files.
#	Author: 		Ryan Dunnam
#	Inputs:
#			data0 - the original voltage data
#			Cfb - the feedback capaciatance
#			Rfb - the feedback resistance
#			scale_data
#			time_scale

	if (fileList == 0):
		sys.exit("File list is empty")
	
	# Counter to use in for loop
	ncount = 0

	if (scale_data == 0):
		scale_idata = 1		# current is in pA
	else:
		scale_idata = scale_data		# can apply other scaling factors (e.g. to mV or fA)
	
	if (time_scale == 0):
		itime_scale = 10**3			# default is time in ms
	else:
		itime_scale = time_scale
		
	# number of files
	nfiles = len(fileList)
	data=array([])
	dt=array([])
	sampleCount=int(0)
	
	for filename in fileList:
		#print "read " + filename
		file0 = QDFDataFile(filename)
		data0 = array(file0.data)
		dt=append(dt,file0.dt)
		
		# Handle cases of last and not last file
		if (ncount + 1 < nfiles):	# not on last file
			# open next file
			file1 = QDFDataFile(fileList[ncount + 1])
			# read in 1st point
			firstPoint = []
			firstPoint.append(file1.data[0])
			# make data1 array - time shift forward by 1
			data1 = concatenate([file0.data[1:],firstPoint])
			del file1
			
		else:	# on last file (or there is only 1) - final output will be 1 point shorter
			data1 = file0.data[1:]
			data0 = file0.data[0:-1]

		file0.data = data1*scale_idata #(((-1.0 * data1/Rfb) - (Cfb * (data1 - data0)/(file0.dt))) * scale_idata)

		# get the number of data points
		n = int(file0.data.size)
		sampleCount+=n
		
		data=append(data, file0.data)

		del file0, data0, data1

	if (mean(dt/dt[0])!=1.0):
		sys.exit("Input files have different sampling rates")
	
	return transpose([(array(range(0, sampleCount))*dt[0]*itime_scale), data])

def fileList(path, prefix, start, end):
	return [("%s%s%04d.qdf" % (path, prefix, i)) for i in range(start,end+1)]
	

def ConvertQDFToCSV(infilelist, outfile, fbC, fbR):
	#return qdf_V2I(infilelist, fbC, fbR).tofile(outfile, sep=',')
	return qdf_I(infilelist, fbC, fbR).tofile(outfile, sep=',')
	


