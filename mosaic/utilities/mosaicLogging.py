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
		logdir=os.path.expanduser('~')+"/Library/Logs/MOSAIC"
		if not os.path.exists(logdir):
			os.mkdir(logdir)
		logname=logdir+"/mosaic.log"
	elif sys.platform.startswith('linux'):
		logname="/var/log/mosaic.log"
	else:
		logname="mosaic.log"

	log=logging.getLogger()
	log.setLevel(logging.DEBUG)

	formatstr=MessageFormatter("%(asctime)-8s %(levelname)-8s %(name)-12s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

	sfh=logging.StreamHandler(stream=sys.stdout)
	sfh.setFormatter(logging.Formatter("%(message)s"))
	sfh.setLevel(logging.INFO)

	rfh=logging.handlers.RotatingFileHandler(filename=logname, maxBytes=mosaic.LogSize, backupCount=5)
	rfh.setFormatter(formatstr)
	if mosaic.DeveloperMode:
		rfh.setLevel(logging.DEBUG)
	else:
		rfh.setLevel(logging.INFO)
	
	log.addHandler(rfh)
	log.addHandler(sfh)

	sh=None

	def __init__(self, *args, **kwargs):
		pass

	@staticmethod
	def getLogger(name=None, dbHnd=None):
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
