"""
	Fit functions used in processing algorithms.
	
	:Created:	10/30/2014
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT	
	:ChangeLog:
	.. line-block::
		12/09/15 	KB 	Added a wrapper for multiStateFunc
		6/24/15 	AB 	Relaxed stepResponseFunc to include different RC constants 
						for up and down states.
		12/31/14 	AB 	Changed multi-state function to include a separate tau for 
						each state following Balijepalli et al, ACS Nano 2014.
		11/19/14	AB	Initial version
"""
import numpy as np

def heaviside(x):
	out=np.array(x)

	out[out==0]=0.5
	out[out<0]=0
	out[out>0]=1

	return out
	
def stepResponseFunc(t, tau1, tau2, mu1, mu2, a, b):
	try:
		t1=(np.exp((mu1-t)/tau1)-1)*heaviside(t-mu1)
		t2=(1-np.exp((mu2-t)/tau2))*heaviside(t-mu2)

		# Either t1, t2 or both could contain NaN due to fixed precision arithmetic errors.
		# In this case, we can set those values to zero.
		t1[np.isnan(t1)]=0
		t2[np.isnan(t2)]=0

		return a*( t1+t2 ) + b
	except:
		raise

def curve_fit_wrapper(t, n, *args):
        tau, mu, a = list(args[0][:n]), list(args[0][n:2*n]), list(args[0][2*n:3*n])
        return multiStateFunc(t, tau, mu, a, args[0][-1], n)
        

def multiStateFunc(t, tau, mu, a, b, n):
	try:
		func=b
		for i in range(n):
			t1=(1-np.exp((mu[i]-t)/tau[i]))

			# For long events, t1 could contain NaN due to fixed precision arithmetic errors.
			# In this case, we can set those values to zero.
			t1[np.isnan(t1)]=0
			
			func += a[i]*heaviside(t-mu[i])*t1

		return func
	except:
		raise

def multiStateStepFunc(t, mu, a, b, n):
	try:
		func=b
		for i in range(n):			
			func += a[i]*heaviside(t-mu[i])

		return func
	except:
		raise
