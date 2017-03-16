class InvalidTraceTypeError(Exception):
	pass

class InvalidLayoutTypeError(Exception):
	pass

class plotlyTrace(dict):
	def __init__(self, xdat, ydat, traceType):
		try:
			self['x']=xdat
			self['y']=ydat
			self.update(plotlyTrace.traceConfig[traceType])

		except KeyError, err:
			raise InvalidTraceTypeError("Trace type '{0}' is not valid.".format(traceType))

	traceConfig={
		"IonicCurrentTimeSeries" : {
										'mode': 'scatter', 
										'line': { 'color': 'rgb(40, 53, 147)', 'width': '1' }, 
										'name': 'ionic current'
									},
		"MeanIonicCurrent" : {
										'mode': 'scatter', 
										'line': { 'color': 'rgb(120, 120, 120)', 'width': '2', 'dash': 'dash' }, 
										'name': 'mean current'
							},
		"IonicCurrentThreshold" : {
										'mode': 'scatter', 
										'line': { 'color': 'rgb(255, 80, 77)', 'width': '2' }, 
										'name': 'ionic current threshold'
								}
	}

class plotlyLayout(dict):
	def __init__(self, layoutType):
		try:
			self['paper_bgcolor']='rgba(0,0,0,0)'
			self['plot_bgcolor']='rgba(0,0,0,0)'
			self['margin']={'l':'50', 'r':'50', 't':'0', 'b':'50'}
			self['showlegend']=False
			self['autosize']=True
			self['height']=300
			self['side']='right'
			
			self.update(plotlyLayout.layoutConfig[layoutType])
		except KeyError, err:
			raise InvalidLayoutTypeError("Layout type '{0}' is not valid.".format(layoutType))
	
	layoutConfig={
		"TimeSeriesLayout" : {
								"xaxis" : {
											"title": "t (s)", 
											"domain": "[0, 0.75]"
										},
								"yaxis" : {
											"title": "i (pA)"
										}

							}
	}
	

class plotlyOptions(dict):
	def __init__(self):
		self["displayLogo"]=False
