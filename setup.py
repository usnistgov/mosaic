from distutils.core import setup
from Cython.Build import cythonize
import numpy

def read_version():
    with open('version', 'r') as f:
        a=f.read()

    return a.rstrip()

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
            'qtgui.fiteventsview'
            ],
    scripts=[
            '.settings',
            'install-test-sh',
            'bin/analysis.py', 
            'dependencies/build-deps-sh', 
            'pyeventanalysis/utest/run-tests-sh', 
            'mathematica/nanoporeAnalysis.m', 
            'mathematica/Util.m', 
            'Makefile',
            'qtgui/SettingsWindow.ui',
            'qtgui/trajview/trajviewui.ui',
            'qtgui/advancedsettings/advancedSettingsDialog.ui',
            'qtgui/consolelog/consoleDialog.ui',
            'qtgui/blockdepthview/blockdepthview.ui',
            'qtgui/statisticsview/statisticsview.ui',
            'qtgui/fiteventsview/fiteventsview.ui'
            ],
    url='http://pypi.python.org/pypi/pyEventAnalysis/',
    license='LICENSE.txt',
    description='Nanopore analysis.',
    long_description=open('README.txt').read(),
    include_dirs=[numpy.get_include()],
)

#ext_modules = cythonize("pyeventanalysis/characterizeEvent.pyx"),
