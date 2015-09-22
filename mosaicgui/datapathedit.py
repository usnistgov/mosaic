"""
	ChangeLog:
		9/4/15		AB 	Initial version

"""
from PyQt4 import QtCore, QtGui
from mosaic.utilities.resource_path import format_path

class datapathedit(QtGui.QLineEdit):
	def __init__( self, parent ):
		super(datapathedit, self).__init__(parent)

		self.setDragEnabled(True)
		
	def dragEnterEvent( self, event ):
		data = event.mimeData()
		urls = data.urls()
		if ( urls and urls[0].scheme() == 'file' ):
			event.acceptProposedAction()

	def dragMoveEvent( self, event ):
		data = event.mimeData()
		urls = data.urls()
		if ( urls and urls[0].scheme() == 'file' ):
			event.acceptProposedAction()

	def dropEvent( self, event ):
		data = event.mimeData()
		urls = data.urls()
		if ( urls and urls[0].scheme() == 'file' ):
			# for some reason, this doubles up the intro slash
			filepath = str( format_path( urls[0].path()) )
			
			if filepath.endswith('.sqlite'):
				self.setText(filepath)
			

