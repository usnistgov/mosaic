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
from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from  mosaic.utilities.resource_path import path_separator, resource_path

class updateService(object):
	def __init__(self):
		self.currentVersion=mosaic.__version__

		self.downloadFolder=tempfile.gettempdir()+path_separator()
		self.CHUNKSIZE=8192

	def CheckUpdate(self):
		if sys.platform.startswith('linux'):
			return False

		self._getUpdateInfo("https://pages.nist.gov/mosaic/version.json")
		
		
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
				return False
		except:
			return False

	def _downloadLink(self):
		if sys.platform.startswith('win'):
			return self._d(self.updateInfoDict["dl-w64"])
		elif sys.platform.startswith('darwin'):
			print self._d(self.updateInfoDict["dl-osx"])
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
						# print ""
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
			QtGui.QMessageBox.warning(None, "MOSAIC Download Error", "There was an error downloading the MOSAIC update.\n\n"+str(e), QtGui.QMessageBox.Ok)
			return False
		except:
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
		except:
			pass

	def _showUpdateAvailableDialog(self):
		"""
			Show a dialog if an update is available. Return True to perform an update, False to cancel
		"""
		version=self._d(self.updateInfoDict["version"])
		build=self._d(self.updateInfoDict["build"])
		changelog=self._d(self.updateInfoDict["changelog"])

		self.updateBox = QtGui.QMessageBox()
		self.updateBox.setIconPixmap( QtGui.QPixmap(resource_path("icons/icon_100px.png")).scaled(50,50) )

		self.updateBox.setText("A new version of MOSAIC is available.")
		self.updateBox.setInformativeText("Update to version {0} ({1})".format(version, build))
		self.updateBox.setWindowTitle("MOSAIC Update")
		self.updateBox.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.updateBox.setDetailedText(changelog)
		self.updateBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
		self.updateBox.setButtonText(QtGui.QMessageBox.Ok, "Download");
		self.updateBox.raise_()
		retval = self.updateBox.exec_()

		return retval==QtGui.QMessageBox.Ok
		
	def _d(self, enctxt):
		return base64.b64decode(enctxt)

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	u=updateService()	
	u.CheckUpdate()
