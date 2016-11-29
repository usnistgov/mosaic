from setuptools import setup, Command
import mosaic
import os
import sys
import nose
from mosaic.tests.mosaicUnitTests import _mosaicUnitTests

class mosaicBinaries(Command):
	description = "build MOSAIC binaries."
	user_options = [
					('inplace', 'i', "build binaries in the current branch"),
					]

	def initialize_options(self):
		self.inplace=0

	def finalize_options(self):
		pass

	def run(self):
		retval=0
		if not self.inplace:
			retval = os.system("git checkout master")

		if retval==0:
			os.system('sh .scripts/pyinstaller-sh')

class mosaicDependencies(Command):
	description = "install MOSAIC dependencies."
	user_options = [
					('upgrade', 'u', "force packages to upgrade"),
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
					('mathematica', 'm', "install Mathematica scripts"),
					('igor', 'i', "install IGOR SQLite drivers")
					]

	def initialize_options(self):
		self.mathematica = 0
		self.igor = 0

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
			os.system("make -C _nistpages html")
		elif self.pdf:
			os.system("make -C _nistpages latexpdf")
		elif self.rebuild:
			os.system("make -C _nistpages clean html latexpdf")
		else:
			os.system("make -C _nistpages html latexpdf")

setup(
	cmdclass={
		'test'              : _mosaicUnitTests(Command), 
		'nosetests'         : _mosaicUnitTests(Command), 
		'mosaic_tests'      : _mosaicUnitTests(Command), 
		'mosaic_docs'       : mosaicDocs, 
		'mosaic_bin'        : mosaicBinaries, 
		'mosaic_deps'       : mosaicDependencies, 
		'mosaic_docs_deps'  : mosaicDocumentationDependencies, 
		'mosaic_addons'     : mosaicAddons
		},
	name='mosaic-nist',
	version=mosaic.__version__+'+'+mosaic.__build__,
	author='Arvind Balijepalli',
	author_email='arvind.balijepalli@nist.gov',
	packages=[
			'mosaic', 
			'mosaic.filters',
			'mosaic.mdio',
			'mosaic.trajio',
			'mosaic.process',
			'mosaic.partition',
			'mosaic.apps', 
			'mosaic.tests', 
			'mosaic.trajio.qdf',
			'mosaic.trajio.abf',
			'mosaic.utilities'
			],
	scripts=[
			'bin/analysis.py', 
			'addons/mathematica/MosaicAnalysis.m', 
			'addons/mathematica/MosaicUtils.m', 
			'addons/mathematica/Util.m', 
			'addons/MATLAB/openandquery.m', 
			'icons/icon_100px.png',
			'icons/error-128.png',
			'icons/warning-128.png',
			'.scripts/install-addons-sh',
			'.scripts/pyinstaller-sh',
			'data/eventMD-PEG28-stepResponseAnalysis.sqlite',
			'data/eventMD-PEG28-cusumLevelAnalysis.sqlite',
			'data/.settings',
			'data/SingleChan-0001.qdf',
			'data/SingleChan-0001_state.txt',
			'commit-hash',
			'requirements.txt',
			'DISCLAIMER.TXT',
			'LICENSE.TXT'
			],
	install_requires=open('requirements.txt').read().splitlines(),
	url=mosaic.DocumentationURL,
	license='LICENSE.txt',
	description='A Modular Single-Molecule Analysis Interface.',
	long_description=open('README.rst').read(),
)