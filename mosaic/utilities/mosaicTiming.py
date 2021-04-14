""" 
	A class that provides platform independent timing and function profiling utilities.

	:Created:	4/10/2016
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		4/14/21		AB 	Windows fixes
		6/17/16 	AB 	Only profile functions in DeveloperMode. Log timing output.
		4/10/16		AB	Initial version
"""
import time
import sys
import mosaic
import mosaic.utilities.mosaicLogging as mlog
from mosaic.utilities.mosaicLogFormat import _d

__all__=["mosaicTiming"]

class timingData(dict):
	"""
		Store timing information for each function being profiled
	"""
	def __init__(self, funcname):
		self["funcname"]=funcname
		self["last"]=0
		self["total"]=0
		self["maxtime"]=0
		self["counter"]=0

	def _currentTime(self):
		return [
			"Timing for \"{0}\": iterations={1}, last={2:0.3f} ms",
			self["funcname"], 
			self["counter"], 
			self["last"]
		] 

	def _timingStatistics(self):
		return [
			"Summary timing for \"{0}\": iterations={1}, total={2:0.3f} ms, maximum={3:0.3f} ms, average={4:0.3f} ms",
			self["funcname"], 
			self["counter"], 
			self["total"], 
			self["maxtime"], 
			self["total"]/float(self["counter"])
		]

class mosaicTiming:
	"""
		Profile code by attaching an instance of this class to any function. All the methods in this class are valid for the function being profiled.
	"""
	def __init__(self):
		"""
			Initialize timing functions
		"""
		self.timingDataDict={}

		if mosaic.DeveloperMode and mosaic.CodeProfiling !='none':
			self.TimingEnabled=True
			if mosaic.CodeProfiling=='summary':
				self.TimingSummary=True
			else:
				self.TimingSummary=False

			self.logger=mlog.mosaicLogging().getLogger(__name__)
		else:
			self.TimingEnabled=False

		
		self.timingFunc=time.time
		
	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		self.PrintStatistics()

	def FunctionTiming(self, func):
		"""
			Pass the function to be profiled as an argument. Alternatively with python 2.4+, attach a decorator to the function being profiled.

			:Parameters:
					- `func` :    function to be profiled

			:Usage:
			
				.. code-block:: python
				
					funcTimer=mosaicTiming.mosaicTiming()

					@funcTimer.FunctionTiming
					def someFunc():
							print 'doing something'

					# summarize the profiling results for someFunc
					funcTimer.PrintStatistics()
		"""
		def timing_wrapper(*args, **kwargs):
			if self.TimingEnabled:
				t1 = self.time()
				res = func(*args, **kwargs)
				t2 = self.time()
				
				try:
					funcTimingObj=self.timingDataDict[func.__name__]
				except KeyError:
					funcname=func.__name__
					funcTimingObj=timingData(funcname)
					self.timingDataDict[funcname]=funcTimingObj

				self._updateTiming(funcTimingObj, t1, t2)
				
				if not self.TimingSummary:
					logger=mlog.mosaicLogging().getLogger(func.__name__)
					logger.debug(_d(
								"Timing: iterations={0}, total={1:0.3f} ms, last={2:0.3f} ms, maximum={3:0.3f} ms",
								funcTimingObj["counter"],
								funcTimingObj["total"],
								funcTimingObj["last"],
								funcTimingObj["maxtime"]
							))
			else:
				res = func(*args, **kwargs)

			return res
		return timing_wrapper
	
	def time(self):
		"""
			A platform independent timing function.
		"""
		return self.timingFunc()

	def Reset(self, funcname=None):
		"""
			Reset all profiling data collected for a specified function or all stored functions.
		"""
		if funcname:
			del self.timingDataDict[funcname]
		else:
			self.timingDataDict={}
		
	def PrintCurrentTime(self):
		"""
			Print timing results of the most recent function call
		"""
		if self.TimingEnabled:
			for k, v in list(self.timingDataDict.items()):
				self.logger.debug( _d(*v._currentTime()) )
		
	def PrintStatistics(self):
		"""
			Print average timing results of the function call
		"""
		if self.TimingEnabled:
			for k, v in list(self.timingDataDict.items()):
				try:
					self.logger.debug( _d(*v._timingStatistics()) )
				except ZeroDivisionError:
					self.logger.error( "ERROR: No timing data is available.")

	def _updateTiming(self, funcTimingObj, t1, t2):
		last=(t2-t1)*1000.0

		funcTimingObj["last"]		=  last
		funcTimingObj["total"]		+= last
		funcTimingObj["counter"]	+= 1
		if last > funcTimingObj["maxtime"]:	funcTimingObj["maxtime"]=last


if __name__ == '__main__':
	with mosaicTiming() as funcTimer:
		@funcTimer.FunctionTiming
		def someFunc():
			time.sleep(0.01)

		for i in range(10):
			someFunc()

