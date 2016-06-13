# -*- coding: utf-8 -*-
"""
	An object that allows arbitrary formatting of log text.

	:Created:	09/12/2015
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT	
	:ChangeLog:
	.. line-block::
		06/13/14 	AB 	Remove mosaicLogFormat class
		09/12/15	AB	Initial version
"""
import sys

__all__=["mosaicLogFormat"]

def _d(msg, *args):
	frame1=sys._getframe(1)
	frame2=sys._getframe(2)
	n=len(args)

	m1="{0} ({{{1}}}:{{{2}}}:{{{3}}}:{{{4}}})".format(msg,n, n+1, n+2, n+3)
	a1=list(args)+[frame1.f_code.co_name, frame2.f_code.co_name, frame2.f_code.co_filename, frame2.f_lineno]
	
	return m1.format(*a1)

def _dprop(msg, *args):
	# frame1=sys._getframe(1)
	frame2=sys._getframe(2)
	n=len(args)

	m1="{0} ({{{1}}}:{{{2}}}:{{{3}}}:{{{4}}})".format(msg,n, n+1, n+2, n+3)
	a1=list(args)+["<property>", frame2.f_code.co_name, frame2.f_code.co_filename, frame2.f_lineno]
	
	return m1.format(*a1)

if __name__ == '__main__':
	def t():
		return _d("Test {0}", 100)
	print t()
