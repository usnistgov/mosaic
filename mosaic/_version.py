import subprocess

__version__="1.3"
try:
	__build__=subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
except:
	__build__=""