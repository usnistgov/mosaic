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
		"NormalEvent" : {
										'mode': 'markers',
										'type': 'scatter', 
										'marker': { 'color': 'rgb(40, 53, 147)', 'size': '8' }, 
										'name': 'ionic current'
									},
		"NormalEventFit" : {
										'mode': 'scatter', 
										# 'line': { 'color': 'rgb(255, 80, 77)', 'width': '2'}
										'line': { 'color': 'rgb(255, 41, 41)', 'width': '2'}
										
									},
		"NormalEventStep" : {
										'mode': 'scatter',
										'line': { 'color': 'rgb(120, 120, 120)', 'width': '2', 'dash': 'dash' }
									},
		"ErrorEvent" : {
										'mode': 'markers',
										'type': 'scatter', 
										'marker': { 'color': 'rgb(255, 41, 41)', 'size': '8' }, 
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
			self['side']='right'
			
			self.update(plotlyLayout.layoutConfig[layoutType])
		except KeyError, err:
			raise InvalidLayoutTypeError("Layout type '{0}' is not valid.".format(layoutType))
	
	layoutConfig={
		"TimeSeriesLayout" : {
								"xaxis" : {
											"title": "t (s)", 
											"domain": "[0, 0.75]",
											"titlefont": {
												"family": 'Roboto, Helvetica',
												"size": 14,
												"color": '#7f7f7f'
											},
											"tickfont": {
												"family": 'Roboto, Helvetica',
												"size": 14,
												"color": '#7f7f7f'
											},
											"zerolinecolor": "rgba(0,0,0,0)"
										},
								"yaxis" : {
											"title": "|i| (pA)",
											"titlefont": {
												"family": 'Roboto, Helvetica',
												"size": 14,
												"color": '#7f7f7f'
											},
											"tickfont": {
												"family": 'Roboto, Helvetica',
												"size": 14,
												"color": '#7f7f7f'
											}
										},
								"height" : 350

							},
		"EventViewLayout" : {
								"xaxis" : {
											"title": "t (s)", 
											"titlefont": {
												"family": 'Roboto, Helvetica',
												"size": 14,
												"color": '#7f7f7f'
											},
											"tickfont": {
												"family": 'Roboto, Helvetica',
												"size": 14,
												"color": '#7f7f7f'
											},
											"zerolinecolor": "rgba(0,0,0,0)"
										},
								"yaxis" : {
											"title": "|i| (pA)",
											"titlefont": {
												"family": 'Roboto, Helvetica',
												"size": 14,
												"color": '#7f7f7f'
											},
											"tickfont": {
												"family": 'Roboto, Helvetica',
												"size": 14,
												"color": '#7f7f7f'
											}
										},
								"height" : 225,
								"width" : 400,
								"hovermode": "false"
							}
	}
	

class plotlyOptions(dict):
	def __init__(self):
		self["displayLogo"]=False
