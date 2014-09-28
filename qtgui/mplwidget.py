from PyQt4.QtCore import *
from PyQt4.QtGui import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT #Agg #as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib import gridspec
import warnings

warnings.filterwarnings(action="ignore", category=UserWarning)

class NavigationToolbar( NavigationToolbar2QT ):
	picked=pyqtSignal(int,name='picked')

	def __init__(self, canvas, parent ):
		NavigationToolbar2QT.__init__(self,canvas,parent)
		self.clearButtons=[]
		# Search through existing buttons
		# next use for placement of custom button
		next=None
		for c in self.findChildren(QToolButton):
			if next is None:
				next=c
			# Don't want to see subplots and customize
			if str(c.text()) in ('Subplots','Customize','Forward', 'Back'):
				c.defaultAction().setVisible(False)
				continue
			# Need to keep track of pan and zoom buttons
			# Also grab toggled event to clear checked status of picker button
			# if str(c.text()) in ('Zoom', 'Pan'):
			# 	c.toggled.connect(self.clearPicker)
			# 	self.clearButtons.append(c)
			# 	next=None

	# 	# create custom button
	# 	pm=QPixmap(64,64)
	# 	# pm.fill(QApplication.palette().color(QPalette.Normal,QPalette.Button))
	# 	c = QColor(0)
	# 	c.setAlpha(0)
	# 	pm.fill( c )
	# 	painter=QPainter(pm)
	# 	# painter.fillRect(6,6,20,20,Qt.red)
	# 	painter.setBrush(Qt.black)
	# 	painter.setPen(Qt.black)
	# 	painter.drawPolygon( QPoint( 22, 22 ), QPoint( 22, 42 ),
 #                           QPoint( 42, 32 ), QPoint( 22, 22 ) )
	# 	# painter.fillRect(3,23,5,23,Qt.blue)
	# 	painter.end()
	# 	icon=QIcon(pm)
	# 	picker=QAction("Next",self)
	# 	picker.setIcon(icon)
	# 	picker.setCheckable(True)
	# 	picker.setToolTip("Load more time-series data")
	# 	self.picker = picker
	# 	button=QToolButton(self)
	# 	button.setDefaultAction(self.picker)

	# 	# Add it to the toolbar, and connect up event
	# 	self.insertWidget(next.defaultAction(),button)
	# 	picker.toggled.connect(self.pickerToggled)

	# 	# Grab the picked event from the canvas
	# 	canvas.mpl_connect('pick_event',self.canvasPicked)
	# 	canvas.mpl_connect('motion_notify_event',self.on_move)

	# def clearPicker( self, checked ):
	# 	if checked:
	# 		self.picker.setChecked(False)

	# def pickerToggled( self, checked ):
	# 	if checked:
	# 		for c in self.clearButtons:
	# 			c.defaultAction().setChecked(False)
	# 		self.set_message('Reject/use observation')

	# def canvasPicked( self, event ):
	# 	if self.picker.isChecked():
	# 		self.picked.emit(event.ind)

	# def on_move(self, event):
	# 	# get the x and y pixel coords
	# 	x, y = event.x, event.y


class MplCanvas(FigureCanvas):
	def __init__(self, nsubplots=1):
		self.dpi=100
			
		self.fig = Figure(dpi=self.dpi, tight_layout=True)
		if nsubplots==2:
			# self.fig, (self.ax, self.ax2) = plt.subplots(1,2, sharey=True)
			# self.fig.set_tight_layout(True)
			self.gs= gridspec.GridSpec(1, 2, width_ratios=[5, 1]) 
			self.gs.update(left=0.15, right=0.97, bottom=0.22, top=0.94, wspace=0.07)
			self.ax = self.fig.add_subplot(self.gs[0])
			self.ax2 = self.fig.add_subplot(self.gs[1], sharey=self.ax)
			self.ax.hold(False)
			self.ax2.hold(False)
		else:
			self.ax = self.fig.add_subplot(1,1,1)
			self.ax.hold(False)

		FigureCanvas.__init__(self, self.fig)

		FigureCanvas.setSizePolicy(self, 
				QSizePolicy.Expanding, 
				QSizePolicy.Expanding
			)

		FigureCanvas.updateGeometry(self)

class MplWidget(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

		self.canvas = MplCanvas()
		self.vbl = QVBoxLayout()
		self.vbl.addWidget(self.canvas)

		self.setLayout(self.vbl)

	def addToolbar(self):
		# self.vbl.addWidget( NavigationToolbar2QTAgg(self.canvas, self) )
		self.vbl.addWidget( NavigationToolbar(self.canvas, self) )

class MplWidget2(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

		self.canvas = MplCanvas(nsubplots=2)
		self.vbl = QVBoxLayout()
		self.vbl.addWidget(self.canvas)

		self.setLayout(self.vbl)

	def addToolbar(self):
		# self.vbl.addWidget( NavigationToolbar2QTAgg(self.canvas, self) )
		self.vbl.addWidget( NavigationToolbar(self.canvas, self) )


# warnings.resetwarnings()