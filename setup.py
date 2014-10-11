from distutils.core import setup, Command
from Cython.Build import cythonize
import numpy
import os
import sys

class UnitTests(Command):
    description = "run unit test suite."
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        os.system('nosetests -v -w utest/ testAlgos.py')

exec(open('pyeventanalysis/_version.py').read())
setup(
    cmdclass={'test': UnitTests},
    name='pyEventAnalysis',
    version=__version__,
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
            'qtgui.aboutdialog',
            'utilities'
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
            'qtgui/ui/SettingsWindow.ui',
            'qtgui/ui/trajviewui.ui',
            'qtgui/ui/advancedSettingsDialog.ui',
            'qtgui/ui/blockdepthview.ui',
            'qtgui/ui/statisticsview.ui',
            'qtgui/ui/fiteventsview.ui',
            'qtgui/ui/consoleDialog.ui',
            'qtgui/ui/aboutdialog.ui',
            'pyinstaller/pyEventAnalysis.spec',
            'icon.png',
            'pyinstaller-sh'
            ],
    url='http://pypi.python.org/pypi/pyEventAnalysis/',
    license='LICENSE.txt',
    description='Nanopore data analysis.',
    long_description=open('README.txt').read(),
    include_dirs=[numpy.get_include()],
)

#ext_modules = cythonize("pyeventanalysis/characterizeEvent.pyx"),
