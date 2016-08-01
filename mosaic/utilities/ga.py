import httplib
import urllib
import uuid
from os.path import expanduser
import mosaic
from mosaic.utilities.resource_path import resource_path, format_path

_debug="/debug"
# _debug=""

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
	try:
		headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
		with open(resource_path("mosaic/utilities/.ga"), 'r') as ga:
			gac=eval(ga.read())
			gaid=gac["gaid"]
			gaurl=gac["gaurl"]

		payload="v=1&tid={0}&cid={1}&t=event&ec=mosaic-{2}-{3}&ea={4}&el={5}".format(
				gaid, 
				_uuid(),
				mosaic.__version__, 
				mosaic.__build__, 
				eventType,
				content
			)

		conn=httplib.HTTPSConnection(gaurl)
		conn.request("POST", "{0}/collect".format(_debug), payload, headers)
		response=conn.getresponse()
		data=response.read()

		conn.close()
		if _debug:
			print data
	except:
		pass

@registerRun
def foo():
	print "foo"

if __name__ == '__main__':
	foo()

