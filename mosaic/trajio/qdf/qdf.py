# -*- coding: utf-8 -*-
"""
	Load QDF files based on the QUB specification (http://www.qub.buffalo.edu/qubdoc/files/qdf.html).

	:Created:	9/21/2016
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
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

		self.dattype=0
		self.datsize=0
		self.datcount=0
		self.nodepos=0
		self.childoffset=0
		self.siblingoffset=0

		self._parsenode()

	def _parsenodeheader(self):
		self.fhnd.seek(self.offset)

		(
			f0, 
			f1, 
			f2, 
			self.dattype, 
			self.datsize, 
			self.datcount,
			self.datpos,
			self.childoffset,
			self.siblingoffset,
			r0,
			r1,
			r2,
			self.namelen
		)= struct.unpack('BBBBIIIIIIHBB', self.fhnd.read(32))

	def _parsenode(self):

		self._parsenodeheader()

		self.nodename=self.fhnd.read(self.namelen)

		if self.datcount:
			self.fhnd.seek(self.datpos)
			code=qubDataTypes[self.dattype<<self.datsize]
			self.data=np.fromfile(self.fhnd, code, self.datcount)


class qtree(dict):
	"""
		A stripped down tree representation.
	"""
	def __init__(self, fhnd, offset):
		self.fhnd=fhnd
		self.hdrOffset=offset

	def parse(self):
		qn=qnode(self.fhnd, self.hdrOffset)
		
		if qn.childoffset:
			s=qnode(self.fhnd, qn.childoffset)
			self[s.nodename]=s
	
			try:
				while s.siblingoffset:
					s=qnode(self.fhnd, s.siblingoffset)
					self[s.nodename]=s
			except AttributeError:
				pass

			for k,v in self.iteritems():
				if v.childoffset:
					t=qtree(self.fhnd, v.childoffset)
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

		dt=qt["Sampling"].data[0]
		scale=qt["Scaling"].data[0]
		dat=qt["Segments"]["Channels"].data/scale

		d1=dat[1:]
		d0=dat[:-1]

		return (((-1.0 * d1/self.Rfb) - (self.Cfb * (d1 - d0)/dt)) * iscale)

	def Current(self, iscale=1e12):
		self._parseQDFTree()

		qt=self.qdftree
		
		scale=qt["Scaling"].data[0]
		return (qt["Segments"]["Channels"].data/scale) * iscale


