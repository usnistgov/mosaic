import subprocess
from mosaic.utilities.resource_path import resource_path

__version__="1.3b4"

try:
	__build__=subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'], stderr=subprocess.STDOUT).strip()
except:
	__build__=""

try:
	if not __build__:
		with open( resource_path('commit-hash'), 'r' ) as f:
			__build__=f.read().strip()
except:
	__build__=""
