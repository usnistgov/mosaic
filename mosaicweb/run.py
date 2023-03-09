import webbrowser
import sys
import mosaicweb
from mosaic.utilities.ga import registerLaunch
import mosaic


if sys.platform.startswith('win'):
	from mosaicweb import app
else:
	import gunicorn.app.base

	class mosaicApplication(gunicorn.app.base.BaseApplication):

		def __init__(self, app, options=None):
			self.options = options or {}
			self.application = app
			super().__init__()

		def load_config(self):
			config = {key: value for key, value in self.options.items()
					if key in self.cfg.settings and value is not None}
			for key, value in config.items():
				self.cfg.set(key.lower(), value)

		def load(self):
			return self.application

@registerLaunch("mweb")
def startMOSAICWeb(newWindow=True):
	#if mosaic.DeveloperMode:
	WebServerPort=mosaic.WebServerPort
	#else:
	#	WebServerPort=getAvailablePort()

	webbrowser.open("http://localhost:{0}/".format(WebServerPort), new=newWindow, autoraise=True)
	
	# Setup platform-dependent timing function
	if sys.platform.startswith('win'):
		app.run(host=mosaic.WebHost, port=WebServerPort, debug=mosaic.DeveloperMode)
	else:
		mosaicApp=mosaicApplication(mosaicweb.app, {
				'bind' 		: '%s:%s' % (mosaic.WebHost, WebServerPort),
				'workers'	: mosaic.WebServerWorkers
			})
		mosaicApp.run()

	
def getAvailablePort():
	from socket import socket

	with socket() as s:
		s.bind(('',0))

		port=s.getsockname()[1]

	return port
	
	