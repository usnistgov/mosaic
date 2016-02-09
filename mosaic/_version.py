import subprocess

__version__="1.3"

try:
	__build__=subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip()
except:
	__build__=""

try:
	if not __build__:
		with open('commit-hash', 'r') as f:
			__build__=f.read().strip()
except:
	__build__=""


