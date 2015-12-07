# -*- coding: utf-8 -*-
"""
	A logging file object that allows arbitrary formatting of log text.

	:Created:	09/12/2015
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT	
	:ChangeLog:
	.. line-block::
		09/12/15	AB	Initial version
"""

class mosaicLog(dict):
	def __init__(self):
		self.gLogCounter=self._logCounter()

	def __setitem__(self, key, val):
		if key=="log":
			dict.__setitem__(self, key+str(self.gLogCounter.next()), val )
		else:
			dict.__setitem__(self, key, val )

	def __getitem__(self, key):
		return dict.__getitem__(self, key)

	def __str__(self):
		try:
			logstr='\t'+self["hdr"]+'\n'
		except KeyError:
			logstr=""

		keys=sorted(self.keys())
		for k in keys:
			if k.startswith("log"):
				logstr+='\t\t'+str(self[k])+"\n"

		logstr+="\n"
		return logstr

	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v

	def _logCounter(self):
		logCounter=0

		while (True):
			yield logCounter
			logCounter+=1

	def addLogHeader(self, header):
		"""
			Add a section header to the output log.

			:Args:
				- `header` : 	header text
		"""
		self["hdr"]=header

	def addLogText(self, log):
		"""
			Add text to the output log.

			:Args:
				- `log` : 	log text
		"""
		self["log"]=log


if __name__ == '__main__':
	m=mosaicLog()

	m.addLogHeader("Event processing settings:")
	m.addLogText( "Algorithm = ADEPT" )
	m.addLogText( "Max. iterations  = {0}".format(10000) )
	m.addLogText( "Fit tolerance (rel. err in leastsq)  = {0}".format(1.e-7) )
	m.addLogText( "Initial partition threshold  = {0}".format(2.5) )
	m.addLogText( "Min. State Length = {0}".format(10) )

	print m
