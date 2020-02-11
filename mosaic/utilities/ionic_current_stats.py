"""
	:Created:	10/30/2014
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT	
	:ChangeLog:
	.. line-block::
		5/24/19 		AB 		Python 3.7 port
		7/29/16         KB      Added weights to histogram fitting
		15/12/15        KB      Added error checking and limits to baseline calculations
		10/30/14	AB	Initial version
"""
import numpy as np 
from scipy.optimize import curve_fit


__all__=["OpenCurrentDist"]

def _fitfunc(x, a, s, m):
	return a*np.exp(-(x-m)**2/(2. * s**2))

def OpenCurrentDist(dat, limit, minBaseline=-1, maxBaseline=-1):
	"""
		Calculate the mean and standard deviation of a time-series.
		
		:Args:
			- `dat` 	: time-series data
			- `limit`	: limit the calculation to the top 50% (+0.5) of the range, bottom 50% (-0.5) or the entire range (0). Any other value of `limit` will cause it to be reset to 0 (i.e. full range).
	"""
	datsign = np.sign( np.mean(dat) )
	uDat = datsign*dat
	dMin, dMax, dMean, dStd = np.floor( np.min(uDat) ), np.ceil( np.max(uDat) ), np.round( np.mean(uDat) ), np.std(uDat)

	try:
		hLimit={0.5 : [dMean, dMax], -0.5 : [dMin, dMean], 0 : [dMin, dMax] }[limit]
	except KeyError:
		hLimit=[dMin, dMax]

	if minBaseline == -1.0 or maxBaseline == -1.0:
		y,x=np.histogram(uDat, range=hLimit, bins=100)
			
	else:
		hLimit = [minBaseline, maxBaseline]
		y,x=np.histogram(uDat, range=hLimit, bins=100)
	try:
		sigma = 1/np.sqrt(y+1e-10)
		popt, pcov = curve_fit(_fitfunc, x[:-1], y, p0=[np.max(y), dStd, np.mean(x)],sigma=sigma)
		perr=np.sqrt(np.diag(pcov))
	except:
		return [0,0]
	if np.any(perr/popt > 0.5) or ((minBaseline > -1 and maxBaseline > -1) and (popt[2] < minBaseline or popt[2] > maxBaseline)): #0.5 is arbitrary for the moment, for testing. Could be added as a parameter or hard-coded pending testing. 
				return [0,0]
		
	return [popt[2], np.abs(popt[1])]


if __name__ == '__main__':
	import mosaic.trajio.qdfTrajIO as qdf
	# import pylab
	from os.path import expanduser

	d=qdf.qdfTrajIO(dirname='data/',filter='*qdf', Rfb=9.1E+9, Cfb=1.07E-12)

	print((OpenCurrentDist(d.popdata(500000), 0.5)))	
	
	# pylab.plot( y, x[:-1] )
	# pylab.show()
