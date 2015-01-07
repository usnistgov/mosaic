import mosaic

def generateUtilsJS(baseurl, version):
	return """
	function detectOS() {{
		var OSName="";
		if (navigator.appVersion.indexOf("Win")!=-1) OSName="Windows";
		if (navigator.appVersion.indexOf("Mac")!=-1) OSName="Mac";
	//	if (navigator.appVersion.indexOf("X11")!=-1) OSName="UNIX";
	//	if (navigator.appVersion.indexOf("Linux")!=-1) OSName="Linux";

		return OSName
	}};
	function downloadText() {{
		OSName=detectOS();
		if (OSName != "") return document.write("Download for "+OSName);
		
		return document.write("Download Source")
	}};
	function sourceURL() {{
		return "{0}/v{1}/mosaic-nist-{1}.tar.gz";
	}}
	function OSXURL() {{
		return "{0}/v{1}/mosaic-{1}.dmg";
	}}
	function WindowsURL() {{
		return "{0}/v{1}/mosaic-x64-{1}.zip";
	}}
	function downloadURL() {{
		OSName=detectOS()
		url=sourceURL()
		if (OSName=="Mac") url=OSXURL();
		if (OSName=="Windows") url=WindowsURL();
		
		return url
	}};
	""".format(baseurl, version)


if __name__ == '__main__':
	with open('utils.js', 'w') as f:
		# str(mosaic.__version__)
		f.write(generateUtilsJS("https://github.com/usnistgov/mosaic/releases/download", "1.0"))

	print "Wrote utils.js"
