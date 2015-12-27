"""
	A collection of analysis functions
"""
import math

import numpy as np
from scipy.optimize import curve_fit


from mosaic.utilities.fit_funcs import singleExponential

def CaptureRate(startTimes):
	"""
		Estimate the capture rate from a list of event start times in milliseconds.
	"""
	arrtimes=np.diff(startTimes)/1000.		
	counts, bins = np.histogram(arrtimes, bins=100, density=True)
	
	try:
		popt, pcov = curve_fit(singleExponential, bins[:len(counts)], counts, p0=[1, np.mean(arrtimes)])
		perr=np.sqrt(np.diag(pcov))
	except:
		return [0,0]

	return [ 1/popt[1], 1/(popt[1]*math.sqrt(len(startTimes))) ]