# -*- coding: utf-8 -*-
"""
	An object that allows arbitrary formatting of log text.

	:Created:	09/12/2015
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT	
	:ChangeLog:
	.. line-block::
		06/14/16 	AB 	Added a new Python property class mimic to add log property set, get and del. 
		06/13/16 	AB 	Remove mosaicLogFormat class
		09/12/15	AB	Initial version
"""
import sys
import mosaic.utilities.mosaicLogging as mlog
import mosaic

__all__=["mosaic_property", "_d", "_dprop"]

def _d(msg, *args):
	"""
		Format a debug log message. This function will automatically append calling function name and file/line number.

		:Parameters:

			- `msg`  : Log message formatted using the Python `formatter class <https://docs.python.org/2/library/string.html#custom-string-formatting>`_.
			- `args` : Message arguments.

		:Usage:

			Log an integer or a float variable.

			.. code-block:: python

				_d("Var x has value {0}", x)

				_d("Var y is a float with value {0:0.2f} to 2 decimal places.", y)
	"""
	frame1=sys._getframe(1)
	frame2=sys._getframe(2)
	n=len(args)

	m1="{0} ({{{1}}}:{{{2}}}:{{{3}}}:{{{4}}})".format(msg,n, n+1, n+2, n+3)
	a1=list(args)+[frame1.f_code.co_name, frame2.f_code.co_name, frame2.f_code.co_filename, frame2.f_lineno]
	
	return m1.format(*a1)

def _dprop(msg, *args):
	"""
		Format a debug log message for a class property. This function will automatically append calling function name and file/line number.

		:Parameters:

			- `msg`  : Log message formatted using the Python `formatter class <https://docs.python.org/2/library/string.html#custom-string-formatting>`_.
			- `args` : Message arguments.

		:Usage:

			Log a property that returns an integer or a float.

			.. code-block:: python

				_dprop("Var x has value {0}", x)

				_dprop("Var y is a float with value {0:0.2f} to 2 decimal places.", y)
	"""
	# frame1=sys._getframe(1)
	frame2=sys._getframe(2)
	n=len(args)

	m1="{0} ({{{1}}}:{{{2}}}:{{{3}}}:{{{4}}})".format(msg,n, n+1, n+2, n+3)
	a1=list(args)+["<property>", frame2.f_code.co_name, frame2.f_code.co_filename, frame2.f_lineno]
	
	return m1.format(*a1)

class mosaic_property(object):
	"""
		Emulate Python property. Add support to the getter and setter methods to automatically log properties in debug mode.
		The new class can be used exactly as the built-in Python property class, for example as a decorator

			.. code-block:: python

				class foo:
					def __init__(self):
						self.x=100

					@mosaic_property
					def x(self):
						return self.x

					@x.setter
					def x(self, val):
						self.x=val

		Adapted from: `<https://docs.python.org/2/howto/descriptor.html#properties>`_.
	"""
	def __init__(self, fget=None, fset=None, fdel=None, doc=None):
		self.fget = fget
		self.fset = fset
		self.fdel = fdel
		if doc is None and fget is not None:
			doc = fget.__doc__
		self.__doc__ = doc

	def __get__(self, obj, objtype=None):
		if obj is None:
			return self
		if self.fget is None:
			raise AttributeError("unreadable attribute")

		rval=self.fget(obj)
		if mosaic.LogProperties:
			logger=mlog.mosaicLogging().getLogger(name=self.fget.__name__)
			logger.debug(_dprop( "GET {0}={1}", self.fget.__name__, rval ))
		return rval

	def __set__(self, obj, value):
		if self.fset is None:
			raise AttributeError("can't set attribute")

		if mosaic.LogProperties:
			logger=mlog.mosaicLogging().getLogger(name=self.fset.__name__)
			logger.debug(_dprop( "SET {0}={1}", self.fset.__name__, value ))
		self.fset(obj, value)

	def __delete__(self, obj):
		if self.fdel is None:
			raise AttributeError("can't delete attribute")

		if mosaic.LogProperties:
			logger=mlog.mosaicLogging().getLogger(name=self.fdel.__name__)
			logger.debug(_dprop( "DEL {0}", self.fdel.__name__ ))

		self.fdel(obj)

	def getter(self, fget):
		return type(self)(fget, self.fset, self.fdel, self.__doc__)

	def setter(self, fset):
		return type(self)(self.fget, fset, self.fdel, self.__doc__)

	def deleter(self, fdel):
		return type(self)(self.fget, self.fset, fdel, self.__doc__)


if __name__ == '__main__':
	class foo:
		def __init__(self):
			self.x=100

		@mosaic_property
		def x(self):
			return self.x

		@x.setter
		def x(self, val):
			self.x=val


	bar=foo()

	print((bar.x))
	bar.x=200
	print((bar.x))
