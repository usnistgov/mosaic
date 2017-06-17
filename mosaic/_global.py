import os.path

# Control global settings
DeveloperMode=False		# Turn on developer options.

CodeProfiling='summary'	# Either 'summary' to print a summary at the end of a run, 
						# 'none' for not timing, or 
						# 'all' to print timing of every function call profiled.
LogProperties=False		# Log all class properties defined with mosaic_property.
LogSizeBytes=int(2<<20) # 2 MB
DocumentationURL='https://pages.nist.gov/mosaic/'

# Options for MOSAIC Web
WebServerPort=5000
# WebServerDataLocation="Y:\\Desktop\\"
WebServerDataLocation=os.path.expanduser('~')+'/Google Drive/ReferenceData/'
