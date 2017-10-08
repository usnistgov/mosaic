# -*- coding: utf-8 -*-
"""
	Setup MOSAIC graphical interfaces.

	:Created:	10/07/2017
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		10/07/17 	AB 	Initial version
"""	
import sys
import multiprocessing
import argparse

from mosaicweb.run import startMOSAICWeb
from mosaicgui.run import startMOSAICQt


class mosaicSetup:
	def __init__(self):
		self.parseCLIArgs()

	def parseCLIArgs(self):
		self.parser = argparse.ArgumentParser(description='Run the MOSAIC graphical interface')
		
		self.parser.add_argument('-w', '--web', dest='web', default=False, action='store_true', help='Run the MOSAIC web interface')
		self.parser.add_argument('-q', '--qt', dest='qt', default=False, action='store_true', help='Run the MOSAIC Qt interface')
		
		self.args = vars(self.parser.parse_args())

	def launcMOSAIC(self):
		if sys.platform.startswith('win'):
			multiprocessing.freeze_support()

		if self.args["qt"]:
			startMOSAICQt()
		elif self.args["web"]:
			startMOSAICWeb()
		else:
			self.parser.print_help()