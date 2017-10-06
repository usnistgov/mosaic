from mosaicweb import app
import mosaic

if __name__ == '__main__':
	app.run(port=mosaic.WebServerPort, debug=mosaic.DeveloperMode)