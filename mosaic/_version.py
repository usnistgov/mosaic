import subprocess
from mosaic.utilities.resource_path import resource_path

try:
	__version__=subprocess.check_output(['git', 'describe', '--abbrev=0', '--match', 'v*', 'HEAD'], stderr=subprocess.STDOUT).strip().lstrip('v')
except:
	__version__=""

try:
	if not __version__:
		with open( resource_path('version-hash'), 'r' ) as f:
			__version__=f.read().strip()		
except:
	__version__=""

try:
	__mweb_version__=subprocess.check_output(['git', 'describe', '--abbrev=0', '--match', 'mwebv*', 'HEAD'], stderr=subprocess.STDOUT).strip().lstrip('mwebv')
except:
	__mweb_version__=""

try:
	if not __mweb_version__:
		with open( resource_path('mweb-version-hash'), 'r' ) as f:
			__mweb_version__=f.read().strip()		
except:
	__mweb_version__=""

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
