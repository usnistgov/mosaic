#test

import math
from struct import unpack
from numpy import * #arange,array,append, concatenate, fromfile, tofile, where, putmask, zeros, average, ravel, nonzero, ceil, mean, transpose
# from operator import itemgetter
from mosaic.qdfTrajIO import *
import numpy as npts
import mosaic.sigproc as sigproc

def catQDF(fileList, outputFile, dwell,ScreenLongOpens = None, ScreenLongBlocks = None, ScreenToggles = None, ScreenTogglesLITE = None):
###############################################################################
#	function Name:	catLDT_lite
#	Author: 		Ryan Dunnam, adapted from the "catLDT_lite()" function by Geoffrey Barrall
#	Description:	Concatenates a list of QDF files but only reads in one at a time
#					Reads headers, computes overall scale and number of points then
#					write out the final big file
#	Inputs:
#			fileList - a list of QDF files to be concatenated.	Created using
#						a command like: 		fileList = sorted(glob('*.ldt'))
#														or
#										fileList = glob(('1.ldt', 2.ldt', ...)
#
#			outputFile - the desired name of the concatenated file
##################################################################################
	#
	firstFile = 1

	# get scaling parms by reading all headers
	for filename in fileList:
		# open file
		fileobj = QDFDataFile(filename, 0)
		# create array of scales, datatypes, and starttimes
		if firstFile == 1:
			firstFile = 0
			scale_array = [fileobj.scale]
			datasize_array = [fileobj.datasize]
			starttime_array = [fileobj.starttime]
		else:
			scale_array = concatenate( (scale_array,[fileobj.scale]) )
			datasize_array = concatenate( (datasize_array,[fileobj.datasize]) )
			starttime_array = concatenate( (starttime_array,[fileobj.starttime]) )
		del fileobj
	
	# final scale for all data
	scale_min = min(scale_array)
	size_max = max(datasize_array)
	
	# setup to write oputput file
	print outputFile
	outFile = open(outputFile, mode = 'wb')
	outFile.write('QUB_(;-)_QFS')
	offset = write_node(outFile, 'DataFile',0,0,0,0,None)
	segoffset = write_node(outFile, 'Segments',0,0,offset,0,None)
	offset = write_node(outFile, 'Sampling',2,13,0,segoffset,(dwell,))
	offset = write_node(outFile, 'Scaling',2,13,0,offset,(float(scale_min),))
	offset = write_node(outFile,'ADChannelCount',2,9,0,offset,(1,))
	offset = write_node(outFile,'ADDataSize',2,9,0,offset,(size_max,))	
	offset = write_node(outFile,'ADDataType',2,9,0,offset,(size_max+5,))

	# write segment data to output file using scale_min
	firstFile = 1
	starttime = 0
	for filename in fileList:
		print filename	# debug

		# read QDF file
		fileobj = QDFDataFile(filename)
		
		# Screen out regions with voltage toggle
		if (ScreenToggles != None) and (len(fileobj.data) != 0):
			fileobj.data = dataScreenToggles(fileobj.data, ScreenToggles)

		if (ScreenTogglesLITE != None) and (len(fileobj.data) != 0):
			fileobj.data = dataScreenTogglesLITE(fileobj.data, dwell, ScreenTogglesLITE)
			
		# Screen out long runs of open channel current (e.g. you have a low event density)
		if (ScreenLongOpens != None) and (len(fileobj.data) != 0):
			fileobj.data = dataScreenLongOpens(fileobj.data, ScreenLongOpens)

		# Screen out long runs of blocked channel current (e.g. you have a lots of gating/blocks)
		if (ScreenLongBlocks != None) and (len(fileobj.data) != 0):
			fileobj.data = dataScreenLongBlocks(fileobj.data, ScreenLongBlocks)
		
		# Don't write empty data
		if len(fileobj.data) == 0:
			continue
			
		# make first segment the child of 'Segments' node and the rest siblings
		if firstFile:
			firstFile = 0
			siboffset = write_node(outFile, 'Segment',0,0,segoffset,0,None)
		else:
			siboffset = write_node(outFile, 'Segment',0,0,0,siboffset,None)
		offset = write_node(outFile,'StartTime',2,13,siboffset,0,(starttime,))
		offset = write_node(outFile,'Channels',2,fileobj.datatype,0,offset,fileobj.data*scale_min)
		starttime += dwell * (len(fileobj.data)-1)
		del fileobj
	
	#closing(outFile)
	outFile.close()


###############################################################################
#	function Name: dataScreenLongOpens
#	Author: Geoffrey Barrall, modified for .qdf files by Ryan Dunnam (2009-02-25)
#	Description: delete long stetches of data that fall within given range
#	Inputs: data (float64 numpy array), screen parms, scale
#	Returns: data (float64 numpy array)
##################################################################################

def dataScreenLongOpens(data, screenParms, Scale = 1):

	n = screenParms[0]				# number of points of continuos open channel current to eliminate
	ymin = screenParms[1] 	# lower amplitude limit for throwing out open channel current
	ymax = screenParms[2] 	# upper limit

	npts = len(data)				# length of data
	nsteps = int(npts/n)			# number of steps we will make through the data
	nres = npts % n 				# bit of data left after nsteps of n

	bigNum = 2*max([abs(data.min()),abs(data.max())])	# a number bigger than any in the dataset

	# step through data
	for i in arange(nsteps):
		# if all points fall between ymin and ymax we will set to bigNum
		if (data[i*n:(i+1L)*n].min() > ymin) and (data[i*n:(i+1L)*n].max() < ymax):
			data[i*n:(i+1L)*n] = zeros(n,dtype = 'float64') + bigNum

	# handle remainder after nsteps of n
	if nres != 0:
		if (data[nsteps*n:nsteps*n + nres].min() > ymin) and (data[nsteps*n:nsteps*n + nres].max() < ymax):
			data[nsteps*n:nsteps*n + nres] = zeros(nres,dtype = int) + bigNum

	# return data array as short into with all bigNum vals screened out
	return array(data[ravel(nonzero(where(data != bigNum, 1, 0)))], dtype = 'float64')
#end routine def

###############################################################################
#	function Name: dataScreenLongBlocks
#	Author: Geoffrey Barrall, modified for .qdf files by Ryan Dunnam (2009-02-25)
#	Description: completely delete long blocks
#	Inputs: data (float64 numpy array), screen parms, scale
#	Returns: data (float64 numpy array)
##################################################################################

def dataScreenLongBlocks(data, screenParms,Scale = 1):

	n = screenParms[0]				# number of points of continuous block channel current to check
	ymin = screenParms[1] 	# lower amplitude limit for throwing out open channel current
	ymax = screenParms[2] 	# upper limit
	nopen = screenParms[3]			# number of points used when finding open state
	openI = screenParms[4]	# The open current
	sigma = screenParms[5]	# noise level in pArms

	npts = len(data)				# length of data
	nsteps = int(npts/n)			# number of steps we will make through the data
	nres = npts % n 				# bit of data left after nsteps of n

	bigNum = 2*max([abs(data.min()),abs(data.max())])	# a number bigger than any in the dataset

	lenData = len(data)

	# find indices for known open channel data
	indexOpen = ravel(nonzero(where( sigproc.smooth(abs(data - openI),nopen,window = 'flat') < sigma, 1, 0)))
	# step through data
	for i in arange(nsteps):
		# if all points fall between ymin and ymax we will set to bigNum
		if (data[i*n:(i+1L)*n].min() > ymin) and (data[i*n:(i+1L)*n].max() < ymax):
#			print "Block = ", i*n, (i+1L)*n
			diffIndex = i*n - indexOpen
			# find first open state to the left
			leftChk = diffIndex[ravel(nonzero(where(diffIndex > 0, 1, 0)))]
			if len(leftChk) !=0:
				left = max([i*n - leftChk.min(),0])
			else:
				left = 0
			# find first open state to the right
			rightChk = diffIndex[ravel(nonzero(where(diffIndex < 0, 1, 0)))]
			if len(rightChk) != 0:
				right = min([i*n - rightChk.max(),lenData])
			else:
				right = lenData
#			print left, i*n, right
			data[left:right] = zeros(right - left,dtype = 'float64') + bigNum

	# handle remainder after nsteps of n
	if nres != 0:
		if (data[nsteps*n:nsteps*n + nres].min() > ymin) and (data[nsteps*n:nsteps*n + nres].max() < ymax):
			diffIndex = nsteps*n - indexOpen
			# find first open state to the left
			leftChk = diffIndex[ravel(nonzero(where(diffIndex > 0, 1, 0)))]
			if len(leftChk) !=0:
				left = max([nsteps*n - leftChk.min(),0])
			else:
				left = 0
			# find first open state to the right
			rightChk = diffIndex[ravel(nonzero(where(diffIndex < 0, 1, 0)))]
			if len(rightChk) != 0:
				right = min([nsteps*n - rightChk.max(),lenData])
			else:
				right = lenData
#			print left, nsteps*n, right
			data[left:right] = zeros(right - left,dtype = 'float64') + bigNum

	# eliminated blocks and found no regions of open channel current
	if data.min == bigNum:
		return array([],dtype = 'float64')

	# eliminated blocks and found regions of open channel current
	else:
		return array(data[ravel(nonzero(where(data != bigNum, 1, 0)))], dtype = 'float64')
#end routine def


###############################################################################
#	function Name: dataScreenToggles
#	Author: Geoffrey Barrall
#	Description: delete voltage toggle regions and surrounding undesirable data
#	Inputs: data (float64 numpy array), screen parms, scale
#	Returns: data (float64 numpy array)
##################################################################################

def dataScreenToggles(data, screenParms, Scale = 1):

	n = screenParms[0]						# number of points used when finding open state
	ampThresh = abs(screenParms[1])	# Larger amplitudes are part of a toggle
	openI = screenParms[2]			# The open current
	sigma = screenParms[3]			# noise level in pArms
	if len(screenParms) > 3:
		nRecover = -1*screenParms[4]
	else:
		nRecover = 0

	lenData = len(data)
	bigNum = 2*max([abs(data.min()),abs(data.max())]) # a number bigger than any in the dataset

	# find indices for ends of voltage toggles.  Returns just the endpoint of the toggles.
	toggleEnds = ravel(nonzero(where(concatenate([where(abs(data) > ampThresh, 1, 0)[1:],zeros(1, dtype = 'float64')]) - \
								where(abs(data) > ampThresh, 1, 0) == -1, 1, 0)))

	# find indices for known open channel data
	indexOpen = ravel(nonzero(where( sigproc.smooth(abs(data - openI),n,window = 'flat') < sigma, 1, 0)))

	# Eliminate toggle regions
	if (len(toggleEnds) != 0) and (len(indexOpen) != 0):
		for i in toggleEnds:
			diffIndex = i - indexOpen
			# find first open state to the left
			leftChk = diffIndex[ravel(nonzero(where(diffIndex > 0, 1, 0)))]
			if len(leftChk) !=0:
				left = max([i - leftChk.min(),0])
			else:
				left = 0
			# find first open state to the right - option to push out an extra nRecover points
			rightChk = diffIndex[ravel(nonzero(where(diffIndex < nRecover, 1, 0)))]
			if len(rightChk) != 0:
				right = min([i - rightChk.max(),lenData])
			else:
				right = lenData
			#print left, i, right
			data[left:right] = zeros(right - left,dtype = 'float64') + bigNum

	# eliminated toggles and found some regions of open channel current
	if (len(toggleEnds) != 0) and (len(indexOpen) != 0):
		return array(data[ravel(nonzero(where(data != bigNum, 1, 0)))], dtype = 'float64')
	# found no regions of open channel current.  Return empty array :(
	elif (len(indexOpen) == 0):
		return array([],dtype = 'float64')
	# found no voltage toggles but there was open channel current.	It's all good.
	elif (len(toggleEnds) == 0):
		return array(data, dtype = 'float64')
	# just in case, return all the data
	else:
		return array(data, dtype = 'float64')

#end routine def

###############################################################################
#	function Name: dataScreenTogglesLITE
#	Original Author: EBS (Ryan Dunnam, adapted from Geoff Barrall's dataScreenToggles())
#  	Modifed: 5/12/15		JHF (NIST)
#
#
#	Description: delete voltage toggle regions and surrounding undesirable data
#	Inputs: data (float64 numpy array), dwell time, screen parms, scale
#	Returns: data (float64 numpy array)
##################################################################################

def dataScreenTogglesLITE(data, dwell, screenParms, Scale = 1):

	ampThresh = abs(screenParms[0])	# Larger amplitudes are part of a toggle
	nCut = screenParms[1]

	lenData = len(data)
	bigNum = 2*max([abs(data.min()),abs(data.max())]) # a number bigger than any in the dataset

	# find indices for ends of voltage toggles.  Returns just the endpoint of the toggles.
	toggleEnds = ravel(nonzero(where(concatenate([where(abs(data) > ampThresh, 1, 0)[1:],zeros(1, dtype = 'float64')]) - \
								where(abs(data) > ampThresh, 1, 0) == -1, 1, 0)))

	# Eliminate toggle regions
	if (len(toggleEnds) != 0):
		for i in toggleEnds:
			if i > nCut:
				left = i - nCut
			else:
				left = 0
			if i + nCut < len(data):
				right = i + nCut
			else:
				right = len(data)
			data[left:right] = zeros(right-left,dtype = 'float64') + bigNum

	# eliminated toggles and found some regions of open channel current
	if (len(toggleEnds) != 0):
		return array(data[ravel(nonzero(where(data != bigNum, 1, 0)))], dtype = 'float64')
	# just in case, return all the data
	else:
		return array(data, dtype = 'float64')