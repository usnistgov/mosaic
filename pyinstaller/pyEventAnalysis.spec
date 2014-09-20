# -*- mode: python -*-
a = Analysis(['../qtgui/qtAnalysisGUI.py'],
             pathex=['/Users/arvind/Research/Experiments/AnalysisTools/pyEventAnalysis/'],
             hiddenimports=['scipy.special._ufuncs_cxx', 'qtgui.mplwidget'],
             hookspath=None,
             runtime_hooks=None)
a.datas += [('.settings', '../.settings',  'DATA')]
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='pyEventAnalysis',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               Tree('../qtgui/ui', prefix='ui'),
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=os.path.join('dist', 'pyEventAnalysis'))
app = BUNDLE(coll,
               name=os.path.join('dist', 'pyEventAnalysis.app'))
