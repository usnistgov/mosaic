"""
	An inverse stationary wavelet transform from 
		https://groups.google.com/forum/#!topic/pywavelets/tLh9ObKJaoc
"""
import math
import numpy
import pywt

def iswt(coefficients, wavelet):
	"""
		M. G. Marino to complement pyWavelets' swt.
		Input parameters:

			coefficients
				approx and detail coefficients, arranged in level value 
				exactly as output from swt:
				e.g. [(cA1, cD1), (cA2, cD2), ..., (cAn, cDn)]

			wavelet
				Either the name of a wavelet or a Wavelet object

	"""
	output = coefficients[0][0].copy() # Avoid modification of input data

	#num_levels, equivalent to the decomposition level, n
	num_levels = len(coefficients)
	for j in range(num_levels,0,-1): 
			step_size = int(math.pow(2, j-1))
			last_index = step_size
			_, cD = coefficients[num_levels - j]
			for first in range(last_index): # 0 to last_index - 1

					# Getting the indices that we will transform 
					indices = numpy.arange(first, len(cD), step_size)

					# select the even indices
					even_indices = indices[0::2] 
					# select the odd indices
					odd_indices = indices[1::2]

					# perform the inverse dwt on the selected indices,
					# making sure to use periodic boundary conditions
					x1 = pywt.idwt(output[even_indices], cD[even_indices], wavelet, 'per') 
					x2 = pywt.idwt(output[odd_indices], cD[odd_indices], wavelet, 'per')

					# perform a circular shift right
					x2 = numpy.roll(x2, 1)

					# average and insert into the correct indices
					output[indices] = (x1 + x2)/2.  

	return output

def apply_threshold(output, scaler = 1., input=None, threshold_type=pywt.thresholding.hard):
	"""
			output
				approx and detail coefficients, arranged in level value 
				exactly as output from swt:
				e.g. [(cA1, cD1), (cA2, cD2), ..., (cAn, cDn)]
			scaler 
				float to allow runtime tuning of thresholding
			input
				vector with length len(output).  If not None, these values are used for thresholding
				if None, then the vector applies a calculation to estimate the proper thresholding
				given this waveform.
	"""
	for j in range(len(output)): 
			cA, cD = output[j]
			if input is None:
					dev = numpy.median(numpy.abs(cD - numpy.median(cD)))/0.6745
					thresh = math.sqrt(2*math.log(len(cD)))*dev*scaler
			else: thresh = scaler*input[j]
			cD = threshold_type(cD, thresh)
			output[j] = (cA, cD)

def measure_threshold(output, scaler = 1.):
	"""
		output
			approx and detail coefficients, arranged in level value 
			exactly as output from swt:
			e.g. [(cA1, cD1), (cA2, cD2), ..., (cAn, cDn)]
		scaler 
			float to allow runtime tuning of thresholding

		returns vector of length len(output) with treshold values

	"""
	measure = []
	for j in range(len(output)): 
			cA, cD = output[j]
			dev = numpy.median(numpy.abs(cD - numpy.median(cD)))/0.6745
			thresh = math.sqrt(2*math.log(len(cD)))*dev*scaler
			measure.append(thresh)
	return measure

if __name__ == '__main__':
	"""
		output = pywt.swt(vec, wl_trans, level=level)
		apply_threshold(output, 0.8, threshold_list)
		final = iswt(output, wl_trans)

		where threshold_list might be the return of measure_threshold, and wl_trans
		is either a string or a Wavelet. 
	"""
	pass
