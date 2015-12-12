"""
	Plot an ionic current time-series.
	
	:Created:	11/19/2015
 	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:ChangeLog:
	.. line-block::
		12/12/15	AB	Generalized plot function to allow different data types
		11/19/15	AB	Initial version
"""
import mosaic.abfTrajIO as abf
import mosaic.qdfTrajIO as qdf
import mosaic.binTrajIO as bin
import mosaic.tsvTrajIO as tsv

import matplotlib.pyplot as plt
import numpy as np
import mosaicscripts.plots.mplformat as mplformat

data_types= {
	"abf" : [abf.abfTrajIO, "*.abf"],
	"qdf" : [qdf.qdfTrajIO, "*.qdf"],
	"bin" : [bin.binTrajIO, "*.bin"],
	"tsv" : [tsv.tsvTrajIO, "*.tsv"]
}
def PlotTimeseries(dir, data_type, t0, t1, Fs, **kwargs):
	"""
		Generate publication quality time-series plots. 

		dir:		directory containing data files
		data_type: 	One of "abf", "qdf", "bin" or "tsv".
		t0: 		start time.
		t1: 		end time.
		Fs: 		Sampling rate in Hz.
		labels:		Axes text labels. For example ```["t (s)", "-i (pA)"]``` for a current vs. time plot.
		data_args:	(optional) For "qdf", "bin" or "tsv", settings to read in data. See :ref:`settings-page` for details.
		axes: 		(optional) Show axes (Default: True)
		highlights:	(optional) Highlight segments of the time-series with a different style (Default: None). For example: 
				highlights=[
        				[[0.282, 0.293], {'color' : '#3F50A0', 'marker' : '.', 'markersize' : 0.1}],
        				[[0.584, 0.597], {'color' : '#D42324', 'marker' : '.', 'markersize' : 0.1}],
        				[[0.685, 0.695], {'color' : '#EB751A', 'marker' : '.', 'markersize' : 0.1}]
    				]
    			Highlight three events at specied location (arg 1: start, end) with specified styles.
		plotopts: 	(optional) Specify plot style. See http://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.plot for details.
	"""
	mplformat.update_rcParams()

	showAxes=kwargs.pop('axes', True)
	highlights=kwargs.pop('highlights', None)
	plotopts=kwargs.pop('plotopts', {})
	polarity=kwargs.pop('polarity', 1.0)
	data_args=kwargs.pop('data_args', {})

	[tsObj, tsFilter] = data_types[data_type]


	tsDat=tsObj(dirname=dir, filter=tsFilter, **data_args)
	t=tsDat.popdata(t0*Fs)
	plotdata=polarity*tsDat.popdata(int((t1-t0)*Fs))

	fig=plt.figure(facecolor='white')

	if not showAxes:
		ax=plt.axes(frameon=False)
		ax.axes.get_xaxis().set_visible(False)
		ax.axes.get_yaxis().set_visible(False)
		

	plt.plot( np.arange(0, t1-t0, 1/float(Fs)), plotdata, **plotopts )
	
	
	if highlights:
		for h in highlights:
			s=h[0][0]
			e=h[0][1]

			plt.plot( np.arange(s, e, 1/float(Fs)), plotdata[int(s*Fs):int(e*Fs)], **h[1] )

	if showAxes:
		labels=kwargs.pop("labels", ["", ""])
		plt.xlabel(labels[0])
		plt.ylabel(labels[1])

		# plt.axes().set_yticks( range(0, 200,50))
	
			
	plt.show()