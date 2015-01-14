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
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('sh .scripts/build-deps-sh')

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

    def finalize_options(self):
        pass

    def run(self):
        if self.html:
            os.system("make -C _docs html")
        elif self.pdf:
            os.system("make -C _docs latexpdf")
        elif self.rebuild:
            os.system("make -C _docs clean html latexpdf")
        else:
            os.system("make -C _docs html latexpdf")
        

setup(
    cmdclass={'mosaic_tests': mosaicUnitTests, 'mosaic_docs': mosaicDocs, 'mosaic_bin': mosaicBinaries, 'mosaic_deps': mosaicDependencies, 'mosaic_addons': mosaicAddons},
    name='mosaic-nist',
    version=mosaic.__version__,
    author='Arvind Balijepalli',
    author_email='arvind.balijepalli@nist.gov',
    packages=[
            'mosaic', 
            'mosaic.utest', 
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
            'mosaic.utilities'
            ],
    scripts=[
            'bin/analysis.py', 
            'addons/mathematica/MosaicAnalysis.m', 
            'addons/mathematica/MosaicUtils.m', 
            'addons/mathematica/Util.m', 
            'addons/MATLAB/openandquery.m', 
            'mosaicgui/ui/SettingsWindow.ui',
            'mosaicgui/ui/trajviewui.ui',
            'mosaicgui/ui/advancedSettingsDialog.ui',
            'mosaicgui/ui/blockdepthview.ui',
            'mosaicgui/ui/statisticsview.ui',
            'mosaicgui/ui/fiteventsview.ui',
            'mosaicgui/ui/consoleDialog.ui',
            'mosaicgui/ui/aboutdialog.ui',
            'pyinstaller/mosaic.spec',
            'icons/icon_100px.png',
            '.scripts/install-addons-sh',
            '.scripts/build-deps-sh', 
            '.scripts/pyinstaller-sh'
            ],
    url='http://pypi.python.org/pypi/mosaic-nist/',
    license='LICENSE.txt',
    description='A Modular Single-Molecule Analysis Interface.',
    long_description=open('README.rst').read(),
    # include_dirs=[numpy.get_include()],
)
