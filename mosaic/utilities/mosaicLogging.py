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
import logging
import logging.handlers
import mosaic
from mosaic.utilities.mosaicLogHandlers import sqliteHandler

__all__=["mosaicLogging", "metaSingleton", "MessageFormatter"]

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
	__metaclass__ = metaSingleton

	_loggers = {}

	if sys.platform.startswith('darwin'):
		logdir=os.path.expanduser('~')+"/Library/Logs/MOSAIC/"
		if not os.path.exists(logdir):
			os.mkdir(logdir)
		logname=logdir+"/mosaic.log"
	elif sys.platform.startswith('linux'):
		logname="/var/log/mosaic.log"
	else:
		lognamd="mosaic.log"

	formatstr=MessageFormatter("%(asctime)-8s %(levelname)-8s %(name)-12s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

	logging.basicConfig(
			stream=sys.stdout,
			format="%(message)s",
			level=logging.INFO
		)
	log=logging.getLogger()

	rfh=logging.handlers.RotatingFileHandler(logname, maxBytes=mosaic.LogSize, backupCount=5)
	rfh.setFormatter(formatstr)
	if mosaic.DeveloperMode:
		rfh.setLevel(logging.DEBUG)
	else:
		rfh.setLevel(logging.INFO)
	log.addHandler(rfh)

	sh=None

	def __init__(self, *args, **kwargs):
		pass

	@staticmethod
	def getLogger(name=None, dbHnd=None):
		if not name:
			logger=logging.getLogger()
		elif name not in mosaicLogging._loggers.keys():
			mosaicLogging._loggers[name] = logging.getLogger(str(name))
		logger=mosaicLogging._loggers[name]

		if dbHnd:
			mosaicLogging.sh=sqliteHandler(dbHnd)
			mosaicLogging.sh.setLevel(logging.INFO)
			mosaicLogging.sh.setFormatter(logging.Formatter("%(message)s\n"))
			logger.addHandler(mosaicLogging.sh)
	
		# if locallog:
		# 	if mosaicLogging.fh==None:
		# 		mosaicLogging.fh=logging.FileHandler(locallog, mode=filemode)
		# 		mosaicLogging.fh.setLevel(logging.INFO)
		# 		mosaicLogging.fh.setFormatter(logging.Formatter("%(message)s"))
		
		# if mosaicLogging.fh:
		# 	logger.addHandler(mosaicLogging.fh)
	
		return logger

