import mosaic

def GenerateTitle():
	return """
		<table>
			<tr>
				<td><a href="index.html"><img class="mosaiclogo" src="landing-images/icon.png" height="75" width="75" alt="MOSAIC"></td>
				<td><p class="downloadtitle">MOSAIC Downloads</p></td>
			</tr>
		</table>
	"""

def GenerateHeader():
	return """
	<head>
	    <title>MOSAIC Downloads</title>
	    <link rel="icon" href="source/favicon.ico" type="image/ico">
	
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<meta http-equiv="Content-Language" content="en">
		<meta http-equiv="Content-Style-Type" content="text/css">
		
		<link href='//fonts.googleapis.com/css?family=Roboto:100,300,100italic,300italic' rel='stylesheet' type='text/css'>
		<link rel="stylesheet" type="text/css" href="style.css">
		
		<script src="//ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
		<script src="utils.js"></script>		
	</head>
	
	<body>
	"""
def GenerateTableFromVersion(baseurl, title, version, showBinaries=True):
	tabsrc="""
		<p class="downloadversion" align="left"><b><em>{0}</em></b></p>
		<table class="downloadtable">
			<col width=40%>
			<col width=60%>
		""".format(title)
	if showBinaries:
		tabsrc+="""
			<tr>
				<td class="downloadtext"><a class="downloadtext" href="{0}/mosaic-{1}.dmg">mosaic-{1}.dmg</a></td>
				<td class="downloadtext"><p class="downloadtext">Mac OS X, 10.8+</p></td>
			</tr>
			<tr>
				<td class="downloadtext"><a class="downloadtext" href="{0}/mosaic-x64-{1}.zip">mosaic-x64-{1}.zip</a></td>
				<td class="downloadtext"><p class="downloadtext">Windows, 64-bit</p></td>
			</tr>
		""".format(baseurl, version)
	tabsrc+="""
			<tr>
				<td class="downloadtext"><a class="downloadtext" href="{0}/mosaic-{1}.tar.gz">mosaic-{1}.tar.gz</a></td>
				<td class="downloadtext"><p class="downloadtext">MOSAIC Source</p></td>
			</tr>
		</table>
	""".format(baseurl, version)

	return tabsrc

if __name__ == '__main__':
	url="https://github.com/usnistgov/mosaic/releases/download/v"
	vers=[
		# ("Version "+str(mosaic.__version__), str(mosaic.__version__), True),
		("Version 1.0 Beta 3, Update 2", "1.0b3.2",True),
		("Version 1.0 Beta 3, Update 1", "1.0b3.1",False),
		("Version 1.0 Beta 3", "1.0b3",False),
		("Version 1.0 Beta 2", "1.0b2",False),
		("Version 1.0 Beta 1", "1.0b1",False)
	]
	htmlout="""
	<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
	<html lang="en">
	"""

	htmlout+=GenerateHeader()
	htmlout+=GenerateTitle()
	for v in vers:
		htmlout+=GenerateTableFromVersion(url+v[1], v[0], v[1], v[2])
	htmlout+="""
		<br /><br /><br /><br /><br /><br /><br /><br />
			<div>
				<hr />
					<table class="legal" align="center">
						<tr class="legal" style="vertical-align: center">
							<td><a class="legal" href="http://pml.nist.gov">Physical Measurement Laboratory</a></td>
							<td><img class="grayscale" src="landing-images/icon.png" height="20" width="20" alt="MOSAIC"><td>
							<td><a class="legal" href="http://nist.gov">National Institute of Standards and Technology</a></td>
						</tr>
					</table>
			</div>
		</body>
	</html>"""

	with open('platforms.html', 'w') as f:
		f.write(htmlout)

	print "Wrote platforms.html"

