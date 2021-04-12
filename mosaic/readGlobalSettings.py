import json
import sys
import os.path
from mosaic.utilities.resource_path import resource_path

def readGlobalSettings():
	try:
		with open( resource_path("mosaic/global.json"), mode="r") as j_object:
			data = json.load(j_object)
	except FileNotFoundError:
		print("Global settings not found. Using default values")
		data=json.loads(
				"""
					{
						"DeveloperMode"			:	false,
						"CodeProfiling"			:	"summary",
						"LogProperties"			:	false,
						"LogSizeBytes"			:	16777216,
						"DocumentationURL"		:	"https://pages.nist.gov/mosaic/",
						"WebHost"				:	"0.0.0.0",
						"WebServerPort"			:	5000,
						"WebServerWorkers"		:	1,
						"WebServerDataLocation"	:	"~",
						"WebServerMode"			:	"local"

					}
				"""
			)

	# Handle special paths
	if data["WebServerDataLocation"]=="~":
		data["WebServerDataLocation"]=os.path.expanduser("~")

	return data

if __name__ == '__main__':
	mosaic_mod = sys.modules[__name__]
	for (k,v) in readGlobalSettings().items():
		setattr(mosaic_mod, k, v)

	print(DeveloperMode)
	print(WebHost)