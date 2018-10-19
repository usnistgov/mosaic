#! /usr/bin/env python
import multiprocessing
import sys
from mosaic.mosaicSetup	import mosaicSetup

if __name__ == '__main__':
	if sys.platform.startswith('win'):
		multiprocessing.freeze_support()

	mosaicSetup().launcMOSAIC()

