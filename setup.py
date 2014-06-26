from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    name='pyEventAnalysis',
    version='1.0.0a1',
    author='Arvind Balijepalli',
    author_email='arvind.balijepalli@nist.gov',
    packages=['pyeventanalysis', 'pyeventanalysis.utest', 'pyeventanalysis.trajviewer','pyeventanalysis.qdf','pyeventanalysis.abf'],
    scripts=['bin/analysis.py', 'dependencies/build-deps-sh', 'pyeventanalysis/utest/run-tests-sh', 'mathematica/nanoporeAnalysis.m', 'mathematica/Util.m', 'Makefile'],
    url='http://pypi.python.org/pypi/pyEventAnalysis/',
    license='LICENSE.txt',
    description='Nanopore analysis.',
    long_description=open('README.txt').read(),
    include_dirs=[numpy.get_include()],
)

#ext_modules = cythonize("pyeventanalysis/characterizeEvent.pyx"),
