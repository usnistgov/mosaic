"""
	Parallel processing module that wraps python Multiprocessing to 
	asycnhronously apply a processing function to a Queue of class
	objects.

	:Created:	9/28/2012
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		9/28/12		AB	Initial version
"""
from numpy import arange,sqrt, random, linalg
from multiprocessing import Pool

import os
import signal
import time

import copy_reg
import types


# Use the copy_reg module to set pickling and unpickling 
# rules for class member functions
def _pickle_method(method):
	func_name = method.im_func.__name__
	obj = method.im_self
	cls = method.im_class
	return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
	for cls in cls.mro():
		try:
			func = cls.__dict__[func_name]
		except KeyError:
			pass
		else:
			break
	
	return func.__get__(obj, cls)

copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
    

class pproc(object):
	"""
		Parallel processing class that wraps Multiprocessing to 
		asycnhronously apply a function to data.
	"""
	def __init__(self, funcname, objlist, nproc):
		self.res=[]
		self.pool = Pool(processes=nproc, initializer=self.init_worker)

		self.funcname = funcname

		# Pre-emptively make a local copy,
		# since we will be modifying the objects
		# in the list.
		self.objlist = list(objlist)
	
	def init_worker(self):
		""" 
			Workaround for a bug in Python that doesn't
			handle KeyboardInterrupt properly with 
			multiprocessing.Pool. Ignoring SIGINT 
			causes KeyboardInterrupt respond properly
		"""
		signal.signal(signal.SIGINT, signal.SIG_IGN)

	def AsyncApply(self):
		"""
			Run through a list of class objects and call a processing
			function asynchronously.
		"""
		for d in self.objlist:
			funchnd = getattr(d, self.funcname)
			self.res.append( self.pool.apply_async(funchnd, ()).get() )

		try:
			time.sleep(5)
		except KeyboardInterrupt:
			self.pool.terminate()
			self.pool.join()
		else:
			self.pool.close()
			self.pool.join()
