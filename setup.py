from distutils.core import setup

setup(
    name='pyEventAnalysis',
    version='0.1.0',
    author='Arvind Balijepalli',
    author_email='arvind.balijepalli@nist.gov',
    packages=['pyeventanalysis', 'pyeventanalysis.utest', 'pyeventanalysis.trajviewer','pyeventanalysis.qdf','pyeventanalysis.abf'],
    test_suite = 'pyeventanalysis.utest',
    scripts=['bin/analysis.py'],
    url='http://pypi.python.org/pypi/pyEventAnalysis/',
    license='LICENSE.txt',
    description='Useful towel-related stuff.',
    long_description=open('README.txt').read(),
)
