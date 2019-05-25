# -*- coding: utf-8 -*-
"""
	Load QDF files based on the QUB specification (http://www.qub.buffalo.edu/qubdoc/files/qdf.html). The QUBTree
	is returned as a Python dict.

	:Created:	9/21/2016
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		5/24/19		AB 	Port to Python 3.7
		9/25/16 	AB 	Code cleanup and bug fixes.
		9/22/16 	AB 	Fixed a QUBTree parsing bug and added data integrity checks.
		9/22/16		AB 	Update scaling when the time-series is stored as current.
		9/22/16 	AB 	Cleanup variable names and header unpacking.
		9/21/16		AB	Initial version	
"""
import struct
import numpy as np

from mosaic.utilities.util import str_

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

		self.dataType=None
		self.dataSize=None
		self.dataCount=None
		self.dataPos=None
		self.childOffset=None
		self.siblingOffset=None
		self.nameLen=None
		self.data=None

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

			try:
				code=qubDataTypes[self.dataType<<self.dataSize]
			except KeyError:
				QDFError("The specified data type ({0}) and size ({1}) are incompatible.".format(self.dataType, self.dataSize))
			
			self.data=np.fromfile(self.fhnd, code, self.dataCount)

class qdict(dict):
	def __getitem__(self, key):
		k=str_(key)
		node=dict.__getitem__(self, k)
		
		if isinstance(node, qnode):
			if len(node.data)==1:
				return node.data[0]
			else:
				return node.data

		return node

	def __setitem__(self, key, val):
		k=str_(key)

		dict.__setitem__(self, k, val)

	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).items():
			self[str_(k)] = v

class qtree(dict):
	"""
		A stripped down tree representation.
	"""
	def __init__(self, fhnd, offset):
		self.fhnd=fhnd
		self.hdrOffset=offset

	def __getitem__(self, key):
		k=str_(key)
		
		return dict.__getitem__(self, k)

	def __setitem__(self, key, val):
		k=str_(key)

		dict.__setitem__(self, k, val)

	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).items():
			self[str_(k)] = v

	def parse(self):
		qn=qnode(self.fhnd, self.hdrOffset)
		
		childDict=qdict()
		if qn.childOffset:
			s=qnode(self.fhnd, qn.childOffset)
			childDict[s.nodeName]=s
	
			try:
				while s.siblingOffset:
					s=qnode(self.fhnd, s.siblingOffset)
					if s.nodeName in list(childDict.keys()):
						raise QDFError("The node name {0} already exists.".format(s.nodeName))
					else:
						childDict[s.nodeName]=s
			except AttributeError:
				pass

			for k,v in childDict.items():
				if v.childOffset:
					t=qtree(self.fhnd, v.childOffset)
					t.parse()
					childDict[k]=t

		self[qn.nodeName]=childDict

class QDFError(Exception):
	pass

class QDF(object):
	def __init__(self, filename, Rfb, Cfb):
		self.filename=filename
		self.Rfb=Rfb
		self.Cfb=Cfb

		self._parseQDFTree()

	def _parseQDFTree(self):
		fhnd=open(self.filename, 'r+b')
		self._checkMagic(fhnd)
		self.qdftree=qtree(fhnd, 12)
		self.qdftree.parse()

		nchans=self.qdftree["DataFile"]["ADChannelCount"]
		if nchans > 1:
			raise QDFError("Multiple I/O channels ({0}) are not supported.".format(nchans))


	def _checkMagic(self, fhnd):
		magic=fhnd.read(12)
		if str(magic, "utf-8") != "QUB_(;-)_QFS":
			raise QDFError("Incorrect magic string found: {0}".format(magic))


	def VoltageToCurrent(self, iscale=1e12):
		"""
			Convert voltage to current in pA (default iscale=1e12)
		"""
		qt=self.qdftree

		dt=qt["DataFile"]["Sampling"]
		scale=qt["DataFile"]["Scaling"]
		data=qt["DataFile"]["Segments"]["Segment"]["Channels"]/scale

		return (((-1.0 * data[1:]/self.Rfb) - (self.Cfb * np.diff(data)/dt)) * iscale)

	def Current(self, iscale=1):
		"""
			Return current in pA (default, iscale=1)
		"""
		qt=self.qdftree
		
		scale=qt["DataFile"]["Scaling"]
		data=qt["DataFile"]["Segments"]["Segment"]["Channels"]
		
		return (data/scale) * iscale


if __name__ == '__main__':
	import pprint

	def kvprint(d, key):
		print("{0} = {1}".format(key, d[key]))

	q=QDF('data/SingleChan-0001.qdf', 9.1e9, 1.07e-12)

	print(q)

	d=q.VoltageToCurrent()

	df=q.qdftree["DataFile"]

	kvprint( df, "Segments" )
	kvprint( df["Segments"], "Segment" )
	kvprint( df, "ADChannelCount" )
	kvprint( df, "ADDataSize" )
	kvprint( df, "ADDataType" )
	kvprint( df, "Sampling" )
	kvprint( df, "Scaling" )
	kvprint( df["Segments"]["Segment"], "StartTime" )
	print()
	pp = pprint.PrettyPrinter(indent=2)
	pp.pprint(q.qdftree)