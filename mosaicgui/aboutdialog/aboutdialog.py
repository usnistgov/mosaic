from __future__ import with_statement

import sys
from mosaic.utilities.resource_path import resource_path

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import Qt

css = """QLabel {
      color: black;
}"""


class AboutDialog(QtGui.QDialog):
	def __init__(self, parent = None):
		super(AboutDialog, self).__init__(parent)

		# uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)),"statisticsview.ui"), self)
		uic.loadUi(resource_path("aboutdialog.ui"), self)
		
		self.setWindowTitle("")
		self.iconLabel.setPixmap( QtGui.QPixmap(resource_path("icon.png")).scaled(100,100) )

		self._positionWindow()
		self._setVersion()

	def _setVersion(self):
		import mosaic

		self.versionLabel.setText( "Version " + mosaic.__version__ )

	def _positionWindow(self):
		"""
			Position settings window at the top left corner
		"""
		if sys.platform=='win32':
			self.setGeometry(38, 250, 300, 200)
		else:
			self.setGeometry(38, 250, 300, 200)
		
if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	dmw = AboutDialog()
	dmw.show()
	dmw.raise_()
	sys.exit(app.exec_())

