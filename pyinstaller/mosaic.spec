# -*- mode: python -*-
import sys
from mosaic.utilities.resource_path import resource_path, format_path

a = Analysis(['../mosaicgui/mosaicGUI.py'],
			 pathex=['..'], 		# resource_path('.settings')
			 hiddenimports=['scipy.special._ufuncs_cxx', 'mosaicgui.mplwidget','Tkinter','FixTk','_tkinter','Tkconstants','FileDialog','Dialog'],
			 hookspath=None,
			 runtime_hooks=None)
# ('.settings', '../.settings',  'DATA'),
a.datas += [ ('icon.png', '../icons/icon.png',  'DATA')]
pyz = PYZ(a.pure)
# On OS X, collect data files and  build an application bundle
if sys.platform=='darwin':
	exe = EXE(pyz,
		  a.scripts,
		  exclude_binaries=True,
		  name='MOSAIC',
		  debug=False,
		  strip=None,
		  upx=True,
		  console=False,
		  icon='icon.png' )
	coll = COLLECT(exe,
				   a.binaries,
				   Tree('../mosaicgui/ui', prefix='ui'),
				   a.zipfiles,
				   a.datas,
				   strip=None,
				   upx=True,
				   name=os.path.join('dist', 'MOSAIC'))
	app = BUNDLE(coll,
				   name=os.path.join('dist', 'MOSAIC.app'))
elif sys.platform=='win32' or sys.platform=='win64':
	for d in a.datas:
		if 'pyconfig' in d[0]: 
			a.datas.remove(d)
			break
	exe = EXE(pyz,
		a.scripts,
		a.binaries,
		Tree(format_path('../mosaicgui/ui'), prefix='ui'),
		a.zipfiles,
		a.datas,
		name='MOSAIC.exe',
		debug=False,
		strip=None,
		upx=True,
		console=False,
		icon='..\\icons\\icon_256px.ico' )
	# coll = COLLECT(exe,
	# 	a.binaries,
	# 	Tree(format_path('../mosaicgui/ui'), prefix='ui'),
	# 	a.zipfiles,
	# 	a.datas,
	# 	strip=None,
	# 	upx=True,
	# 	name=os.path.join('dist', 'MOSAIC'))