from distutils.core import setup
from Cython.Build import cythonize
import numpy

def read_version():
    with open('version', 'r') as f:
        ver=f.read()

    return ver.rstrip()

setup(
    name='pyEventAnalysis',
    version=read_version(),
    author='Arvind Balijepalli',
    author_email='arvind.balijepalli@nist.gov',
    packages=[
            'pyeventanalysis', 
            'pyeventanalysis.utest', 
            'pyeventanalysis.trajviewer',
            'pyeventanalysis.qdf',
            'pyeventanalysis.abf',
            'qtgui',
            'qtgui.trajview',
            'qtgui.advancedsettings',
            'qtgui.consolelog',
            'qtgui.blockdepthview',
            'qtgui.statisticsview',
            'qtgui.fiteventsview',
            'utilities'
            ],
    scripts=[
            'version',
            '.settings',
            'install-test-sh',
            'bin/analysis.py', 
            'dependencies/build-deps-sh', 
            'pyeventanalysis/utest/run-tests-sh', 
            'mathematica/nanoporeAnalysis.m', 
            'mathematica/Util.m', 
            'Makefile',
            'qtgui/ui/SettingsWindow.ui',
            'qtgui/ui/trajviewui.ui',
            'qtgui/ui/advancedSettingsDialog.ui',
            'qtgui/ui/blockdepthview.ui',
            'qtgui/ui/statisticsview.ui',
            'qtgui/ui/fiteventsview.ui',
            'qtgui/ui/consoleDialog.ui',
            'pyinstaller/pyEventAnalysis.spec',
            'pyinstaller-sh'
            ],
    url='http://pypi.python.org/pypi/pyEventAnalysis/',
    license='LICENSE.txt',
    description='Nanopore data analysis.',
    long_description=open('README.txt').read(),
    include_dirs=[numpy.get_include()],
)

#ext_modules = cythonize("pyeventanalysis/characterizeEvent.pyx"),
