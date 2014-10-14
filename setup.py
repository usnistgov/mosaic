from setuptools import setup, Command
# from distutils.core import setup, Command
from Cython.Build import cythonize
# import numpy
import os
import sys

class UnitTests(Command):
    description = "run the unit test suite."
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        os.system('nosetests -v -w utest/ testAlgos.py')

class BuildDocs(Command):
    description = "build pyEventAnalysis documentation."
    user_options = [ ('html', None, "build HTML documentation"),
                     ('pdf', None, "build PDF documentation"),
                     ('all', None, "build HTML and PDF documentation"),
                     ('rebuild', None, "rebuild HTML and PDF documentation"),
                    ]

    def initialize_options(self):
        self.html = 0
        self.pdf = 0
        self.all = 0
        self.rebuild = 0

    def finalize_options(self):
        pass

    def run(self):
        if self.html:
            os.system("make -C doc-sphinx html")
        if self.pdf:
            os.system("make -C doc-sphinx latexpdf")
        if self.all:
            os.system("make -C doc-sphinx html latexpdf")
        if self.rebuild:
            os.system("make -C doc-sphinx clean html latexpdf")



exec(open('pyeventanalysis/_version.py').read())
setup(
    cmdclass={'unittest': UnitTests, 'docs': BuildDocs},
    name='pyEventAnalysis',
    version=__version__,
    author='Arvind Balijepalli',
    author_email='arvind.balijepalli@nist.gov',
    packages=[
            'pyeventanalysis', 
            'utest', 
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
            'install-test-sh',
            'bin/analysis.py', 
            'dependencies/build-deps-sh', 
            'utest/run-tests-sh', 
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
    # include_dirs=[numpy.get_include()],
)

#ext_modules = cythonize("pyeventanalysis/characterizeEvent.pyx"),
