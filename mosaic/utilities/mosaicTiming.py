""" 
	A class that provides platform independent timing and function profiling utilities.

	:Created:	4/10/2016
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		4/10/16		AB	Initial version
"""
import time
import sys

__all__=["mosaicTiming"]

class mosaicTiming:
	"""
		Profile code by attaching an instance of this class to any function. All the methods in this class are valid for the function being profiled.
	"""
	def __init__(self, logger=None):
		"""
			Initialize timing functions
		"""
		self.TotalTime		= 0		# total time - sum of times for each func call
		self.Counter		= 0		# number of times the function was called
		self.LastTime		= 0		# current execution time of function
		self.MaxTime		= 0		# maximum execution time
		self.FunctionName	= ""	# function name being profiled

		# Setup platform-dependent timing function
		if sys.platform.startswith('win'):
			self.timingFunc=time.clock
		else:
			self.timingFunc=time.time
		
	def FunctionTiming(self, func):
		"""
			Pass the function to be profiled as an argument. Alternatively with python 2.4+, attach a decorator to the function being profiled
			For example:
					funcTimer=mosaicTiming.mosaicTiming()

					@funcTimer.FunctionTiming
					def someFunc():
							print 'doing something'

					# summarize the profiling results for someFunc
					funcTimer.PrintStatistics()

			:Parameters:
					- `func` :    function to be profiled
		"""
		def wrapper(*arg):
			t1 = self.time()
			res = func(*arg)
			t2 = self.time()
			
			self.FunctionName	=  func.func_name
			self.LastTime		=  (t2-t1)*1000.0
			self.TotalTime		+= self.LastTime
			self.Counter		+= 1
			if self.LastTime > self.MaxTime:
				self.MaxTime=self.LastTime
			return res
		return wrapper
	
	def time(self):
		"""
			Replace time.time() with a platform independent timing function
		"""
		return self.timingFunc()

	def Reset(self):
		"""
			Reset all profiling data collected for a function
		"""
		self.FunctionName	= ""
		self.LastTime		= 0
		self.TotalTime		= 0
		self.Counter		= 0
		self.MaxTime		= 0
		
	def PrintCurrentTime(self):
		"""
			Print timing results of the most recent function call
		"""
		print("Timing results for function \"%s\": Iterations = %d, Current = %0.3f ms" % (self.FunctionName, self.Counter, self.LastTime) )
		
	def PrintStatistics(self):
		"""
			Print average timing results of the function call
		"""
		try:
			print( "Timing results for function \"%s\":\n\tIterations = %d, Total = %0.3f ms, Maximum = %0.3f ms, Average = %0.3f ms" % (self.FunctionName, self.Counter, self.TotalTime, self.MaxTime, self.TotalTime/self.Counter) )
		except ZeroDivisionError:
			print( "ERROR: No timing data is available.")

if __name__ == '__main__':
	funcTimer=mosaicTiming()

	@funcTimer.FunctionTiming
	def someFunc():
		time.sleep(0.01)

	for i in range(10):
		someFunc()

	# summarize the profiling results for someFunc
	funcTimer.PrintStatistics()
