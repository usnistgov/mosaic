import numpy as np

def heaviside(x):
	out=np.array(x)

	out[out==0]=0.5
	out[out<0]=0
	out[out>0]=1

	return out
	
def stepResponseFunc(t, tau, mu1, mu2, a, b):
	try:
		t1=(np.exp((mu1-t)/tau)-1)*heaviside(t-mu1)
		t2=(1-np.exp((mu2-t)/tau))*heaviside(t-mu2)

		# Either t1, t2 or both could contain NaN due to fixed precision arithmetic errors.
		# In this case, we can set those values to zero.
		t1[np.isnan(t1)]=0
		t2[np.isnan(t2)]=0

		return a*( t1+t2 ) + b
	except:
		raise

def multiStateFunc(t, tau, mu, a, b, n):
	try:
		func=b
		for i in range(n):
			t1=(1-np.exp((mu[i]-t)/tau))

			# For long events, t1 could contain NaN due to fixed precision arithmetic errors.
			# In this case, we can set those values to zero.
			t1[np.isnan(t1)]=0
			
			func += a[i]*heaviside(t-mu[i])*t1

		return func
	except:
		raise