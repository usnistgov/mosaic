from distutils.core import setup

setup(
    name='pyEventAnalysis',
    version='0.1.0',
    author='Arvind Balijepalli',
    author_email='arvind.balijepalli@nist.gov',
    packages=['pyeventanalysis', 'pyeventanalysis.utest', 'pyeventanalysis.trajviewer'],
    scripts=['bin/analysis.py'],
    url='http://pypi.python.org/pypi/pyEventAnalysis/',
    license='LICENSE.txt',
    description='Useful towel-related stuff.',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy >= 1.8.1",
        "cython >= 0.20.1",
        "scipy >= 0.14.0",
        "pyzmq >= 14.3.0",
        "matplotlib >= 1.3.1",
        "lmfit >= 0.7.4",
        "uncertainties >= 2.4.6",
    ],
)