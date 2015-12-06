from setuptools import setup, Command
import mosaic
import os
import sys

class mosaicUnitTests(Command):
    description = "run the MOSAIC unit test suite."
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        if not self.verbose:
            os.system('nosetests -w mosaic/utest/ mosaicTests.py')
        else:
            os.system('nosetests -v -w mosaic/utest/ mosaicTests.py')

class mosaicBinaries(Command):
    description = "build MOSAIC binaries."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('sh .scripts/pyinstaller-sh')

class mosaicDependencies(Command):
    description = "install MOSAIC dependencies."
    user_options = [
                    ('upgrade', None, "force packages to upgrade"),
                    ]

    def initialize_options(self):
        self.upgrade=0

    def finalize_options(self):
        pass

    def run(self):
        # os.system('sh .scripts/build-deps-sh')
        if self.upgrade:
            os.system('pip install -r requirements.txt --upgrade')
        else:
            os.system('pip install -r requirements.txt')

class mosaicDocumentationDependencies(Command):
    description = "install dependencies for Sphinx documentation."
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('sh .scripts/build-docs-deps-sh')

class mosaicAddons(Command):
    description = "install MOSAIC addons (Mathematica, Igor and Matlab scripts)."
    user_options = [ 
                    ('mathematica', None, "install Mathematica scripts"),
                    ('igor', None, "install IGOR SQLite drivers"),
                    ('all', None, "install all scripts"),
                    ]

    def initialize_options(self):
        self.mathematica = 0
        self.igor = 0
        self.all = 0

    def finalize_options(self):
        pass

    def run(self):
        if self.mathematica:
            os.system('sh .scripts/install-addons-sh ')
        elif self.igor:
            os.system( 'sh .scripts/install-igor-addons-sh' )
        else:
            os.system('sh .scripts/install-addons-sh ')
            os.system( 'sh .scripts/install-igor-addons-sh' )

class mosaicDocs(Command):
    description = "build MOSAIC documentation."
    user_options = [ ('all', None, "build HTML and PDF documentation (default)"),
                     ('html', None, "build HTML documentation"),
                     ('pdf', None, "build PDF documentation"),
                     ('rebuild', None, "rebuild HTML and PDF documentation"),
                    ]

    def initialize_options(self):
        self.html = 0
        self.pdf = 0
        self.all = 0
        self.rebuild = 0
        self.upload = 0

    def finalize_options(self):
        pass

    def run(self):
        # always build docs in the master branch.
        os.system("git checkout master")
        if self.html:
            os.system("make -C _docs html")
        elif self.pdf:
            os.system("make -C _docs latexpdf")
        elif self.rebuild:
            os.system("make -C _docs clean html latexpdf")
        else:
            os.system("make -C _docs html latexpdf")
        

setup(
    cmdclass={
        'mosaic_tests'      : mosaicUnitTests, 
        'mosaic_docs'       : mosaicDocs, 
        'mosaic_bin'        : mosaicBinaries, 
        'mosaic_deps'       : mosaicDependencies, 
        'mosaic_docs_deps'  : mosaicDocumentationDependencies, 
        'mosaic_addons'     : mosaicAddons
        },
    name='mosaic-nist',
    version=mosaic.__version__,
    author='Arvind Balijepalli',
    author_email='arvind.balijepalli@nist.gov',
    packages=[
            'mosaic', 
            'mosaic.utest', 
            'mosaic.qdf',
            'mosaic.abf',
            'mosaic.utilities'
            ],
    scripts=[
            'bin/analysis.py', 
            'addons/mathematica/MosaicAnalysis.m', 
            'addons/mathematica/MosaicUtils.m', 
            'addons/mathematica/Util.m', 
            'addons/MATLAB/openandquery.m', 
            'icons/icon_100px.png',
            '.scripts/install-addons-sh',
            '.scripts/build-deps-sh', 
            '.scripts/pyinstaller-sh',
            'data/eventMD-PEG28-stepResponseAnalysis.sqlite',
            'data/eventMD-PEG28-cusumLevelAnalysis.sqlite',
            'data/.settings',
            'data/SingleChan-0001.qdf',
            'data/SingleChan-0001_state.txt'
            ],
    install_requires=[
          'numpy==1.8.1',
          'cython==0.20.1',
          'scipy==0.15.0',
          'lmfit==0.7.4',
          'uncertainties==2.4.6',
          'matplotlib==1.3.1',
          'PyWavelets==0.2.2',
      ],
    url='https://usnistgov.github.io/mosaic/',
    license='LICENSE.txt',
    description='A Modular Single-Molecule Analysis Interface.',
    long_description=open('README.rst').read(),
    # include_dirs=[numpy.get_include()],
)
