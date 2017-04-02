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
import os
import traceback
from datetime import datetime, timedelta
import mosaic
import mosaic.utilities.mosaicLogging as mlog
from mosaic.utilities.mosaicLogFormat import _d
from mosaic.utilities.resource_path import resource_path, format_path

def registerLaunch(func):
	def funcWrapper(*args, **kwargs):
		_gaPost("launch", func.__name__)
		return func(*args, **kwargs)
	return funcWrapper

def registerRun(func):
	def funcWrapper(*args, **kwargs):
		_gaPost("run", func.__name__)
		return func(*args, **kwargs)
	return funcWrapper

def registerStop(func):
	def funcWrapper(*args, **kwargs):
		_gaPost("stop", func.__name__)
		return func(*args, **kwargs)
	return funcWrapper

def _uuid():
    uuidfile=format_path(expanduser('~')+"/.mosaicuuid")
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

		if eval(gac["gaenable"]):
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
	logger=mlog.mosaicLogging().getLogger(name=__name__)
	# ga_cache=resource_path("mosaic/utilities/.ga")
	ga_cache=format_path(tempfile.gettempdir()+'/.ga')
	logger.debug(_d("Looking for GA cache {0}", ga_cache))

	try:
		gaModTime = datetime.fromtimestamp(os.stat(ga_cache).st_mtime)
		gaExpireAge=timedelta(hours=24)
		gaAge=datetime.today() - gaModTime

		if gaAge > gaExpireAge:
			logger.debug(_d("GA settings cache has expired."))
			_getGASettings(ga_cache)
		else:
			logger.debug(_d("GA settings cache found. gaAge={0}", gaAge))

	except:
		logger.debug(_d("GA settings are not cached."))
		_getGASettings(ga_cache)

	with open(ga_cache, 'r') as ga:
		return json.loads(ga.read())

def _getGASettings(ga_cache):
	logger=mlog.mosaicLogging().getLogger(name=__name__)

	try:
		req=urllib2.Request(mosaic.DocumentationURL+".ga")
		streamHandler=urllib2.build_opener()
		stream=streamHandler.open(req)

		with open(ga_cache, 'w') as ga:
			ga.write( stream.read() )

		logger.debug(_d("Cached GA settings to {0}.", ga_cache))
	except:
		logger.exception(_d("An error occured when trying to cache GA settings."))

_gaCredentialCache()

@registerRun
def foo():
	print "foo"

if __name__ == '__main__':
	foo()

