#!/usr/bin/env python
""" 
	1-D Histogram plot.

	:Created:	12/13/2015
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		12/13/15		AB	Initial version
"""
# -*- coding: utf-8 -*-

import matplotlib
import numpy as np
import matplotlib.cm as cm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import mosaicscripts.plots.mplformat as mplformat



def histogram_plot(dat, nbins, x_range, **kwargs):
	"""
		Generate publication quality contour plots using the ```contour_plot``` function. The function expects a two-dimensional array of data (typically blockade depth and residence time) and several options as listed below:

		:Args:
			- `dat` : 			    2-D array with format [[x1,y1], [x2,y2], ... ... ... [xn,yn]]
			- `nbinx` :				number of bins.
			- `x_range` : 			list with min and max in X. If `None`, min and max values of the data set the range.
		
		:Keyword Args:
			- `density` :			(optional) If True, display the probability density function. Default is `False`
			- `color` :				(optional) Plot color. Default is `#4155A3`.
			- `fill_alpha` :		(optional) Fill transperancy. 0 turns off fill. Default is 0.25.
			- `xticks` :			(optional) specify ticks for the X-axis. List of format [ (tick, label), ...]
			- `yticks` :			(optional) specify ticks for the X-axis. List of format [ (tick, label), ...]
			- `figname` :			(optional) figure name if saving an image. File extension determines format.
			- `dpi` :				(optional) figure resolution.
			- `show` :				(optional) if True (default) call the show() function to display the plot.
			- `return_histogram` :	(optional) if True, return the histogram values and bins. Default is False.

			- `advanced_opts` :		(optional) a Python dictionary that supplies advanced plotting options. See `Matplotlib plot documentation 
<http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot>`_ for details.
	"""
	mplformat.update_rcParams()

	den=kwargs.pop('density', False)
	xticks=kwargs.pop( 'xticks', () )
	yticks=kwargs.pop( 'yticks', () )
	xlabel=kwargs.pop( 'xlabel', '' )
	ylabel=kwargs.pop( 'ylabel', '' )
	color=kwargs.pop( 'color', '#4155A3' )
	fill_alpha=kwargs.pop( 'fill_alpha', 0.25)
	show=kwargs.pop('show', False)
	return_histogram=kwargs.pop('return_histogram', False)
	advanced_opts=kwargs.pop( 'advanced_opts', {} )

	plotopts={'color': color}
	plotopts.update( advanced_opts )


	x=np.hstack(np.array(dat))

	h, bins=np.histogram(x, bins=nbins, range=x_range, density=den)

	plt.plot(bins[:-1], h, **plotopts)	
	plt.fill_between(bins[:-1], 0, h, facecolor=color, alpha=fill_alpha )
	plt.xlabel( xlabel )
	plt.ylabel( ylabel )

	plt.xticks( xticks )
	plt.yticks( yticks )

	try:
		plt.savefig( 
			kwargs["figname"], 
			dpi=kwargs.pop("dpi", 600), 
			pad_inches=0.2,
			facecolor='w', 
			edgecolor='w',
			orientation='portrait', 
			papertype=None, 
			format=None,
			transparent=False,
			box_inches=None
		)
	except:
		pass

	if show:
		plt.show()


	if return_histogram:
		return h, bins[:-1]
