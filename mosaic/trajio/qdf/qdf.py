# -*- coding: utf-8 -*-
"""
	Load QDF files based on the QUB specification (http://www.qub.buffalo.edu/qubdoc/files/qdf.html).

	:Created:	9/21/2016
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		9/22/16 	AB 	Cleanup variable names and header unpacking.
		9/21/16		AB	Initial version	
"""
import struct
import numpy as np 

qubDataTypes={
	28		:	"h",
	144		:	"i",
	3328	:	"d"
}

class qnode(object):
	"""
		A single node in the QUBTree.
	"""
	def __init__(self, fhnd, offset):
		self.fhnd=fhnd
		self.offset=offset

		self.dataType=0
		self.dataSize=0
		self.dataCount=0
		self.dataPos=0
		self.childOffset=0
		self.siblingOffset=0
		self.nameLen=0

		self._parsenode()

	def _parsenodeheader(self):
		self.fhnd.seek(self.offset)

		(
			flags, 
			self.dataType, 
			self.dataSize, 
			self.dataCount,
			self.dataPos,
			self.childOffset,
			self.siblingOffset,
			reserved,
			self.nameLen
		)= struct.unpack('3sBIIIII7sB', self.fhnd.read(32))

	def _parsenode(self):

		self._parsenodeheader()

		self.nodeName=self.fhnd.read(self.nameLen)

		if self.dataCount:
			self.fhnd.seek(self.dataPos)
			code=qubDataTypes[self.dataType<<self.dataSize]
			
			d=np.fromfile(self.fhnd, code, self.dataCount)
			if len(d)==1:
				self.data=d[0]
			else:
				self.data=d


class qtree(dict):
	"""
		A stripped down tree representation.
	"""
	def __init__(self, fhnd, offset):
		self.fhnd=fhnd
		self.hdrOffset=offset

	def parse(self):
		qn=qnode(self.fhnd, self.hdrOffset)
		
		if qn.childOffset:
			s=qnode(self.fhnd, qn.childOffset)
			self[s.nodeName]=s
	
			try:
				while s.siblingOffset:
					s=qnode(self.fhnd, s.siblingOffset)
					self[s.nodeName]=s
			except AttributeError:
				pass

			for k,v in self.iteritems():
				if v.childOffset:
					t=qtree(self.fhnd, v.childOffset)
					t.parse()
					self[k]=t

class QDFError(Exception):
	pass

class QDF(object):
	def __init__(self, filename, Rfb, Cfb):
		self.filename=filename
		self.Rfb=Rfb
		self.Cfb=Cfb

	def _parseQDFTree(self):
		fhnd=open(self.filename, 'r+b')
		self._checkMagic(fhnd)
		self.qdftree=qtree(fhnd, 12)
		self.qdftree.parse()


	def _checkMagic(self, fhnd):
		magic=fhnd.read(12)
		if magic != 'QUB_(;-)_QFS':
			raise QDFError("Incorrect magic string found: {0}".format(magic))


	def VoltageToCurrent(self, iscale=1e12):
		self._parseQDFTree()

		qt=self.qdftree

		dt=qt["Sampling"].data
		scale=qt["Scaling"].data
		dat=qt["Segments"]["Channels"].data/scale

		return (((-1.0 * dat[1:]/self.Rfb) - (self.Cfb * np.diff(dat)/dt)) * iscale)

	def Current(self, iscale=1e12):
		self._parseQDFTree()

		qt=self.qdftree
		
		scale=qt["Scaling"].data
		return (qt["Segments"]["Channels"].data/scale) * iscale


