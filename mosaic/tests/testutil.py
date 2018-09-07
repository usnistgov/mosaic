import csv
import string
import json
import numpy as np

from mosaic.utilities.util import eval_

param_t={
	"n" 				: int,
	"OpenChCurrent"		: float,
	"RCConstant"		: list,
	"eventDelay"		: list,
	"deltaStep"			: list,
	"FsKHz"				: int,
	"BkHz"				: int,
	"padding"			: int,
	"noisefArtHz"		: int
}


def readcsv(fname):
	r1=csv.reader(open(fname,'rU'), delimiter=',')

	p1=r1.next()
	p2=r1.next()

	Fs=1e6/(float(p2[0])-float(p1[0]))
		
	# Store the ionic currents for the first two points
	dat=[]
	dat=[float(p1[1]), float(p2[1])]
	dat.extend([ float(row[1]) for row in r1 ])

	return [Fs, dat]

def readparams(fname):
	r1=csv.reader(open(fname,'rU'), delimiter=',')

	dat=[]
	dat.extend([ row for row in r1 ])
	d1=[ p[0].split('=') for p in dat ]

	def _formatstr(s):
		if s.startswith('List'):
			return list(eval_(s.replace('List','')))
		else:
			return float(s)

	return dict([ ( p[0], _formatstr(p[1]) ) for p in d1])


def readDataRAW(datfile):
		return np.fromfile(datfile, dtype=np.float64)

def readParametersJSON(paramfile):
	prm=json.loads("".join((open(paramfile, 'r').readlines())))
	
	for k in prm.keys():
		v=eval_(prm[k])
		prm[k]=param_t[k](v)

	return prm