from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
	def __init__(self):
		self.dpi=100
		self.fig = Figure(dpi=self.dpi)
		
		self.ax = self.fig.add_subplot(111)
		self.ax.hold(False)

		FigureCanvas.__init__(self, self.fig)
		
		FigureCanvas.setSizePolicy(self, 
				QtGui.QSizePolicy.Expanding, 
				QtGui.QSizePolicy.Expanding
			)
		
		FigureCanvas.updateGeometry(self)

class MplWidget(QtGui.QWidget):
	def __init__(self, parent = None):
 		QtGui.QWidget.__init__(self, parent)

		self.canvas = MplCanvas()
		self.vbl = QtGui.QVBoxLayout()
		self.vbl.addWidget(self.canvas)
		self.vbl.addWidget( NavigationToolbar(self.canvas, None) )
		self.setLayout(self.vbl)
