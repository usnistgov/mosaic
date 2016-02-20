import glob
import os

for g in glob.glob('*_files*'):
	os.system( 'mv {0} {1}'.format(g[:-6]+'.rst', 'source/doc/') )
	os.system( 'mv {0} {1}'.format(g[:-6]+'_files', 'source/doc/') )