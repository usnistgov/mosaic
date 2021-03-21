import webbrowser
import gunicorn.app.base
import mosaicweb
from mosaic.utilities.ga import registerLaunch
import mosaic

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
	mosaicApp=mosaicApplication(mosaicweb.app, {
			'bind' : '%s:%s' % (mosaic.WebHost, mosaic.WebServerPort)
		})
	webbrowser.open("http://localhost:{0}/".format(mosaic.WebServerPort), new=newWindow, autoraise=True)
	#app.run(host=mosaic.WebHost, port=mosaic.WebServerPort, debug=mosaic.DeveloperMode)
	mosaicApp.run()