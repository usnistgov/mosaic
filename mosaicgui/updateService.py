"""
	A basic framework to check for MOSAIC updates.


	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
"""	
import sys
import os
import json
import base64
import urllib2
import mosaic
import tempfile
from PyQt4 import QtCore, uic
from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from docutils.core import publish_string
import mosaic.utilities.mosaicLogging as mlog
from  mosaic.utilities.resource_path import path_separator, resource_path


class MOSAICUpdateDialog(QtGui.QDialog):
	def __init__(self, parent = None):
		super(MOSAICUpdateDialog, self).__init__(parent)

		uic.loadUi(resource_path("MOSAICUpdate.ui"), self)
		
		self.mosaicIcon.setPixmap( QtGui.QPixmap(resource_path("icons/icon_100px.png")).scaled(75, 75) )

class MOSAICUpdateBox(QtGui.QMessageBox):
	    def __init__(self):
	        QtGui.QMessageBox.__init__(self)
	        self.setSizeGripEnabled(True)

	    def event(self, e):
	        result = QtGui.QMessageBox.event(self, e)

	        self.setMinimumHeight(0)
	        self.setMaximumHeight(16777215)
	        self.setMinimumWidth(0)
	        self.setMaximumWidth(16777215)
	        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

	        # textEdit = self.findChild(QtGui.QTextEdit)
	        # if textEdit != None :
	        #     textEdit.setMinimumHeight(0)
	        #     textEdit.setMaximumHeight(16777215)
	        #     textEdit.setMinimumWidth(0)
	        #     textEdit.setMaximumWidth(16777215)
	        #     textEdit.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

	        return result

class updateService(object):
	def __init__(self):
		self.currentVersion=mosaic.__version__

		self.logger=mlog.mosaicLogging().getLogger(__name__)

		self.downloadFolder=tempfile.gettempdir()+path_separator()
		self.CHUNKSIZE=8192

	def CheckUpdate(self):
		if sys.platform.startswith('linux'):
			self.logger.info("Update service not supported on Linux.")
			return False

		self._getUpdateInfo(mosaic.DocumentationURL+"/version.json")
		
		
		if self._checkUpdateAvailable():
			if self._showUpdateAvailableDialog():
				url=self._downloadLink()
				if self._downloadUpdateFile(url):
					self._openUpdateImage(url)
					return True

		return False


	def _checkUpdateAvailable(self):
		"""
			Check if a new update is available.  Return True if available, else False
		"""
		try:
			if self.currentVersion in eval(self._d(self.updateInfoDict["update-versions"])):
				return True
			else:
				self.logger.info("No updates available.")
				return False
		except BaseException, err:
			logger.exception(err)
			return False

	def _downloadLink(self):
		if sys.platform.startswith('win'):
			return self._d(self.updateInfoDict["dl-w64"])
		elif sys.platform.startswith('darwin'):
			return self._d(self.updateInfoDict["dl-osx"])
		else:
			return self._d(self.updateInfoDict["dl-source"])

	def _downloadUpdateFile(self, url):
		try:
			fHandle = urllib2.urlopen(url)
			fSize=int(fHandle.info().getheader('Content-Length').strip())
			fBytes=0

			progressDialog=QtGui.QProgressDialog("Downloading MOSAIC ...", "Cancel", fBytes, fSize)
			progressDialog.setFixedSize(350,100)
			progressDialog.setWindowModality(Qt.WindowModal)
         
			with open(self.downloadFolder+os.path.basename(url), "wb") as updateFile:
				while True:
					if progressDialog.wasCanceled():
						self.logger.info("The user canceled the MOSAIC update.")
						return False

					buf=fHandle.read(self.CHUNKSIZE)
					if not buf:
						break

					progressDialog.setValue(fBytes)
					fBytes+=self.CHUNKSIZE
					updateFile.write(buf)

			progressDialog.setValue(fSize)

			return True
		except urllib2.HTTPError, e:
			self.logger.error("There was an error downloading the MOSAIC update ({0}).".format(str(e)))
			QtGui.QMessageBox.warning(None, "MOSAIC Download Error", "There was an error downloading the MOSAIC update.\n\n"+str(e), QtGui.QMessageBox.Ok)
			return False
		except BaseException, e:
			self.logger.exception(e)
			return False

	def _openUpdateImage(self, url):
		if sys.platform.startswith('darwin'):
			os.system('hdiutil mount -autoopen {0}'.format(self.downloadFolder+os.path.basename(url)))
		elif sys.platform.startswith('win'):
			os.startfile(self.downloadFolder+os.path.basename(url))
			# os.system('explorer /select,{0}'.format(self.downloadFolder+os.path.basename(url))) 
		else:
			os.system('xdg-open "%s"' % self.downloadFolder+os.path.basename(url))
			# print "Downloaded to : ", self.downloadFolder+os.path.basename(url)

	def _getUpdateInfo(self, url):
		import pprint
		pp = pprint.PrettyPrinter(indent=4)

		try:
			req=urllib2.Request(url)
			streamHandler=urllib2.build_opener()
			stream=streamHandler.open(req)

			self.updateInfoDict=json.loads( self._d(stream.read()) )
		except BaseException, err:
			logger.exception(err)

	def _showUpdateAvailableDialog(self):
		"""
			Show a dialog if an update is available. Return True to perform an update, False to cancel
		"""
		version=self._d(self.updateInfoDict["version"])
		build=self._d(self.updateInfoDict["build"])
		changelog=self._d(self.updateInfoDict["changelog"])

		# self.updateBox = QtGui.QMessageBox()
		self.updateBox = MOSAICUpdateDialog()

		self.updateBox.informativeText.setText("Update to version {0} ({1})".format(version, build))
		self.updateBox.changelogTextEdit.setText( publish_string(changelog, writer_name='html') )
		
		# self.updateBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
		# self.updateBox.setButtonText(QtGui.QMessageBox.Ok, "Download");
		self.updateBox.show()
		self.updateBox.raise_()
		retval = self.updateBox.exec_()

		if not retval: self.logger.info("The user canceled the MOSAIC update.")

		return retval
		
	def _d(self, enctxt):
		return base64.b64decode(enctxt)


if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	u=updateService()	
	u.CheckUpdate()

	# dmw = MOSAICUpdateDialog()
	# dmw.show()
	# dmw.raise_()
	# sys.exit(app.exec_())
