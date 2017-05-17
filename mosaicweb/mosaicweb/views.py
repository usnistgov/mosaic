from mosaicweb import app
from flask import send_file, make_response, jsonify, request

import mosaic
from mosaic.utilities.sqlQuery import query, rawQuery
from mosaic.utilities.analysis import caprate
from mosaic.utilities.resource_path import format_path
from mosaic.trajio.metaTrajIO import EmptyDataPipeError, FileNotFoundError
import mosaic.mdio.sqlite3MDIO as sqlite
import mosaic.settings as settings

from mosaicweb import __mosaicweb_version__, __mosaicweb_build__
from mosaicweb.mosaicAnalysis import mosaicAnalysis, analysisStatistics, analysisTimeSeries, analysisHistogram, analysisContour
from mosaicweb.sessionManager import sessionManager
from mosaicweb.utils.utils import gzipped

import pprint
import time
import random
import json
import glob
import os
import os.path
import logging
import numpy as np
from sqlite3 import OperationalError

class InvalidPOSTRequest(Exception):
	pass


logger=logging.getLogger()

gAnalysisSessions=sessionManager.sessionManager()
gStartTime=time.time()

@app.route("/")
def index():
	return send_file("templates/index.html")

@app.route('/about', methods=['POST'])
def about():
	return jsonify(ver=mosaic.__version__, build=mosaic.__build__, uiver=str(__mosaicweb_version__), uibuild=str(__mosaicweb_build__)), 200

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
@gzipped
def newAnalysis():
	global gAnalysisSessions

	try:
		defaultSettings=False
		params = dict(request.get_json())

		dataPath = params.get('dataPath', None)
		settingsString = params.get('settingsString', None)
		sessionID=params.get('sessionID', None)

		if dataPath and not settingsString:		# brand new session
			# print "brand new session: ", dataPath, settingsString, sessionID	
			sessionID=gAnalysisSessions.newSession()
			ma=mosaicAnalysis.mosaicAnalysis( format_path(mosaic.WebServerDataLocation+'/'+dataPath), sessionID) 

			gAnalysisSessions.addDataPath(sessionID, format_path(mosaic.WebServerDataLocation+'/'+dataPath) )
			gAnalysisSessions.addMOSAICAnalysisObject(sessionID, ma)
		elif sessionID and settingsString:	# update settings
			# print "update settings: ", dataPath, settingsString, sessionID
			ma=gAnalysisSessions.getSessionAttribute(sessionID, 'mosaicAnalysisObject')
			ma.updateSettings(settingsString)

			gAnalysisSessions.addSettingsString(sessionID, ma.analysisSettingsDict)
		elif sessionID and not settingsString:  # a session ID loaded from a route
			# print "session id from route: ", dataPath, settingsString, sessionID
			ma=gAnalysisSessions.getSessionAttribute(sessionID, 'mosaicAnalysisObject')
		else:
			raise InvalidPOSTRequest('An invalid POST request was received.')
		

		return jsonify(respondingURL='new-analysis', sessionID=sessionID, **ma.setupAnalysis() ), 200
	except EmptyDataPipeError, err:
		return jsonify( respondingURL='new-analysis', errType='EmptyDataPipeError', errSummary="End of data.", errText=str(err) ), 500
	except FileNotFoundError, err:
		return jsonify( respondingURL='new-analysis', errType='FileNotFoundError', errSummary="Files not found.", errText=str(err) ), 500
	except InvalidPOSTRequest, err:
		return jsonify( respondingURL='new-analysis', errType='InvalidPOSTRequest', errSummary="An invalid POST request was received.", errText=str(err) ), 500

@app.route('/load-analysis', methods=['POST'])
@gzipped
def loadAnalysis():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())
		db=params.get('databaseFile', None)

		databaseFile = format_path(mosaic.WebServerDataLocation+'/'+db )
		if not databaseFile:
			raise InvalidPOSTRequest("Missing required parameter 'databaseFile'")

		info, settings=_dbInfo(databaseFile)

		dataPath=info['datPath']

		sessionID=gAnalysisSessions.newSession()
		ma=mosaicAnalysis.mosaicAnalysis(dataPath, sessionID) 
		ma.updateSettings(settings)
		
		# ma.setupAnalysis()

		gAnalysisSessions.addDatabaseFile(sessionID, databaseFile)
		gAnalysisSessions.addAnalysisRunningFlag(sessionID, False)
		gAnalysisSessions.addDataPath(sessionID, dataPath)
		gAnalysisSessions.addMOSAICAnalysisObject(sessionID, ma)

		return jsonify(respondingURL='load-analysis', sessionID=sessionID ), 200
	except InvalidPOSTRequest, err:
		return jsonify( respondingURL='load-analysis', errType='InvalidPOSTRequest', errSummary="An invalid POST request was received.", errText=str(err) ), 500
	except BaseException, err:
		return jsonify( respondingURL='load-analysis', errType='UnknownError', errSummary="'{0}' is not a valid database file.".format(db), errText=str(err) ), 500

@app.route('/start-analysis', methods=['POST'])
def startAnalysis():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())
		sessionID=params['sessionID']
		session=gAnalysisSessions[sessionID]

		try:
			settingsString=params['settingsString'] 
			gAnalysisSessions.addSettingsString(sessionID, settingsString)
		except KeyError:
			pass

		ma=gAnalysisSessions.getSessionAttribute(sessionID, 'mosaicAnalysisObject')
		ma.updateSettings(settingsString)
		ma.runAnalysis()

		gAnalysisSessions.addDatabaseFile(sessionID, ma.dbFile)
		gAnalysisSessions.addAnalysisRunningFlag(sessionID, ma.analysisRunning)
		

		return jsonify( respondingURL="start-analysis", analysisRunning=ma.analysisRunning), 200
	except (sessionManager.SessionNotFoundError, KeyError):
		return jsonify( respondingURL='start-analysis', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500

@app.route('/stop-analysis', methods=['POST'])
def stopAnalysis():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())
		sessionID=params['sessionID']
		session=gAnalysisSessions[sessionID]

		ma=gAnalysisSessions.getSessionAttribute(sessionID, 'mosaicAnalysisObject')
		ma.stopAnalysis()

		gAnalysisSessions.addAnalysisRunningFlag(sessionID, ma.analysisRunning)

		return jsonify( respondingURL="stop-analysis", analysisRunning=ma.analysisRunning, newDataAvailable=True ), 200
	except (sessionManager.SessionNotFoundError, KeyError):
		return jsonify( respondingURL='stop-analysis', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500

@app.route('/analysis-results', methods=['POST'])
@gzipped
def analysisResults():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())
		sessionID=params['sessionID']
		qstr=params['query']
		bins=params['nBins']
		density=params.get('density', False)
		dbfile=gAnalysisSessions.getSessionAttribute(sessionID, 'databaseFile')

		ma=gAnalysisSessions.getSessionAttribute(sessionID, 'mosaicAnalysisObject')
		gAnalysisSessions.addAnalysisRunningFlag(sessionID, ma.analysisRunning)

		a=analysisHistogram.analysisHistogram(dbfile, qstr, bins, density)

		return jsonify( respondingURL="analysis-results", analysisRunning=ma.analysisRunning, **a.analysisHistogram() ), 200
	except sessionManager.SessionNotFoundError:
		return jsonify( respondingURL='analysis-results', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500
	except KeyError, err:
		return jsonify( respondingURL='analysis-results', errType='KeyError', errSummary="The key {0} was not found.".format(str(err)), errText="The key {0} was not found.".format(str(err)) ), 500
	except OperationalError, err:
		return jsonify( respondingURL='analysis-results', errType='OperationalError', errSummary="Syntax error: {0}".format(str(err)), errText="Syntax error: {0}".format(str(err)) ), 500


@app.route('/analysis-contour', methods=['POST'])
@gzipped
def analysisContourPlot():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())
		sessionID=params['sessionID']
		qstr=params['query']
		bins=params['nBins']
		showContours=params.get('showContours', True)
		dbfile=gAnalysisSessions.getSessionAttribute(sessionID, 'databaseFile')

		ma=gAnalysisSessions.getSessionAttribute(sessionID, 'mosaicAnalysisObject')
		gAnalysisSessions.addAnalysisRunningFlag(sessionID, ma.analysisRunning)

		a=analysisContour.analysisContour(dbfile, qstr, bins, showContours)

		return jsonify( respondingURL="analysis-contour", analysisRunning=ma.analysisRunning, **a.analysisContour() ), 200
	except sessionManager.SessionNotFoundError:
		return jsonify( respondingURL='analysis-contour', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500
	except KeyError, err:
		return jsonify( respondingURL='analysis-contour', errType='KeyError', errSummary="The key {0} was not found.".format(str(err)), errText="The key {0} was not found.".format(str(err)) ), 500
	except OperationalError, err:
		return jsonify( respondingURL='analysis-contour', errType='OperationalError', errSummary="Syntax error: {0}".format(str(err)), errText="Syntax error: {0}".format(str(err)) ), 500


@app.route('/analysis-statistics', methods=['POST'])
def analysisStats():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())
		
		sessionID=params['sessionID']
		dbfile=gAnalysisSessions.getSessionAttribute(sessionID, 'databaseFile')

		a=analysisStatistics.analysisStatistics(dbfile)

		return jsonify(respondingURL='analysis-statistics', **a.analysisStatistics()), 200
	except (sessionManager.SessionNotFoundError, KeyError):
		return jsonify( respondingURL='analysis-statistics', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500

@app.route('/analysis-log', methods=['POST'])
def analysisLog():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())
		
		sessionID=params['sessionID']
		dbfile=gAnalysisSessions.getSessionAttribute(sessionID, 'databaseFile')

		logstr=(rawQuery(dbfile, "select logstring from analysislog")[0][0]).replace(str(mosaic.WebServerDataLocation), "<Data Root>")

		return jsonify(respondingURL='analysis-log', logText=logstr), 200
	except (sessionManager.SessionNotFoundError, KeyError):
		return jsonify( respondingURL='analysis-statistics', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500

@app.route('/event-view', methods=['POST'])
# @gzipped
def eventView():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())

		sessionID=params['sessionID']
		eventNumber=params['eventNumber']
		dbfile=gAnalysisSessions.getSessionAttribute(sessionID, 'databaseFile')

		a=analysisTimeSeries.analysisTimeSeries(dbfile, eventNumber)

		return jsonify(respondingURL='event-view', **a.timeSeries()), 200
	except (sessionManager.SessionNotFoundError, KeyError), err:
		print err
		return jsonify( respondingURL='event-view', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500


@app.route('/poll-analysis-status', methods=['POST'])
def pollAnalysisStatus():
	global gStartTime

	if (time.time()-gStartTime)%10 < 5.0:
		return jsonify( respondingURL="poll-analysis-status", newDataAvailable=True ), 200
	else:
		return jsonify( respondingURL="poll-analysis-status", newDataAvailable=False ), 200

@app.route('/list-data-folders', methods=['POST'])
def listDataFolders():
	params = dict(request.get_json())

	level=params.get('level', 'Data Root')
	if level == 'Data Root':
		folder=mosaic.WebServerDataLocation
	else:
		folder=format_path(mosaic.WebServerDataLocation+'/'+level+'/')

	folderList=[]

	for item in sorted(glob.glob(folder+'/*')):
		itemAttr={}
		if os.path.isdir(item):
			itemAttr['name']=os.path.relpath(item, folder)
			itemAttr['relpath']=os.path.relpath(item, format_path(mosaic.WebServerDataLocation) )
			itemAttr['desc']=_folderDesc(item)
			itemAttr['modified']=time.strftime('%m/%d/%Y, %I:%M %p', time.localtime(os.path.getmtime(item)))

			folderList.append(itemAttr)

	return jsonify( respondingURL='list-data-folders', level=level+'/', fileData=folderList )

@app.route('/list-database-files', methods=['POST'])
def listDatabaseFiles():
	params = dict(request.get_json())

	level=params.get('level', 'Data Root')
	if level == 'Data Root':
		folder=mosaic.WebServerDataLocation
	else:
		folder=format_path(mosaic.WebServerDataLocation+'/'+level+'/')

	fileList=[]

	for item in sorted(glob.glob(folder+'/*')):
		itemAttr={}
		if os.path.isdir(item):
			itemAttr['name']=os.path.relpath(item, folder)
			itemAttr['relpath']=os.path.relpath(item, format_path(mosaic.WebServerDataLocation) )
			itemAttr['desc']=_folderDesc(item)
			itemAttr['modified']=time.strftime('%m/%d/%Y, %I:%M %p', time.localtime(os.path.getmtime(item)))

			fileList.append(itemAttr)
		else:
			if _fileExtension(item)==".sqlite":
				itemAttr['name']=os.path.relpath(item, folder)
				itemAttr['relpath']=os.path.relpath(item, format_path(mosaic.WebServerDataLocation) )
				itemAttr['desc']="SQLite database, {0}".format(_fileSize(item))
				itemAttr['modified']=time.strftime('%m/%d/%Y, %I:%M %p', time.localtime(os.path.getmtime(item)))

				fileList.append(itemAttr)

	return jsonify( respondingURL='list-database-files', level=level+'/', fileData=fileList )

def _folderDesc(item):
	nqdf = len(glob.glob(item+'/*.qdf'))
	nbin = len(glob.glob(item+'/*.bin'))+len(glob.glob(item+'/*.dat'))
	nabf = len(glob.glob(item+'/*.abf'))
	nsqlite = len(glob.glob(item+'/*.sqlite'))
	nfolders = len( [i for i in os.listdir(item) if os.path.isdir(item+'/'+i) ] )

	if nqdf > 0:
		returnString = "{0} QDF {1}".format(nqdf, _fileLabel(nqdf))
	elif nbin > 0:
		returnString = "{0} BIN {1}".format(nbin, _fileLabel(nbin))
	elif nabf > 0:
		returnString = "{0} ABF {1}".format(nabf, _fileLabel(nabf))
	elif nfolders==0:
		returnString = "No data {1}."
	else:
		returnString = "{0} {1}".format(nfolders, _fileLabel(nfolders, "sub-folder")) 

	if nsqlite>0:
		returnString="{0}, {1} SQLite {2}".format(returnString, nsqlite, _fileLabel(nsqlite, "database"))
	return returnString

def _fileExtension(fname):
	return os.path.splitext(fname)[1].lower()

def _fileSize(fname):
	sz=os.stat(fname).st_size

	for label in ['bytes', 'KB', 'MB', 'GB', 'TB']:
		if sz < 1024.0:
			return "{0} {1}".format(round(sz,1), label)
		sz/=1024.0

def _fileLabel(nitems, label="file"):
	if nitems>1:
		return "{0}s".format(label)
	else:
		return label

def _dbInfo(dbname):
	db=sqlite.sqlite3MDIO()
	db.openDB(dbname)

	info=db.readAnalysisInfo()
	settings=db.readSettings()
	
	db.closeDB()

	return info, settings
	