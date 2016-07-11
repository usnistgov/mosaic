"""
http://carsonfarmer.com/2009/07/syntax-highlighting-with-pyqt/
"""
import sys
import json
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from mosaic.utilities.resource_path import resource_path

class mosaicSyntaxHighlight( QSyntaxHighlighter ):
		def __init__( self, parent, rulefile ):
			super(QSyntaxHighlighter, self).__init__( parent )

			self.parent = parent

			self.highlightRules = []

			with open(rulefile,'r') as j:
				syn=json.loads(j.read())

			self.colors=syn["colors"]
			self.rules=syn["rules"]
	
			self.generateKeywordRules("keyword")
			self.generateKeywordRules("reservedClasses")

			self.generateRegexRules("assignmentOperator", self.rules["assignmentOperator"])
			self.generateRegexRules("delimiter", self.rules["delimiter"])
			self.generateRegexRules("specialConstant", self.rules["specialConstant"])
			self.generateRegexRules("boolean", self.rules["boolean"])
			self.generateRegexRules("number", self.rules["number"])
			self.generateRegexRules("comment", self.rules["comment"])
			self.generateRegexRules("string", "\".*\"")
			self.generateRegexRules("string", "\'.*\'")

		def generateKeywordRules(self, section):
			keyword = QTextCharFormat()
			brush = QBrush( self._colorvalue(self.colors[section]), Qt.SolidPattern )
			keyword.setForeground( brush )
			keywords = QStringList( eval(self.rules[section]) )

			if keywords==[]:
				return

			for word in keywords:
				pattern = QRegExp("\\b" + word + "\\b")
				rule = HighlightingRule( pattern, keyword )
				self.highlightRules.append( rule )

		def generateRegexRules(self, section, regexstr):
			if regexstr=="":
				return

			regex = QTextCharFormat()
			brush = QBrush( self._colorvalue(self.colors[section]), Qt.SolidPattern )
			pattern = QRegExp( regexstr )
			regex.setForeground( brush )
			rule = HighlightingRule( pattern, regex )
			self.highlightRules.append( rule )

		def highlightBlock( self, text ):
			for rule in self.highlightRules:
				expression = QRegExp( rule.pattern )
				index = expression.indexIn( text )
				while index >= 0:
					length = expression.matchedLength()
					self.setFormat( index, length, rule.format )
					index = text.indexOf( expression, index + length )
			self.setCurrentBlockState( 0 )

		def _colorvalue(self, colorstr):
			if colorstr.startswith('rgb'):
				return QColor(*self._parsergb(colorstr))
			else:
				return getattr(Qt, colorstr)

		def _parsergb(self, rgbstr):
			return [ int(color) for color in rgbstr.split('(')[1].split(')')[0].split(',') ]

class HighlightingRule():
	def __init__( self, pattern, format ):
		self.pattern = pattern
		self.format = format

class TextEditorApp( QMainWindow ):
	def __init__(self):
		super(QMainWindow, self).__init__()

		font = QFont()
		font.setFamily( "Monaco" )
		font.setPointSize( 14 )

		editor = QTextEdit()
		editor.setFont( font )
		
		mosaicSyntaxHighlight( editor, resource_path('mosaicgui/highlight-spec/json.json') )
		
		self.setCentralWidget( editor )
		self.setWindowTitle( "Syntax Highlighting Test" )


if __name__ == "__main__":  
	app = QApplication( sys.argv )
	window = TextEditorApp()
	window.show()
	window.raise_()

	sys.exit( app.exec_() )
