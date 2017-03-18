from mosaicweb import app
from flask import send_file, make_response, jsonify, request
import mosaic
from mosaic.utilities.sqlQuery import query
from mosaic.utilities.analysis import caprate
from mosaicweb.mosaicAnalysis import mosaicAnalysis
from mosaic.trajio.metaTrajIO import EmptyDataPipeError, FileNotFoundError
import mosaic.settings as settings

import pprint
import time
import random
import json
import glob
import os
import logging
import numpy as np

logger=logging.getLogger()

@app.route("/")
def index():
    return send_file("templates/index.html")

@app.route('/about', methods=['POST'])
def about():
	return jsonify(ver=mosaic.__version__, build=mosaic.__build__, uiver='1.0.0', uibuild='58cbed0'), 200

@app.route('/histogram', methods=['POST'])
def histogram():
	_id=""
	_histscript=""
	params = dict(request.get_json())

	# time.sleep(3)
	return jsonify( respondingURL="histogram", **_histPlot() ), 200

@app.route('/validate-settings', methods=['POST'])
def validateSettings():
	try:
		params = dict(request.get_json())

		analysisSettings = params.get('analysisSettings', "")

		jsonSettings = json.loads(analysisSettings)

		return jsonify( respondingURL="validate-settings", status="OK" ), 200
	except ValueError, err:
		return jsonify( respondingURL="validate-settings", errType='ValueError', errSummary="Parse error", errText=str(err) ), 500

@app.route('/processing-algorithm', methods=['POST'])
def processingAlgorithm():
	try:
			defaultSettings=eval(settings.__settings__)
			params = dict(request.get_json())

			procAlgorithmSectionName=params["procAlgorithm"]

			return jsonify(
					respondingURL='processing-algorithm',
					procAlgorithmSectionName=procAlgorithmSectionName,
					procAlgorithm=defaultSettings[procAlgorithmSectionName]
				), 200
	except:
		return jsonify( respondingURL='processing-algorithm', errType='UnknownAlgorithmError', errSummary="Data Processing Algorithm not found.", errText="Data Processing Algorithm not found." ), 500

@app.route('/new-analysis', methods=['POST'])
def newAnalysis():
	try:
		defaultSettings=False
		params = dict(request.get_json())

		dataPath = mosaic.WebServerDataLocation+'/'+params.get('dataPath', '')

		try:
			s=json.loads(params['settingsString'])
		except KeyError, err:
			sObj=mosaic.settings.settings(dataPath)
			s=sObj.settingsDict
			defaultSettings=sObj.defaultSettingsLoaded

		# pp = pprint.PrettyPrinter(indent=4)
		# pp.pprint(s)
		blkSize=float(params.get('blockSize', -1))
		start=float(params.get('start', -1))
	
		ma=mosaicAnalysis.mosaicAnalysis(s, dataPath, defaultSettings)
		temp=ma.setupAnalysis() 

		return jsonify(respondingURL='new-analysis', **temp), 200
	except EmptyDataPipeError, err:
		return jsonify( respondingURL='new-analysis', errType='EmptyDataPipeError', errSummary="End of data.", errText=str(err) ), 500
	except FileNotFoundError, err:
		return jsonify( respondingURL='new-analysis', errType='FileNotFoundError', errSummary="Files not found.", errText=str(err) ), 500

@app.route('/list-data-folders', methods=['POST'])
def listDataFolders():
	params = dict(request.get_json())

	level=params.get('level', 'Data Root')
	if level == 'Data Root':
		folder=mosaic.WebServerDataLocation
	else:
		folder=mosaic.WebServerDataLocation+'/'+level+'/'

	folderList=[]

	for item in sorted(glob.glob(folder+'/*')):
		itemAttr={}
		if os.path.isdir(item):
			itemAttr['name']=os.path.relpath(item, folder)
			itemAttr['relpath']=os.path.relpath(item, mosaic.WebServerDataLocation)
			itemAttr['desc']=_folderDesc(item)
			itemAttr['modified']=time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(item)))

			folderList.append(itemAttr)

	return jsonify( respondingURL='list-data-folders', level=level+'/', dataFolders=folderList )

def _folderDesc(item):
	nqdf = len(glob.glob(item+'/*.qdf'))
	nbin = len(glob.glob(item+'/*.bin'))+len(glob.glob(item+'/*.dat'))
	nabf = len(glob.glob(item+'/*.abf'))
	nfolders = len( [i for i in os.listdir(item) if os.path.isdir(item+'/'+i) ] )

	if nqdf > 0:
		return "{0} QDF files".format(nqdf)
	elif nbin > 0:
		return "{0} BIN files".format(nbin)
	elif nabf > 0:
		return "{0} ABF files".format(nabf)
	elif nfolders==0:
		return "No data files."
	else:
		return "{0} sub-folders".format(nfolders) 

def _histPlot():
	q=query(
		mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite",
		"select BlockDepth from metadata where ProcessingStatus='normal' and ResTime > 0.02 and BlockDepth between 0.05 and 0.5"
	)
	x=np.hstack(np.array(q))
	c,b=np.array(np.histogram(x, bins=500))

	dat={}

	trace1={};
	trace1['x']=list(b)
	trace1['y']=list(c)
	trace1['mode']='lines'
	trace1['line']= { 'color': 'rgb(40, 53, 147)', 'width': '1.5' }
	trace1['name']= 'blockade depth'

	layout={}
	# layout['title']='Blockade Depth Histogram'
	layout['xaxis']= { 'title': '<i>/<i_0>', 'type': 'linear' }
	layout['yaxis']= { 'title': 'counts', 'type': 'linear' }
	layout['paper_bgcolor']='rgba(0,0,0,0)'
	layout['plot_bgcolor']='rgba(0,0,0,0)'
	layout['margin']={'l':'50', 'r':'50', 't':'0', 'b':'50'}
	layout['showlegend']=False
	layout['autosize']=True
	# layout['height']=250

	normalEvents, totalEvents=_eventStats()
	stats={}
	stats['eventsProcessed']=totalEvents
	stats['errorRate']=round(100.*(1-(normalEvents/float(totalEvents))), 1)
	stats['captureRate']=_caprate()

	dat['data']=[trace1]
	dat['layout']=layout
	dat['options']={'displayLogo': False}
	dat['stats']=stats

	return dat

def _caprate():
	q=query(
		mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite",
		"select AbsEventStart from metadata where ProcessingStatus='normal' order by AbsEventStart ASC"
	)
	return round(caprate(np.hstack(q))[0], 1)

def _eventStats():
	normalEvents=len(query(
		mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite",
		"select AbsEventStart from metadata where ProcessingStatus='normal' order by AbsEventStart ASC"
	))
	totalEvents=len(query(
		mosaic.WebServerDataLocation+"/m40_0916_RbClPEG/eventMD-20161208-130302.sqlite",
		"select ProcessingStatus from metadata"
	))

	return normalEvents, totalEvents
	