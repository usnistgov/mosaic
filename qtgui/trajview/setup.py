from setuptools import setup

APP = ['trajviewer.py']
OPTIONS = {'argv_emulation': True, 'includes': ['sip', 'PyQt4', 'PyQt4.QtCore', 'PyQt4.QtGui']}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)


