import matplotlib.pyplot as plt

def update_rcParams():
	fontlabel_size=16
	tick_size=16
	plt.rcParams.update(
		{
			'backend': 'wxAgg', 
			'lines.markersize' : 2, 
			# 'font-family': 'sans-serif',
			'font.sans-serif': 'Helvetica',
			'font.weight': 200,
			'axes.labelsize': fontlabel_size, 
			'text.fontsize': fontlabel_size, 
			'legend.fontsize': fontlabel_size, 
			'xtick.labelsize': tick_size, 
			'ytick.labelsize': tick_size, 
			'text.usetex': False, 
			'xtick.major.size': 10,
			'ytick.major.size': 10,
			'xtick.major.width': 1,
			'ytick.major.width': 1,
			'contour.negative_linestyle': 'solid'
		}
	)