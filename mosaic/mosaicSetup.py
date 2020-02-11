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
import argparse

class mosaicSetup:
	def __init__(self):
		self.parseCLIArgs()
		# pass

	def parseCLIArgs(self):
		self.parser = argparse.ArgumentParser(description='Run the MOSAIC graphical interface')
		
		self.parser.add_argument('-w', '--web', dest='web', default=True, action='store_true', help='(default) Run the MOSAIC web interface (default)')
		self.parser.add_argument('-q', '--qt', dest='qt', default=False, action='store_true', help='(depracated) Run the MOSAIC Qt interface')
		
		self.args = vars(self.parser.parse_args())

	def launchMOSAIC(self):
		if self.args["qt"]:
			print("\nThe MOSAIC Qt GUI is no longer supported. Please use the web interface.\n")			

			self.parser.print_help()
		elif self.args["web"]:
			try:
				from mosaicweb.run import startMOSAICWeb
			except ImportError as err:
				print("Missing dependencies for Web GUI ({0}).".format(err))
				return
			startMOSAICWeb()
		else:
			self.parser.print_help()

		# from mosaicweb.run import startMOSAICWeb
		# startMOSAICWeb()
	
