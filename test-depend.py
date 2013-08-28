import numpy
import scipy
import zmq
import matplotlib
import uncertainties
import lmfit


numpy.test(label='fast',verbose=0)
print '\n'.join(''.ljust(5))
scipy.test(label='fast',verbose=0)
print '\n'.join(''.ljust(5))

print 'Installed packages:\n'
for p in [numpy, scipy, zmq, matplotlib, uncertainties, lmfit]:
	print p.__name__, p.__version__, p.__path__[0]

