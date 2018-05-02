
*Generate publication quality contour plots using the
mosaicscripts.plot.contour module.*

::

    :Created:   11/19/2015
    :Author:    Arvind Balijepalli <arvind.balijepalli@nist.gov>
    :License:   See LICENSE.TXT
    :ChangeLog:
        11/19/15        AB  Initial version

.. code:: python

    import matplotlib.pyplot as plt
    import mosaicscripts.plots.contour as contour
    from mosaic.utilities.sqlQuery import query

Plots are generated using the ``mosaicscripts.plots.contour_plot()``
function. See the `contour module <../mosaicscripts/plots/contour.py>`__
for additional details.

.. code:: python

    contour.contour_plot(
    					query(
    						"../data/eventMD-20150404-221533_MSA.sqlite",
    						"select BlockDepth, StateResTime from metadata where ProcessingStatus='normal' and BlockDepth > 0 and ResTime > 0.025"
    						),
    					x_range=[0.01, 0.26], 
    					y_range=[0.02, 0.06], 
    					bin_size=0.0085, 
    					contours=6, 
    					colormap=plt.get_cmap('Purples'),
    					img_interpolation='nearest',
    					xticks=[
    							(0.05, '0.05'),                
    							(0.1, '0.1'),
    							(0.15, '0.15'),
    							(0.2, '0.2')
    							],
    					yticks=[
    							(0.025, '25'),
    							(0.04, '40'),
    							(0.05, '50')
    							],
    					axes_type=['linear', 'log', 'linear'],
                        figname="contour.png",
    					colorbar_num_ticks=4,
    					cb_round_digits=-1,
    					min_count_pct=0.08, 	# Set bins with < 7% of max to 0,
    					xlabel=r"$<i>/<i_0>$",
    					ylabel=r"Residence Time ($\mu s$)"
    			)



.. image:: ContourPlots_files/ContourPlots_3_0.png


Plot styling can be controlled with custom colormaps. Examples are found
within the ``contour.gen_colormap()`` function. Calling this function
makes two additional colormaps (``mosaicBlue`` and ``mosaicOrange``)
available as seen below.

.. code:: python

    contour.gen_colormaps()

**Note:** The ``colormap`` argument is now uses ``Orange1`` as opposed
to ``Purples`` above.

.. code:: python

    contour.contour_plot(
    					query(
    						"../data/eventMD-20150404-221533_MSA.sqlite",
    						"select BlockDepth, StateResTime from metadata where ProcessingStatus='normal' and BlockDepth > 0 and ResTime > 0.025"
    						),
    					x_range=[0.01, 0.26], 
    					y_range=[0.02, 0.06], 
    					bin_size=0.0085, 
    					contours=6, 
    					colormap=plt.get_cmap('mosaicOrange'),
    					img_interpolation='nearest',
    					xticks=[
    							(0.05, '0.05'),                
    							(0.1, '0.1'),
    							(0.15, '0.15'),
    							(0.2, '0.2')
    							],
    					yticks=[
    							(0.025, '25'),
    							(0.04, '40'),
    							(0.05, '50')
    							],
    					axes_type=['linear', 'log','linear'],
                        figname="contour.png",
    					colorbar_num_ticks=4,
    					cb_round_digits=-1,
    					min_count_pct=0.08, 	# Set bins with < 7% of max to 0,
    					xlabel=r"$<i>/<i_0>$",
    					ylabel=r"Residence Time ($\mu s$)"
    			)



.. image:: ContourPlots_files/ContourPlots_7_0.png

