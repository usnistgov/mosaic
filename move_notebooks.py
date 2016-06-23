import glob
import os
import shutil

for g in glob.glob('*_files*'):
	try:
		shutil.rmtree( os.path.abspath( 'source/doc/'+g[:-6]+'_files' ) )
	except OSError, err:
		print err
		pass

	shutil.copy( os.path.abspath(g[:-6]+'.rst'), os.path.abspath('source/doc/') )
	shutil.move( os.path.abspath(g[:-6]+'_files'), os.path.abspath('source/doc/') )