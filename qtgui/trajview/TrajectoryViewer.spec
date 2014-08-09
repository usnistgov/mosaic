# -*- mode: python -*-
a = Analysis(['trajviewer.py'],
             pathex=['/Users/arvind/Research/Experiments/AnalysisTools/pyEventAnalysis/pyeventanalysis/trajviewer'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='TrajectoryViewer',
          debug=False,
          strip=None,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name='TrajectoryViewer')
app = BUNDLE(coll,
             name='TrajectoryViewer.app',
             icon=None)
