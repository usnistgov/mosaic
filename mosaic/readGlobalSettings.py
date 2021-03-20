import json
import sys

def readGlobalSettings():
	with open("mosaic/global.json", mode="r") as j_object:
		data = json.load(j_object)

	return data

if __name__ == '__main__':
	mosaic_mod = sys.modules[__name__]
	for (k,v) in readGlobalSettings().items():
		setattr(mosaic_mod, k, v)

	print(DeveloperMode)
	print(WebHost)