"""
	A module that queries analysis Histograms.

	:Created:	4/15/2017
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		4/15/17		AB 	Initial version
"""
from mosaic.utilities.sqlQuery import query, rawQuery
from mosaicweb.plotlyUtils import plotlyWrapper
import numpy as np

class analysisHistogram:
	"""
		A class that compiles MOSAIC analysis histograms.
	"""
	def __init__(self, dbFile, qstr, bins, density):
		self.AnalysisDBFile = dbFile
		self.queryString=qstr
		self.numBins=bins
		self.density=density

		self.responseDict={}

	def analysisHistogram(self):
		xlabeldict={
			"BlockDepth"	: "i/i<sub>0</sub>",
			"ResTime"		: "t (ms)"
		}
		xlabel=xlabeldict.pop(self.queryString.split('from')[0].split('select')[1].split()[0], self.queryString.split('from')[0].split('select')[1].split()[0])
		
		if self.density:
			ylabeldict={
				"BlockDepth"	: "rho",
				"ResTime"		: "rho (ms<sup>-1</sup>)"
			}
			ylabel=ylabeldict.pop(self.queryString.split('from')[0].split('select')[1].split()[0], "rho")
		else:
			ylabel="counts"

		layout={}
		layout['xaxis']= { 
						'title': xlabel, 
						'type': 'linear',
						"titlefont": {
										"family": 'Roboto, Helvetica',
										"size": '16',
										"color": '#7f7f7f'
									},
									"tickfont": {
										"family": 'Roboto, Helvetica',
										"size": '16',
										"color": '#7f7f7f'
									}
					}
		layout['yaxis']= {
						'title': ylabel,
						'type': 'linear',
						"titlefont": {
										"family": 'Roboto, Helvetica',
										"size": '16',
										"color": '#7f7f7f'
									},
									"tickfont": {
										"family": 'Roboto, Helvetica',
										"size": '16',
										"color": '#7f7f7f'
									}
					}
		layout['paper_bgcolor']='rgba(0,0,0,0)'
		layout['plot_bgcolor']='rgba(0,0,0,0)'
		layout['margin']={'l':'50', 'r':'50', 't':'0', 'b':'50'}
		layout['showlegend']="False"
		layout['autosize']="True"

		ydat, xdat = self._hist()
		self.responseDict['data']=[plotlyWrapper.plotlyTrace(xdat.tolist(), ydat.tolist(), "Histogram")]
		self.responseDict['layout']=layout
		self.responseDict['options']={'displayLogo': "False"}

		return self.responseDict

	def _hist(self):
		q=query(
			self.AnalysisDBFile,
			self.queryString
		)
		x=np.hstack( np.hstack( np.array( q ) ) )
		
		# xmin=np.max([0, np.min(x)])
		xmin=np.min(x)
		xmax=np.max(x)

		return np.array(np.histogram(x, bins=self.numBins, density=self.density), dtype=object)

if __name__ == '__main__':
	import mosaic

	a=analysisHistogram(
			mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite",
			"select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.02",
			500
		)

	print(a.analysisHistogram())