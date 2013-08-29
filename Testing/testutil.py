import csv
import string

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

	return dict([ ( p[0], float(p[1]) ) for p in d1])