# -*- mode: python -*-
import sys
from mosaic.utilities.resource_path import resource_path, format_path
sys.setrecursionlimit(5000)

a = Analysis(
				['../runMOSAIC.py'],
				pathex=['..'], 		# resource_path('.settings')
				hiddenimports=[
				 		'scipy.special._ufuncs_cxx', 
				 		'pywt._extensions._cwt',
				 		'email.mime.multipart',
				 		'email.mime.message',
						'email.mime.text',
						'email.mime.image',
						'email.mime.audio', 
						'sqlalchemy.sql.default_comparator',
						'jinja2',
						'gunicorn.glogging',
						'gunicorn.workers.sync'
				 	],
				datas = [ 
					('../icons/*.png', 'icons'),
					('../commit-hash', '.'),
					('../version-hash', '.'),
					('../mweb-version-hash', '.'),
					('../mosaicweb/templates/index.html', 'mosaicweb/templates')
				],
				hookspath=None,
				runtime_hooks=None
			)

pyz = PYZ(a.pure)
# On OS X, collect data files and  build an application bundle
if sys.platform=='darwin':
	exe = EXE(
				pyz,
				a.scripts,
				exclude_binaries=True,
				name='MOSAIC',
				debug=False,
				strip=None,
				upx=True,
				console=False,
				icon='icon.png' 
			)
	coll = COLLECT(
					exe,
					a.binaries,
					Tree('../mosaicweb/static', prefix='mosaicweb/static'),
					a.zipfiles,
					a.datas,
					strip=None,
					upx=True,
					name=os.path.join('dist', 'MOSAIC')
				)
	app = BUNDLE(
					coll,
				   	name=os.path.join('dist', 'MOSAIC.app')
				)
elif sys.platform=='win32' or sys.platform=='win64':
	for d in a.datas:
		if 'pyconfig' in d[0]: 
			a.datas.remove(d)
			break
	exe = EXE(pyz,
		a.scripts,
		a.binaries,
		Tree(format_path('../mosaicweb/static'), prefix='mosaicweb/static'),
		a.zipfiles,
		a.datas,
		name='MOSAIC.exe',
		debug=False,
		strip=None,
		upx=True,
		console=False,
		icon='..\\icons\\icon_256px.ico' )
