from mosaicweb import app
from flask import send_file, make_response, jsonify, request

import mosaic
from mosaic.utilities.sqlQuery import query, rawQuery
from mosaic.utilities.analysis import caprate
import mosaic.utilities.ga as ga
from mosaic.utilities.resource_path import format_path, path_separator
from mosaic.trajio.metaTrajIO import EmptyDataPipeError, FileNotFoundError
from mosaic.utilities.ga import registerLaunch, registerStart, registerStop
import mosaic.mdio.sqlite3MDIO as sqlite
import mosaic.settings as settings
import mosaic.utilities.mosaicLogging as mlog

from mosaicweb.mosaicAnalysis import mosaicAnalysis, analysisStatistics, analysisTimeSeries, analysisHistogram, analysisContour, analysisDBUtils
from mosaicweb.sessionManager import sessionManager
from mosaicweb.utils.utils import gzipped

import pprint
import tempfile
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

logger=logging.getLogger(name="mwebserver")

gAnalysisSessions=sessionManager.sessionManager()
gStartTime=time.time()

@app.route("/")
def index():
	return send_file("templates/index.html")

@app.route('/about', methods=['POST'])
def about():
	return jsonify(ver=mosaic.__version__, build=mosaic.__build__, uiver=str(mosaic.__mweb_version__)), 200

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
@registerLaunch("new_analysis_mweb")
def newAnalysis():
	global gAnalysisSessions
	# logger=mlog.mosaicLogging().getLogger(name=__name__)

	try:
		defaultSettings=False
		params = dict(request.get_json())

		dataPath = params.get('dataPath', None)
		settingsString = params.get('settingsString', None)
		sessionID=params.get('sessionID', None)

		if dataPath and not settingsString:		# brand new session
			# print "brand new session: ", dataPath, settingsString, sessionID	
			logger.info("/new-analysis: "+format_path(mosaic.WebServerDataLocation+'/'+dataPath))

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
@registerLaunch("load_analysis_mweb")
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
@registerStart("mweb")
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
		gAnalysisSessions.addAnalysisRunningFlag(sessionID, ma.analysisStatus)
		

		return jsonify( respondingURL="start-analysis", analysisRunning=ma.analysisStatus), 200
	except (sessionManager.SessionNotFoundError, KeyError):
		return jsonify( respondingURL='start-analysis', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500

@app.route('/stop-analysis', methods=['POST'])
@registerStop("mweb")
def stopAnalysis():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())
		sessionID=params['sessionID']
		session=gAnalysisSessions[sessionID]

		ma=gAnalysisSessions.getSessionAttribute(sessionID, 'mosaicAnalysisObject')
		ma.stopAnalysis()

		gAnalysisSessions.addAnalysisRunningFlag(sessionID, ma.analysisStatus)

		return jsonify( respondingURL="stop-analysis", analysisRunning=ma.analysisStatus, newDataAvailable=True ), 200
	except (sessionManager.SessionNotFoundError, KeyError):
		return jsonify( respondingURL='stop-analysis', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500

@app.route('/analysis-histogram', methods=['POST'])
@gzipped
def analysisHistogramPlot():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())
		sessionID=params['sessionID']
		qstr=params['query']
		bins=params['nBins']
		density=params.get('density', False)
		dbfile=gAnalysisSessions.getSessionAttribute(sessionID, 'databaseFile')

		ma=gAnalysisSessions.getSessionAttribute(sessionID, 'mosaicAnalysisObject')
		gAnalysisSessions.addAnalysisRunningFlag(sessionID, ma.analysisStatus)

		a=analysisHistogram.analysisHistogram(dbfile, qstr, bins, density)
		ah=a.analysisHistogram()

		return jsonify( respondingURL="analysis-results", analysisRunning=ma.analysisStatus, **ah ), 200
	except sessionManager.SessionNotFoundError:
		return jsonify( respondingURL='analysis-results', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500
	except KeyError, err:
		return jsonify( respondingURL='analysis-results', errType='KeyError', errSummary="The key {0} is not permitted.".format(str(err)), errText="The key {0} was not found.".format(str(err)) ), 500
	except OperationalError, err:
		return jsonify( respondingURL='analysis-results', errType='OperationalError', errSummary="Syntax error: {0}".format(str(err)), errText="Syntax error: {0}".format(str(err)) ), 500
	except BaseException, err:
		return jsonify( respondingURL='analysis-results', errType='UnknownError', errSummary="{0}".format(str(err)), errText="{0}".format(str(err)) ), 500

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
		gAnalysisSessions.addAnalysisRunningFlag(sessionID, ma.analysisStatus)

		a=analysisContour.analysisContour(dbfile, qstr, bins, showContours)

		return jsonify( respondingURL="analysis-contour", analysisRunning=ma.analysisStatus, **a.analysisContour() ), 200
	except sessionManager.SessionNotFoundError:
		return jsonify( respondingURL='analysis-contour', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500
	except KeyError, err:
		return jsonify( respondingURL='analysis-contour', errType='KeyError', errSummary="The key {0} was not found.".format(str(err)), errText="The key {0} was not found.".format(str(err)) ), 500
	except OperationalError, err:
		return jsonify( respondingURL='analysis-contour', errType='OperationalError', errSummary="Syntax error: {0}".format(str(err)), errText="Syntax error: {0}".format(str(err)) ), 500
	except analysisContour.QuerySyntaxError, err:
		return jsonify( respondingURL='analysis-contour', errType='QuerySyntaxError', errSummary="The submitted query is not allowed for contour plots.", errText="The submitted query is not allowed for contour plots." ), 500


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
@gzipped
def eventView():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())

		sessionID=params['sessionID']
		eventNumber=params['eventNumber']
		eventFilter=params.get('eventFilter', ['normal', 'warning', 'error'])

		dbfile=gAnalysisSessions.getSessionAttribute(sessionID, 'databaseFile')

		a=analysisTimeSeries.analysisTimeSeries(dbfile, eventNumber, eventFilter)

		return jsonify(respondingURL='event-view', **a.timeSeries()), 200
	except (sessionManager.SessionNotFoundError, KeyError), err:
		return jsonify( respondingURL='event-view', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500
	except analysisTimeSeries.EmptyEventFilterError:
		return jsonify( respondingURL='event-view', errType='EmptyEventFilterError', errSummary="At least one event type must be selected.", errText="At least one event type must be selected." ), 500
	except analysisTimeSeries.EndOfDataError:
		return jsonify( respondingURL='event-view', errType='EndOfDataError', errSummary="End of data stream.", errText="End of data stream." ), 500

@app.route('/analysis-database-csv', methods=['POST'])
@gzipped
def analysisDatabaseCSV():
	global gAnalysisSessions

	try:
		params = dict(request.get_json())

		sessionID=params['sessionID']
		dbfile=gAnalysisSessions.getSessionAttribute(sessionID, 'databaseFile')
		
		a=analysisDBUtils.analysisDBUtils(dbfile, "select * from metadata")

		return jsonify(respondingURL='analysis-database-csv', **a.csv()), 200
	except (sessionManager.SessionNotFoundError, KeyError), err:
		return jsonify( respondingURL='analysis-database-csv', errType='MissingSIDError', errSummary="A valid session ID was not found.", errText="A valid session ID was not found." ), 500


@app.route('/poll-analysis-status', methods=['POST'])
def pollAnalysisStatus():
	global gStartTime

	if (time.time()-gStartTime)%10 < 5.0:
		return jsonify( respondingURL="poll-analysis-status", newDataAvailable=True ), 200
	else:
		return jsonify( respondingURL="poll-analysis-status", newDataAvailable=False ), 200

@app.route('/list-data-folders', methods=['POST'])
def listDataFolders():
	# logger=mlog.mosaicLogging().getLogger(name=__name__)

	params = dict(request.get_json())

	level=params.get('level', 'Data Root')
	if level == 'Data Root':
		logger.info("/list-data-folders: "+format_path(mosaic.WebServerDataLocation))
		folder=mosaic.WebServerDataLocation
	else:
		logger.info("/list-data-folders: "+format_path(mosaic.WebServerDataLocation+'/'+level+'/'))
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

	return jsonify( respondingURL='list-data-folders', level=level+'/', fileData=folderList ), 200

@app.route('/list-database-files', methods=['POST'])
def listDatabaseFiles():
	# logger=mlog.mosaicLogging().getLogger(name=__name__)

	params = dict(request.get_json())

	level=params.get('level', 'Data Root')
	if level == 'Data Root':
		logger.info("/list-database-files: "+format_path(mosaic.WebServerDataLocation))
		folder=mosaic.WebServerDataLocation
	else:
		logger.info("/list-database-files: "+format_path(mosaic.WebServerDataLocation+'/'+level+'/'))
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

	return jsonify( respondingURL='list-database-files', level=level+'/', fileData=fileList ), 200

@app.route('/list-active-sessions', methods=['POST'])
def listActiveSessions():
	sessions={}

	for key in gAnalysisSessions.keys():
		sessions[key]={
			'dataPath': str(gAnalysisSessions.getSessionAttribute(key, 'dataPath')).split(path_separator())[-1],
			'analysisRunning': gAnalysisSessions.getSessionAttribute(key, 'analysisRunning'),
			'sessionCreateTime': time.strftime('%m/%d/%Y, %I:%M:%S %p', gAnalysisSessions.getSessionAttribute(key, 'sessionCreateTime'))
		}
	return jsonify( respondingURL='list-active-sessions', sessions=sessions ), 200

@app.route('/analytics', methods=['POST'])
def analytics():
	ga_cache=format_path(tempfile.gettempdir()+'/.ga')

	params = dict(request.get_json())
	appAnalytics=params.get("appAnalytics", -1)

	gac=ga._gaCredentialCache()
	if appAnalytics!=-1:
		gac["gaenable"]=str(appAnalytics)

	with open(ga_cache, "w") as g:
		g.write(json.dumps(gac))

	return jsonify( respondingURL="analytics", appAnalytics=0, showAnalyticsOptions=0), 200
	# return jsonify( respondingURL="analytics", appAnalytics=eval(gac["gaenable"]), showAnalyticsOptions=eval(gac["gauimode"])), 200

@app.route('/quit-local-server', methods=['POST'])
def quitLocalServer():
	logger.info("Received remote shutdown request.")
	
	_shutdownServer()

	return jsonify( respondingURL='quit-local-server' ), 200

def _shutdownServer():
	global gAnalysisSessions

	logger.info("Starting shutdown.")

	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('No servers found.')

	for k, s in gAnalysisSessions.iteritems():
		logger.info('Shutting down running analysis {0}'.format(k))
		if s['analysisRunning']:
			s['mosaicAnalysisObject'].stopAnalysis()
		

	logger.info("Shutdown complete.")
	func()

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
		returnString = "No data"
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
	