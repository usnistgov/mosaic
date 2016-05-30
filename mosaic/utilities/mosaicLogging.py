"""
http://stackoverflow.com/questions/15727420/using-python-logging-in-multiple-modules
"""
import sys
import os
import logging
import logging.handlers
import mosaic

__all__=["mosaicLogging", "metaSingleton"]

class metaSingleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances.keys():
			cls._instances[cls] = super(metaSingleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]


class mosaicLogging(object):
	__metaclass__ = metaSingleton

	_loggers = {}

	if sys.platform.startswith('darwin'):
		logdir=os.path.expanduser('~')+"/Library/Logs/MOSAIC/"
		if not os.path.exists(logdir):
			os.mkdir(logdir)
		logname=logdir+"/mosaic.log"
	elif sys.platform.startswith('linux'):
		logname="/var/log/mosaic.log"

	formatstr=logging.Formatter("%(asctime)-8s %(levelname)-8s %(name)-12s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

	log=logging.getLogger()
	log.setLevel(logging.DEBUG)
	rfh=logging.handlers.RotatingFileHandler(logname, maxBytes=mosaic.LogSize, backupCount=5)
	rfh.setFormatter(formatstr)
	if mosaic.DeveloperMode:
		rfh.setLevel(logging.DEBUG)
	else:
		rfh.setLevel(logging.INFO)
	log.addHandler(rfh)

	def __init__(self, *args, **kwargs):
		pass

	@staticmethod
	def getLogger(name=None):
		if not name:
			return logging.getLogger()
		elif name not in mosaicLogging._loggers.keys():
			mosaicLogging._loggers[name] = logging.getLogger(str(name))
		return mosaicLogging._loggers[name]
