"""
	A wrapper to define a fixed length numpy FIFO. This buffer is designed
	to always hold a specified number of elements with the following properties:
		1. Elements are always added to the end of the list.
		2. If the buffer overflows, elements are deleted from the front of 
		   the list without any warning.
		3. The entire FIFO data can be accessed using the 'data' property.

	Author: 	Arvind Balijepalli
	Created:	7/26/2012

	ChangeLog:
		7/26/12		AB	Initial version
"""
import numpy as np

class npfifo:
	def __init__(self, fifolen, dtype=np.float64):
		"""
			Initialize a fixed length numpy array. 

			Args:
				fifolen		number of elements in the FIFO
				dtype		(optional) element data types. default: float64
			Returns:
				None
			Errors:
				None
		"""
		# allocate the array for the FIFO
		self.npFIFO=np.array([], dtype=dtype)

		# specified length
		self.lenFIFO=fifolen

		# FIFO index for efficient deletes
		self.idxFIFO=0

	#################################################################
	# Public functions
	#################################################################
	def push(self, dat):
		"""
			Append a numpy array to the end of the FIFO. If this operation causes 
			an overflow, then elements are deleted from the front
			Args:
				dat 	numpy array to Append
			Returns:
				None
			Errors:
				None
		"""
		# add the new data
		self.npFIFO=np.hstack((self.npFIFO, dat))
		
		# set the current index value 
		if len(self.npFIFO)>=self.lenFIFO:
			self.idxFIFO=len(self.npFIFO)-self.lenFIFO
			# check if data should be physically deleted
			self.__trimfifo()

	#################################################################
	# Properties
	#################################################################
	@property 
	def data(self):
		"""
			Return FIFO data
		"""
		if len(self.npFIFO) < self.lenFIFO:
			return self.npFIFO[self.idxFIFO:]
		else:
			return self.npFIFO[self.idxFIFO:self.idxFIFO+self.lenFIFO]

	def __len__(self):
		return self.lenFIFO

	#################################################################
	# Private functions
	#################################################################
	def __trimfifo(self):
		"""
			Efficient delete: trim the FIFO when the number of 
			popped entries exceeds 3 times the defined FIFO length.
		"""
		if self.idxFIFO > 3*self.lenFIFO:
			self.npFIFO=np.delete(self.npFIFO, np.s_[:self.idxFIFO:], axis=0)
			# reset the index
			self.idxFIFO=0

