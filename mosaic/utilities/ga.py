"""
	A basic framework for GA support.


	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
"""	
import httplib
import urllib2
import uuid
import json
import tempfile
from base64 import b64decode as dec
from os.path import expanduser, isfile
from functools import wraps
import os
import traceback
from datetime import datetime, timedelta
import mosaic
import mosaic.utilities.mosaicLogging as mlog
from mosaic.utilities.mosaicLogFormat import _d
from mosaic.utilities.resource_path import resource_path, format_path
from mosaic.utilities.util import eval_

def registerLaunch(tag):
	def _registerLaunch(func):
		@wraps(func)
		def funcWrapper(*args, **kwargs):
			_gaPost("launch_"+tag, func.__name__)
			return func(*args, **kwargs)
		return funcWrapper
	return _registerLaunch

def registerQuit(tag):
	def _registerQuit(func):
		@wraps(func)
		def funcWrapper(*args, **kwargs):
			_gaPost("quit_"+tag, func.__name__)
			return func(*args, **kwargs)
		return funcWrapper
	return _registerQuit

def registerStart(tag):
	def _registerStart(func):
		@wraps(func)
		def funcWrapper(*args, **kwargs):
			_gaPost("start_"+tag, func.__name__)
			return func(*args, **kwargs)
		return funcWrapper
	return _registerStart


def registerStop(tag):
	def _registerStop(func):
		@wraps(func)
		def funcWrapper(*args, **kwargs):
			_gaPost("stop_"+tag, func.__name__)
			return func(*args, **kwargs)
		return funcWrapper
	return _registerStop


def _uuid():
	uuidfile=format_path(tempfile.gettempdir()+'/.mosaicuuid')
	try:
		with open (uuidfile, "r") as u:
			return u.read()
	except:
		uuidgen=str(uuid.uuid4())
		with open(uuidfile, "w") as uw:
			uw.write(uuidgen)
		return uuidgen

def _gaPost(eventType, content):
	logger=mlog.mosaicLogging().getLogger(name=__name__)

	try:
		headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
		gac=_gaCredentialCache()

		if eval_(gac["gaenable"]):
			payload="v=1&tid={0}&cid={1}&t=event&ec=mosaic-{2}-{3}&ea={4}&el={5}".format(
					dec(gac["gaid"]), 
					_uuid(),
					mosaic.__version__, 
					mosaic.__build__, 
					eventType,
					content
				)

			if mosaic.DeveloperMode:
				_debug="/debug"
			else:
				_debug=""

			conn=httplib.HTTPSConnection(dec(gac["gaurl"]))
			conn.request("POST", "{0}/{1}".format(_debug, dec(gac["gamode"])), payload, headers)
			response=conn.getresponse()
			data=response.read()

			conn.close()
			if _debug:
				logger.debug(_d("ga collect: {0}", data))
	except BaseException as err:
		logger.debug(_d("Exception ignored: {0}\n{1}", repr(err), traceback.format_exc()))
		pass

def _gaCredentialCache():
	try:
		try:
			logger=mlog.mosaicLogging().getLogger(name=__name__)
			
			ga_cache=format_path(tempfile.gettempdir()+'/.ga')
			logger.debug(_d("Looking for GA cache {0}", ga_cache))

			gaModTime = datetime.fromtimestamp(os.stat(ga_cache).st_mtime)
			gaExpireAge=timedelta(hours=24)
			gaAge=datetime.today() - gaModTime

			if gaAge > gaExpireAge:
				logger.debug(_d("GA settings cache has expired."))
				ga_old=_gaSettingsDict(ga_cache)
				_getGASettings(ga_cache)
				ga_new=_gaSettingsDict(ga_cache)

				if ga_old["gaenable"]==False:
					ga_new["gaenable"]=False

				with open(ga_cache, "w") as ga:
					ga.write(json.dumps(ga_new))
			else:
				logger.debug(_d("GA settings cache found ({0}). gaAge={1}", str(ga_cache), str(gaAge)))
		except:
			logger.debug(_d("GA settings are not cached."))
			_getGASettings(ga_cache)

		with open(ga_cache, 'r') as ga:
			return json.loads(ga.read())
	except BaseException as err:
		logger.debug(_d("Exception ignored: {0}\n{1}", repr(err), traceback.format_exc()))
		return

def _gaSettingsDict(ga_cache):
	with open(ga_cache, 'r') as ga:
		return dict(json.loads(ga.read()))

def _getGASettings(ga_cache):
	logger=mlog.mosaicLogging().getLogger(name=__name__)
	
	try:
		req=urllib2.Request(mosaic.DocumentationURL+".ga")
		streamHandler=urllib2.build_opener()
		stream=streamHandler.open(req)

		with open(ga_cache, 'w') as ga:
			ga.write( stream.read() )

		logger.info("Cached GA settings to {0}.".format(str(ga_cache)))
	except:
		logger.exception(_d("An error occured when trying to cache GA settings."))

_gaCredentialCache()

@registerLaunch("cli")
def foo():
	print "foo"

if __name__ == '__main__':
	foo()

