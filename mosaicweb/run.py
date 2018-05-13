import webbrowser
from mosaicweb import app
from mosaic.utilities.ga import registerLaunch
import mosaic

@registerLaunch("mweb")
def startMOSAICWeb(newWindow=True):
	webbrowser.open("http://localhost:{0}/".format(mosaic.WebServerPort), new=newWindow, autoraise=True)
	app.run(port=mosaic.WebServerPort, debug=mosaic.DeveloperMode)