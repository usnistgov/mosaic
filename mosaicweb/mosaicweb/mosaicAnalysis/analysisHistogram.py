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
	def __init__(self, dbFile, qstr, bins):
		self.AnalysisDBFile = dbFile
		self.queryString=qstr
		self.numBins=bins

		self.responseDict={}

	def analysisHistogram(self):
		xlabel={
			"BlockDepth"	: "i/i<sub>0</sub>",
			"ResTime"		: "t (ms)"
		}[self.queryString.split('from')[0].split('select')[1].split()[0]]

		layout={}
		layout['xaxis']= { 'title': xlabel, 'type': 'linear' }
		layout['yaxis']= { 'title': 'counts', 'type': 'linear' }
		layout['paper_bgcolor']='rgba(0,0,0,0)'
		layout['plot_bgcolor']='rgba(0,0,0,0)'
		layout['margin']={'l':'50', 'r':'50', 't':'0', 'b':'50'}
		layout['showlegend']=False
		layout['autosize']=True

		ydat, xdat = self._hist()
		self.responseDict['data']=[plotlyWrapper.plotlyTrace(list(xdat), list(ydat), "Histogram")]
		self.responseDict['layout']=layout
		self.responseDict['options']={'displayLogo': False}

		return self.responseDict

	def _hist(self):
		q=query(
			self.AnalysisDBFile,
			self.queryString
		)
		x=np.hstack( np.hstack( np.array( q ) ) )
		
		return np.array(np.histogram(x, bins=self.numBins))

if __name__ == '__main__':
	import mosaic

	a=analysisHistogram(
			mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite",
			"select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.02",
			500
		)

	print a.analysisHistogram()