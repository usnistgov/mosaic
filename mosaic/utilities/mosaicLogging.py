# -*- coding: utf-8 -*-
"""
	An implementation of Python logging heavily adapted from `<http://stackoverflow.com/questions/15727420/using-python-logging-in-multiple-modules>`_.

	:Created:	5/29/2016
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		5/30/16 	AB 	Strip whitespace from rotating file handler messages.
		5/29/16		AB	Initial version
"""
import sys
import os
import warnings
import logging
import logging.handlers
import mosaic
from mosaic.utilities.mosaicLogHandlers import sqliteHandler
from mosaic.utilities.resource_path import format_path

__all__=["mosaicLogging", "metaSingleton", "MessageFormatter", "mosaicExceptionHandler"]

def mosaicExceptionHandler(extype, exvalue, extb):
	if issubclass(extype, KeyboardInterrupt):
		sys.__excepthook__(extype, exvalue, extb)
		return

	logger=mosaicLogging().getLogger(__name__)
	handler = logging.StreamHandler(stream=sys.stderr)
	logger.addHandler(handler)
	logger.critical("", exc_info=(extype, exvalue, extb))


class metaSingleton(type):
	_instances = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances.keys():
			cls._instances[cls] = super(metaSingleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class MessageFormatter(logging.Formatter):
    def format(self, record):
        record.msg = record.msg.strip()
        return super(MessageFormatter, self).format(record)


class mosaicLogging(object):
	"""
		A custom logging class that uses the Python logging facility. Logs are automatically saved to a metaMDIO instance,
		and to a file log when DeveloperMode is active.
	"""
	__metaclass__ = metaSingleton

	_loggers = {}

	log=logging.getLogger()
	log.setLevel(logging.DEBUG)

	formatstr=MessageFormatter("%(asctime)-8s %(levelname)-8s %(name)-12s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

	# Rotating File Handler
	try:
		logdir=mosaic.LogLocation

		defaultLogLocation=False
	except AttributeError, err:
		defaultLogLocation=True

		if sys.platform.startswith('darwin'):
			logdir=format_path(os.path.expanduser('~')+"/Library/Logs/MOSAIC")
			if not os.path.exists(logdir):
				os.mkdir(logdir)
		elif sys.platform.startswith('linux'):
			if os.getuid()==0:
				logdir="/var/log/"
			else:
				log.info("MOSAIC log will be saved to ~/mosaic.log. Run MOSAIC with sudo to save logs to '/var/log/.")
				logdir=os.path.expanduser("~")
		else:
			logdir=os.path.expanduser("~")

	logname=format_path(logdir+"/mosaic.log")


	rfh=logging.handlers.RotatingFileHandler(filename=logname, maxBytes=mosaic.LogSizeBytes, backupCount=5)
	rfh.setFormatter(formatstr)
	if mosaic.DeveloperMode:
		rfh.setLevel(logging.DEBUG)
	else:
		rfh.setLevel(logging.INFO)
	
	log.addHandler(rfh)

	if defaultLogLocation:
		warntext="WARNING: Global settings attribute 'LogLocation' was not defined. Logs will be saved to the default location: {0}".format(logname)
		log.warning(warntext)
		warnings.warn(warntext, RuntimeWarning)

	sh=None

	def __init__(self, *args, **kwargs):
		pass

	@staticmethod
	def getLogger(name=None, dbHnd=None):
		"""
			Get a logger instance. 

			:Parameters:

				- `name`  : Logger name
				- `dbHnd` : MetaMDIO handle to allow logs to be saved to the database.

			:Usage:

				In this example, we get an instance of a logger with the module name and log a debug message.

				.. code-block:: python 

					logger=mosaicLogging().getLogger(__name__)

					logger.debug("Test debug message")

		"""
		if not name:
			logger=logging.getLogger()
		elif name not in mosaicLogging._loggers.keys():
			logger=logging.getLogger(str(name))
			mosaicLogging._loggers[name]=logger
		else:
			logger=mosaicLogging._loggers[name]

		if dbHnd:
			# if a db handle is set, update all loggers with the new handle
			mosaicLogging.sh=sqliteHandler(dbHnd)
			mosaicLogging.sh.setLevel(logging.INFO)
			mosaicLogging.sh.setFormatter(logging.Formatter("%(message)s\n"))

			for name in mosaicLogging._loggers.keys():
				l=mosaicLogging._loggers[name]
				for h in l.handlers:
					if isinstance(h, sqliteHandler):
						l.removeHandler(h)
				
				l.addHandler(mosaicLogging.sh)
	
		return logger

if __name__ == '__main__':
	logger=mosaicLogging().getLogger(__name__)

	logger.debug("Test debug message")
