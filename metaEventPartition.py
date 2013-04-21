from abc import ABCMeta, abstractmethod

class metaEventPartition(object):
	__metaclass__=ABCMeta

	def __init__(self, icurr, Fs, **kwargs):
		pass

	@abstractmethod
	def PartitionEvents(self):
		"""
			This is the equivalent of a pure virtual function in C++. Specific event processing
			algorithms must implement this method.
		"""
		pass