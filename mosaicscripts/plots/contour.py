#!/usr/bin/env python
""" 
	Contour plot overlaid on top of an image.

	:Created:	11/11/2015
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		02/20/16 		AB 	Added an option to plot the z-axis on a log scale.
		02/05/16 		AB 	Add options to scale z-axis (histogram, density or scaled)
		01/10/15 		AB  Rename custom colormaps
		11/11/15		AB	Initial version
"""
# -*- coding: utf-8 -*-

import matplotlib
import numpy as np
import matplotlib.cm as cm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import mosaicscripts.plots.mplformat as mplformat
from matplotlib.colors import LogNorm

def contour_plot(dat2d, x_range, y_range, bin_size, contours, colormap, img_interpolation, **kwargs):
	"""
		Generate publication quality contour plots using the ```contour_plot``` function. The function expects a two-dimensional array of data (typically blockade depth and residence time) and several options as listed below:

		:Args:
			- `dat2d` : 			    2-D array with format [[x1,y1], [x2,y2], ... ... ... [xn,yn]]
			- `x_range` : 				list with min and max in X
			- `y_range` : 				list with min and max in Y
			- `bin_size` :				bin size
			- `contours` :				number of contours
			- `colormap` :				Colormap to use. Expects a colormap object. See http://matplotlib.org/examples/color/colormaps_reference.html.
			- `img_interpolation` :		interpolation to use for image
		
		:Keyword Args:
			- `zscale` : 				(optional) plot the probability density if set to `density` or scale to the max count if set to `unity`.
			- `xticks` :				(optional) specify ticks for the X-axis. List of format [ (tick, label), ...]
			- `yticks` :				(optional) specify ticks for the X-axis. List of format [ (tick, label), ...]
			- `figname` :				(optional) figure name if saving an image. File extension determines format.
			- `dpi` :					(optional) figure resolution
			- `colorbar_num_ticks` :	(optional) number of ticks in the colorbar
			- `cb_round_digits` :		(optional) round colorbar ticks to multiple of cb_round_digits. For example, -2 rounds to 100. See python docs.
			- `min_count_pct` :			(optional) set bins with < min_count_pct of the maximum to 0
			- `axes_type` :				(optional) set linear or log axis. Expects a list for X and Y. For example ['linear', 'log'].
			- `z_type` :				(optional) plot the image density on a 'linear' or 'log' scale. Default is 'linear'
	"""
	mplformat.update_rcParams()

	cmap = colormap # plt.get_cmap(colormap)

	try:
		ax=kwargs['axes_type']

		x_axes_type=ax[0]
		y_axes_type=ax[1]

		aspect='auto'
		zscale=kwargs.pop('zscale', 'None')
		if zscale=='density': 
			density = True
		else:
			density = False

		zt=kwargs.pop('z_type', 'linear')
		if zt=='linear':
			z_type=None
		else:
			z_type=LogNorm()

	except:
		x_axes_type='linear'
		y_axes_type='linear'
		aspect=(Y.max()-Y.min())/(X.max()-X.min())


	x1,y1=np.transpose(np.array(dat2d))

	if y_axes_type=='log':
		xedges = np.arange(np.log(y_range[0]), np.log(y_range[1]), 10*bin_size)
		y=np.log( np.hstack(np.array(y1)) )
	else:
		xedges = np.arange(y_range[0], y_range[1], bin_size)
		y=np.hstack(np.array(y1))

	if x_axes_type=='log':
		yedges = np.arange(np.log(x_range[0]), np.log(x_range[1]), 10*bin_size)
		x=np.log( np.hstack(np.array(x1)) )
	else:
		yedges = np.arange(x_range[0], x_range[1], bin_size)
		x=np.hstack(np.array(x1))

	if zscale=='unity':
		ZZ,xe,ye=np.histogram2d(y, x, bins=(xedges, yedges))
		Z=ZZ/ZZ.max()
	else:
		Z,xe,ye=np.histogram2d(y, x, bins=(xedges, yedges), normed=density)

	X, Y = np.meshgrid(ye[:-1], xe[:-1])

	lmin=kwargs.pop("min_count_pct", 0.0)*Z.max()
	lmax=Z.max()
	delta_l=Z.max()/float(contours)


	lowvals=Z<lmin
	Z[lowvals]=0

	plt.figure()

	levels = np.arange(lmin,lmax, delta_l)

	CS = plt.contour(X, Y, Z, 
			levels=levels,
			interpolation=img_interpolation, 
			colors='0.3',
			origin='lower',
			linewidths=1.25,
			extent=[X.min(), X.max(), Y.min(), Y.max()],
			norm=z_type
			)
	im = plt.imshow(Z, 
			interpolation='gaussian', 
			origin='lower', 
			extent=[X.min(), X.max(), Y.min(), Y.max()],
			cmap=cmap,
			norm=z_type
			)
	plt.axes().set_aspect(aspect=aspect)

	plt.axes().set_xlabel(kwargs.pop('xlabel',''))
	plt.axes().set_ylabel(kwargs.pop('ylabel',''))
	
	try:
			xt, xtl=np.transpose(np.array(kwargs['xticks']))
			plt.axes().set_xticks(xt.astype(np.float))
			plt.axes().set_xticklabels(xtl)

			yt, ytl=np.transpose(np.array(kwargs['yticks']))
			plt.axes().set_yticks(np.log(yt.astype(np.float)))
			plt.axes().set_yticklabels(ytl)
	except:
			raise


	try:
		roundn=kwargs.pop('cb_round_digits', -1)
		CBIticks=[round(d, roundn) for d in np.arange(0, Z.max()+(float(kwargs["colorbar_num_ticks"])-1), Z.max()/(float(kwargs["colorbar_num_ticks"])-1))]
	except:
		CBIticks=None

	CBI = plt.colorbar(im, 
		orientation='vertical', 
		shrink=0.8, 
		ticks=CBIticks,
		drawedges=False,
		spacing='proportional'
		)

	if CBIticks: CBI.ax.set_yticklabels(CBIticks)

	l, b, w, h = plt.gca().get_position().bounds
	ll, bb, ww, hh = CBI.ax.get_position().bounds
	CBI.ax.set_position([ll, b + 0.1*h, ww, h*0.8])

	try:
		if kwargs["figname"]:
			plt.savefig( 
				kwargs["figname"], 
				dpi=kwargs.pop("dpi", 600), 
				pad_inches=0,
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
	# plt.show()


def gen_cmap_alpha(segs):
		alpha=[]
		alpha.append((0,0.0,0.0))
		for s in np.arange(1/float(segs), 1, 1./float(segs)):
				alpha.append( (s, s, s+1./float(segs)) )
		alpha.append((1,1,1))
		return alpha

def gen_colormaps():
	# Make a couple custom colormaps
	cdict_Bl = {'red':   [(0., 0.3, 0.3),
					   (0.5, 0.3, 0.3),
					   (1.0, 0.3, 0.3)],

			 'green': [(0., 0.42, 0.42),
					   (0.5, 0.42, 0.42),
					   (1.0, 0.42, 0.42)],

			 'blue':  [(0., 0.78, 0.78),
					   (0.5, 0.78, 0.78),
					   (1.0, 0.78, 0.78)],

			 'alpha':  gen_cmap_alpha(2000)
			}  
	cdict_Or = {'red':   [(0., 0.95, 0.95),
					   (0.5, 0.95, 0.95),
					   (1.0, 0.95, 0.95)],

			 'green': [(0., 0.54, 0.54),
					   (0.5, 0.54, 0.54),
					   (1.0, 0.54, 0.54)],

			 'blue':  [(0., 0.1, 0.1),
					   (0.5, 0.1, 0.1),
					   (1.0, 0.1, 0.1)],

			 'alpha':  gen_cmap_alpha(1000)
			}

	mosBlue = matplotlib.colors.LinearSegmentedColormap('mosaicBlue', cdict_Bl)
	mosOrange = matplotlib.colors.LinearSegmentedColormap('mosaicOrange', cdict_Or)

	plt.register_cmap(cmap=mosBlue)
	plt.register_cmap(cmap=mosOrange)


