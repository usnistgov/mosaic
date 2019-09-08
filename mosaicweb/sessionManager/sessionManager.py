"""
	A class that manages sessions from clients to the Flask server

	:Created:	3/24/2017
	:Author: 	Arvind Balijepalli <arvind.balijepalli@nist.gov>
	:License:	See LICENSE.TXT
	:ChangeLog:
	.. line-block::
		3/24/17		AB 	Initial version
"""
import uuid
import time

class SessionNotFoundError(Exception):
	pass
class AttributeNotFoundError(Exception):
	pass

class session(dict):
	def __init__(self, sid=''):
		self['sessionID']=sid
		self['sessionCreateTime']=time.localtime(time.time())
		self['analysisRunning']=False

	def __setitem__(self, key, val):
		if key=='sessionID':
			if val=='':
				v1=uuid.uuid4().hex
			else:
				v1=val
		elif key=='analysisRunning':
			if val==True:
				self['sessionRunStartTime']=time.localtime(time.time())
			v1=val
		else:
			v1=val

		dict.__setitem__(self, key, v1)

	def __getitem__(self, key):
		return dict.__getitem__(self, key)

	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).items():
			self[k] = v

class sessionManager(dict):
	def newSession(self):
		"""
			Setup a new session.

			:Parameters: 
				None
		"""
		sidObj=session()
		self[sidObj['sessionID']]=sidObj

		return sidObj['sessionID']

	def getSession(self, sid):
		"""
			Get an existing session object
		"""
		try:
			return self[sid]
		except KeyError:
			raise SessionNotFoundError("Session with id '{0}' was not found.".format(sid))

	def getSessionAttribute(self, sid, attrName):
		try:
			sobj=self[sid]
			try:
				return sobj[attrName]
			except KeyError:
				raise AttributeNotFoundError("Attribute '{0}' was not found.".format(attrName))
		except KeyError:
			raise SessionNotFoundError("Session with id '{0}' was not found.".format(sid))

	def addDataPath(self, sid, dataPath):
		self._addAttribute(sid, 'dataPath', dataPath)

	def addSettingsString(self, sid, settingsString):
		self._addAttribute(sid, 'settingsString', settingsString)

	def addDatabaseFile(self, sid, dbFile):
		self._addAttribute(sid, 'databaseFile', dbFile)

	def addAnalysisRunningFlag(self, sid, analysisRunningFlag):
		self._addAttribute(sid, 'analysisRunning', analysisRunningFlag)

	def addMOSAICAnalysisObject(self, sid, mosaicAnalysisObj):
		self._addAttribute(sid, 'mosaicAnalysisObject', mosaicAnalysisObj)

	def _addAttribute(self, sid, attrName, attr):
		try:
			self[sid][attrName]=attr
		except KeyError:
			raise SessionNotFoundError("Session with id '{0}' was not found.".format(sid))

if __name__ == '__main__':
	s=sessionManager()

	key=s.newSession()
	s.addDataPath(key, 'foo/bar')
	s.addSettingsString(key, '{}')
	s.addDatabaseFile(key, 'foo.sqlite')

	print(s.keys())
	print(s[key])
	s.addAnalysisRunningFlag(key, True)
	print(s.getSession(key))

	print(s.getSessionAttribute(s.keys()[0], 'dataPath'))
