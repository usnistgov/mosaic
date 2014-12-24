
	function detectOS() {
		var OSName="";
		if (navigator.appVersion.indexOf("Win")!=-1) OSName="Windows";
		if (navigator.appVersion.indexOf("Mac")!=-1) OSName="Mac";
	//	if (navigator.appVersion.indexOf("X11")!=-1) OSName="UNIX";
	//	if (navigator.appVersion.indexOf("Linux")!=-1) OSName="Linux";

		return OSName
	};
	function downloadText() {
		OSName=detectOS();
		if (OSName != "") return document.write("Download for "+OSName);
		
		return document.write("Download Source")
	};
	function sourceURL() {
		return "https://github.com/usnistgov/mosaic/releases/download/v1.0b3.2/mosaic-1.0b3.2.tar.gz";
	}
	function OSXURL() {
		return "https://github.com/usnistgov/mosaic/releases/download/v1.0b3.2/mosaic-1.0b3.2.dmg";
	}
	function WindowsURL() {
		return "https://github.com/usnistgov/mosaic/releases/download/v1.0b3.2/mosaic-x64-1.0b3.2.zip";
	}
	function downloadURL() {
		OSName=detectOS()
		url=sourceURL()
		if (OSName=="Mac") url=OSXURL();
		if (OSName=="Windows") url=WindowsURL();
		
		return url
	};
	