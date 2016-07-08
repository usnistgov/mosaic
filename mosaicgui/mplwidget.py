import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import gridspec
import warnings

warnings.filterwarnings(action="ignore", category=UserWarning)

def update_rcParams():
	fontlabel_size=12
	tick_size=12

	matplotlib.rcParams.update(
		{
			'figure.facecolor' : 'white',	# #ECECEC
			'figure.autolayout' : True,
			'figure.dpi' : 100,
			'figure.subplot.wspace'  : 0.0,
			'figure.subplot.hspace'  : 0.0,
			'lines.markersize' : 1.5, 
			'axes.prop_cycle' : matplotlib.cycler(color=['#0072B2', '#DB5E00', 'k']),
			'font.family': 'sans-serif',
			'font.sans-serif': 'Helvetica',
			'font.weight': 200,
			'axes.labelsize': fontlabel_size,
			'axes.facecolor' : 'white', 
			'legend.fontsize': fontlabel_size, 
			'xtick.labelsize': tick_size, 
			'ytick.labelsize': tick_size, 
			'text.usetex': False, 
			'text.fontsize': fontlabel_size, 
			'xtick.major.size': 7.5,
			'ytick.major.size': 7.5,
			'xtick.major.width': 1,
			'ytick.major.width': 1,
			'contour.negative_linestyle': 'solid',
			'agg.path.chunksize' : 10000
		}
	)

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

class MplCanvas(FigureCanvas):
	def __init__(self, nsubplots=1):
		self.dpi=matplotlib.rcParams['figure.dpi']
			
		self.fig = Figure(dpi=self.dpi, tight_layout=True)
		if nsubplots==2:
			self.gs= gridspec.GridSpec(1, 2, width_ratios=[5, 1]) 
			self.gs.update(left=0.15, right=0.97, bottom=0.22, top=0.94, wspace=0.07)
			self.ax = self.fig.add_subplot(self.gs[0])
			self.ax2 = self.fig.add_subplot(self.gs[1], sharey=self.ax)
			self.ax.hold(False)
			self.ax2.hold(False)
		else:
			self.ax = self.fig.add_subplot(1,1,1)
			self.ax.hold(False)

		super(MplCanvas, self).__init__(self.fig)

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
		self.vbl.addWidget( NavigationToolbar(self.canvas, self) )

class MplWidget2(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)

		self.canvas = MplCanvas(nsubplots=2)
		self.vbl = QVBoxLayout()
		self.vbl.addWidget(self.canvas)

		self.setLayout(self.vbl)

	def addToolbar(self):
		self.vbl.addWidget( NavigationToolbar(self.canvas, self) )
