"""
	A collection of utility functions
"""
import sys
import numpy

class WindowSizeError:
	pass

def avg(dat):
	"""
		Calculate the average of a list of reals
	"""
	try:
		return sum(dat)/len(dat)
	except ZeroDivisionError:
		return 0.0

def sd(dat):
	"""
		Wrapper for numpy std
	"""
	return numpy.std(dat)

def filter(dat, windowSz):
	"""
		Filter the data using a convolution. Returns an
		array of size len(dat)-windowSz+1 if dat is longer than 
		windowSz. If len(dat) < windowSz, raise WindowSizeError
	"""
	if len(dat)<windowSz: raise WindowSizeError("Data length ({0}) must be longer than specified window size ({1}).".format(len(dat),windowSz))

	# define the weights for the convolution
	weights=numpy.repeat(1.0,windowSz)/windowSz

	return list(numpy.convolve(dat,weights,'valid'))

def partition(dat, size):
	"""
		Partition a list into sub-lists, each of length size. If the number of elements
		in dat does not partition evenly, the last sub-list will have fewer elements.
	"""
	return (lambda dat, size:  map(lambda i: dat[i:i+size],  xrange(0, len(dat), size)))(dat,size)


def decimate(dat, size):
	"""
		Decimate dat for a specified window size.
	"""
	return [ avg(decim) for decim in partition(dat,size) ]

def commonest(dat):
	"""
		Return the most common element in a list.
	"""
	return max( set(dat), key=dat.count )

def selectS(dat, nSigma, mu, sd):
	"""
		Select and return data from a list that lie within
		nSigma * SD of the mean.
	"""
	#sigma=min( numpy.std(dat), sd )

	return [ d for d in dat if d>(mu-sd) and d<(mu+sd) ]

def flat2(dat):
	"""
		Flatten a 2D array to a list
	"""
	return reduce(lambda x,y: x+y,dat)