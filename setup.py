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



exec(open('mosaic/_version.py').read())
setup(
    cmdclass={'unittest': UnitTests, 'docs': BuildDocs},
    name='mosaic',
    version=__version__,
    author='Arvind Balijepalli',
    author_email='arvind.balijepalli@nist.gov',
    packages=[
            'mosaic', 
            'utest', 
            'mosaic.qdf',
            'mosaic.abf',
            'mosaicgui',
            'mosaicgui.trajview',
            'mosaicgui.advancedsettings',
            'mosaicgui.consolelog',
            'mosaicgui.blockdepthview',
            'mosaicgui.statisticsview',
            'mosaicgui.fiteventsview',
            'mosaicgui.aboutdialog',
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
            'mosaicgui/ui/SettingsWindow.ui',
            'mosaicgui/ui/trajviewui.ui',
            'mosaicgui/ui/advancedSettingsDialog.ui',
            'mosaicgui/ui/blockdepthview.ui',
            'mosaicgui/ui/statisticsview.ui',
            'mosaicgui/ui/fiteventsview.ui',
            'mosaicgui/ui/consoleDialog.ui',
            'mosaicgui/ui/aboutdialog.ui',
            'pyinstaller/mosaic.spec',
            'icon.png',
            'pyinstaller-sh'
            ],
    url='http://pypi.python.org/pypi/MOSAIC/',
    license='LICENSE.txt',
    description='A Modular Single-Molecule Analysis Interface.',
    long_description=open('README.txt').read(),
    # include_dirs=[numpy.get_include()],
)

#ext_modules = cythonize("mosaic/characterizeEvent.pyx"),
