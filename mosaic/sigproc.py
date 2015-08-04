# Signal Processing functions

import numpy
from scipy.signal import lfilter, iirfilter
from numpy import pi, array, zeros, concatenate

def smooth(x,window_len=10,window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='same')
    return y[window_len-1:-window_len+1]


def lpfQuB(data, fc, fs, order = 4, ftype = "bessel"):
# lpfQuB(data,fc,fs,order = 5, ftype = "bessel")
# Provides low pass filtering to closely match that from QuB
# Still shows a little more ripple than the QuB filter,
# but the similarity is very close overall.
# Input:
#	data - flotaing point data
#	fc - critical frequency in Hz
#	fs - sampling frequency in Hz (also 1/dwell)
#	order - filter order
#	ftype - type of filter, e.g. bessel or butter.
# Output:
#	filtered_data - low pass filtered data.  Numpy float array

	# Determine beginning and end padding to make result more QuB like
	paddingStart = zeros(10*order, dtype = float) + data[0]
	paddingEnd = zeros(2*(order + 1), dtype = float) + data[-1:]

	# Compute filter parameters
	(b,a) = iirfilter(order,pi*fc/fs,analog = 0, ftype = ftype, btype = "lowpass", output = 'ba')

	# Filter data
	data_out = (lfilter(b, a, concatenate((paddingStart,data, paddingEnd)), axis = -1, zi = None))[len(paddingStart)+len(paddingEnd):]
        print "Data Out Max = ", max(data_out)
	# Return filtered data
	return data_out


