"""
	A collection of functions that support ABF1 and ABF2 file formats in gap-free mode and for
	single channels.

	This code is heavily adapted from the Neo project (http://neuralensemble.org/trac/neo)

	Author: Arvind Balijepalli
	Created: 5/23/2013

	ChangeLog:
		7/28/14 	AB 	Included support for mode 5 (event driven fixed length)
		5/23/13		AB	Initial version
"""
import struct
from numpy import *
from numpy import memmap
import re
import datetime

class struct_file(file):
	def read_f(self, format , offset = None):
		if offset is not None:
			self.seek(offset)
		return struct.unpack(format , self.read(struct.calcsize(format)))

	def write_f(self, format , offset = None , *args ):
		if offset is not None:
			self.seek(offset)
		self.write( struct.pack( format , *args ) )

class InvalidModeError(Exception):
	pass
class MultipleChannelError(Exception):
	pass


def abfload_gp(filename):
	header = read_header(filename)
	version = header['fFileVersionNumber']

	bandwidth=0
	gain=0

	# file format
	if header['nDataFormat'] == 0 :
		dt = dtype('i2')
	elif header['nDataFormat'] == 1 :
		dt = dtype('f4')
	
	if version <2. :
		nbchannel = header['nADCNumChannels']
		nbepisod = header['lSynchArraySize']
		headOffset = header['lDataSectionPtr']*BLOCKSIZE+header['nNumPointsIgnored']*dt.itemsize
		totalsize = header['lActualAcqLength']
		if nbchannel == 1:
			if header['nTelegraphEnable'][0]:
				try:
					gain = header['fTelegraphAdditGain'][0]
					bandwidth = header['fTelegraphFilter'][0]
				except KeyError:
					bandwidth=0
					gain=0
	elif version >=2. :
		nbchannel = header['sections']['ADCSection']['llNumEntries']
		headOffset = header['sections']['DataSection']['uBlockIndex']*BLOCKSIZE
		nbepisod = header['sections']['SynchArraySection']['llNumEntries']
		totalsize = header['sections']['DataSection']['llNumEntries']
		if nbchannel == 1:
			if header['listADCInfo'][0]['nTelegraphEnable']:
				try:
					gain = header['listADCInfo'][0]['fTelegraphAdditGain']
					bandwidth = header['listADCInfo'][0]['fTelegraphFilter']
				except KeyError:
					bandwidth=0
					gain=0

	data = memmap(filename , dt  , 'r', shape = (totalsize,) , offset = headOffset)

	# Check file mode. Only gapfree mode (3) is supported
	if version <2. :
		mode = header['nOperationMode']
	elif version >=2. :
		mode = header['protocol']['nOperationMode']

	# print mode, nbchannel, nbepisod, bandwidth, gain
	# for k,v in header.iteritems():
	# 	print k, '=', v

	# Check for either gap free or event driven fixed-length modes
	if mode not in [3, 5]:
		raise InvalidModeError("Only gap-free (3) and event driven fixed length (5) modes are currently supported")
	if nbchannel != 1:
		raise MultipleChannelError('Data from more than one channel is not currently supported')

	# gap free mode
	m = data.size%nbchannel
	if m != 0 : data = data[:-m]
	data = data.reshape( (data.size/nbchannel, nbchannel)).astype('f')
	if dt == dtype('i2'):
		if version <2. :
			reformat_integer_V1(data, nbchannel , header)
		elif version >=2. :
			reformat_integer_V2(data, nbchannel , header)                

	# save the sampling frequency separately
	if version <2. :
		freq = 1./(header['fADCSampleInterval']*nbchannel*1.e-6)
	elif version >=2. :
		freq = 1.e6/header['protocol']['fADCSequenceInterval']

	return [freq, header['fFileSignature'], bandwidth, gain, data[:,0]]

def read_header(filename):
	"""
	read the header of the file
	
	The startegy differ here from the orignal script under Matlab.
	In the original script for ABF2, it complete the header with informations
	that are located in other strutures.
	
	In ABF2 this function return header with sub dict :
		listADCInfo
		protocole
		tags
	that contain more information.
	"""
	fid = struct_file(filename,'rb')
	
	# version
	fFileSignature =  fid.read(4)
	if fFileSignature == 'ABF ' :
		headerDescription = headerDescriptionV1
	elif fFileSignature == 'ABF2' :
		headerDescription = headerDescriptionV2
	else :
		return None
		
	# construct dict
	header = { }
	for key, offset , format in headerDescription :
		val = fid.read_f(format , offset = offset)
		if len(val) == 1:
			header[key] = val[0]
		else :
			header[key] = array(val)
	
	# correction of version number and starttime
	if fFileSignature == 'ABF ' :
		header['lFileStartTime'] =  header['lFileStartTime'] +  header['nFileStartMillisecs']*.001
	elif fFileSignature == 'ABF2' :
		n = header['fFileVersionNumber']
		header['fFileVersionNumber'] = n[3]+0.1*n[2]+0.01*n[1]+0.001*n[0]
		header['lFileStartTime'] = header['uFileStartTimeMS']*.001
	
	if header['fFileVersionNumber'] < 2. :
		# tags
		listTag = [ ]
		for i in range(header['lNumTagEntries']) :
			fid.seek(header['lTagSectionPtr']+i*64)
			tag = { }
			for key, format in TagInfoDescription :
				val = fid.read_f(format )
				if len(val) == 1:
					tag[key] = val[0]
				else :
					tag[key] = array(val)
			listTag.append(tag)
		header['listTag'] = listTag
	
	elif header['fFileVersionNumber'] >= 2. :
		# in abf2 some info are in other place
		
		# sections 
		sections = { }
		for s,sectionName in enumerate(sectionNames) :
			uBlockIndex,uBytes,llNumEntries= fid.read_f( 'IIl' , offset = 76 + s * 16 )
			sections[sectionName] = { }
			sections[sectionName]['uBlockIndex'] = uBlockIndex
			sections[sectionName]['uBytes'] = uBytes
			sections[sectionName]['llNumEntries'] = llNumEntries
		header['sections'] = sections
		
		
		# strings sections
		# hack for reading channels names and units
		fid.seek(sections['StringsSection']['uBlockIndex']*BLOCKSIZE)
		bigString = fid.read(sections['StringsSection']['uBytes'])
		goodstart = bigString.lower().find('clampex')
		if goodstart == -1 :
			goodstart = bigString.lower().find('axoscope')
		
		bigString = bigString[goodstart:]
		strings = bigString.split('\x00')
		
		
		# ADC sections
		header['listADCInfo'] = [ ]
		for i in range(sections['ADCSection']['llNumEntries']) :
			#  read ADCInfo
			fid.seek(sections['ADCSection']['uBlockIndex']*\
						BLOCKSIZE+sections['ADCSection']['uBytes']*i)
			ADCInfo = { }
			for key, format in ADCInfoDescription :
				val = fid.read_f(format )
				if len(val) == 1:
					ADCInfo[key] = val[0]
				else :
					ADCInfo[key] = array(val)
			ADCInfo['recChNames'] = strings[ADCInfo['lADCChannelNameIndex']-1]
			ADCInfo['recChUnits'] = strings[ADCInfo['lADCUnitsIndex']-1]
			
			header['listADCInfo'].append( ADCInfo )
	
		# protocol sections
		protocol = { }
		fid.seek(sections['ProtocolSection']['uBlockIndex']*BLOCKSIZE)
		for key, format in protocolInfoDescription :
			val = fid.read_f(format )
			if len(val) == 1:
				protocol[key] = val[0]
			else :
				protocol[key] = array(val)
		header['protocol'] = protocol
		
		# tags
		listTag = [ ]
		for i in range(sections['TagSection']['llNumEntries']) :
			fid.seek(sections['TagSection']['uBlockIndex']*\
						BLOCKSIZE+sections['TagSection']['uBytes']*i)
			tag = { }
			for key, format in TagInfoDescription :
				val = fid.read_f(format )
				if len(val) == 1:
					tag[key] = val[0]
				else :
					tag[key] = array(val)
			listTag.append(tag)
			
		header['listTag'] = listTag
			
		
	fid.close()
	
	return header

def reformat_integer_V1(data, nbchannel , header):
	"""
	reformat when dtype is int16 for ABF version 1
	"""
	for i in range(nbchannel):
		data[:,i] /= header['fInstrumentScaleFactor'][i]
		data[:,i] /= header['fSignalGain'][i]
		data[:,i] /= header['fADCProgrammableGain'][i]
		if header['nTelegraphEnable'][i] :
			data[:,i] /= header['fTelegraphAdditGain'][i]
		data[:,i] *= header['fADCRange']
		data[:,i] /= header['lADCResolution']
		data[:,i] += header['fInstrumentOffset'][i]
		data[:,i] -= header['fSignalOffset'][i]
	
def reformat_integer_V2(data, nbchannel , header):
	"""
	reformat when dtype is int16 for ABF version 2
	"""
	for i in range(nbchannel):
		data[:,i] /= header['listADCInfo'][i]['fInstrumentScaleFactor']
		data[:,i] /= header['listADCInfo'][i]['fSignalGain']
		data[:,i] /= header['listADCInfo'][i]['fADCProgrammableGain']
		if header['listADCInfo'][i]['nTelegraphEnable'] :
			data[:,i] /= header['listADCInfo'][i]['fTelegraphAdditGain']
		data[:,i] *= header['protocol']['fADCRange']
		data[:,i] /= header['protocol']['lADCResolution']
		data[:,i] += header['listADCInfo'][i]['fInstrumentOffset']
		data[:,i] -= header['listADCInfo'][i]['fSignalOffset']

BLOCKSIZE = 512

headerDescriptionV1= [
		 ('fFileSignature',0,'4s'),
		 ('fFileVersionNumber',4,'f' ),
		 ('nOperationMode',8,'h' ),
		 ('lActualAcqLength',10,'i' ),
		 ('nNumPointsIgnored',14,'h' ),
		 ('lActualEpisodes',16,'i' ),
		 ('lFileStartTime',24,'i' ),
		 ('lDataSectionPtr',40,'i' ),
		 ('lTagSectionPtr',44,'i' ),
		 ('lNumTagEntries',48,'i' ),
		 ('lSynchArrayPtr',92,'i' ),
		 ('lSynchArraySize',96,'i' ),
		 ('nDataFormat',100,'h' ),
		 ('nADCNumChannels', 120, 'h'),
		 ('fADCSampleInterval',122,'f'),
		 ('fSynchTimeUnit',130,'f' ),
		 ('lNumSamplesPerEpisode',138,'i' ),
		 ('lPreTriggerSamples',142,'i' ),
		 ('lEpisodesPerRun',146,'i' ),
		 ('fADCRange', 244, 'f' ),
		 ('lADCResolution', 252, 'i'),
		 ('nFileStartMillisecs', 366, 'h'),
		 ('nADCPtoLChannelMap', 378, '16h'),
		 ('nADCSamplingSeq', 410, '16h'),
		 ('sADCChannelName',442, '10s'*16),
		 ('sADCUnits',602, '8s'*16) ,
		 ('fADCProgrammableGain', 730, '16f'),
		 ('fInstrumentScaleFactor', 922, '16f'),
		 ('fInstrumentOffset', 986, '16f'),
		 ('fSignalGain', 1050, '16f'),
		 ('fSignalOffset', 1114, '16f'),
		 ('nTelegraphEnable',4512, '16h'),
		 ('fTelegraphAdditGain',4576,'16f'),
		 ]


headerDescriptionV2 =[
		 ('fFileSignature',0,'4s' ),
		 ('fFileVersionNumber',4,'4b') , 
		 ('uFileInfoSize',8,'I' ) ,
		 ('lActualEpisodes',12,'I' ) ,
		 ('uFileStartDate',16,'I' ) ,
		 ('uFileStartTimeMS',20,'I' ) ,
		 ('uStopwatchTime',24,'I' ) ,
		 ('nFileType',28,'H' ) ,
		 ('nDataFormat',30,'H' ) ,
		 ('nSimultaneousScan',32,'H' ) ,
		 ('nCRCEnable',34,'H' ) ,
		 ('uFileCRC',36,'I' ) ,
		 ('FileGUID',40,'I' ) ,
		 ('uCreatorVersion',56,'I' ) ,
		 ('uCreatorNameIndex',60,'I' ) ,
		 ('uModifierVersion',64,'I' ) ,
		 ('uModifierNameIndex',68,'I' ) ,
		 ('uProtocolPathIndex',72,'I' ) ,
		 ]


sectionNames= ['ProtocolSection',
			 'ADCSection',
			 'DACSection',
			 'EpochSection',
			 'ADCPerDACSection',
			 'EpochPerDACSection',
			 'UserListSection',
			 'StatsRegionSection',
			 'MathSection',
			 'StringsSection',
			 'DataSection',
			 'TagSection',
			 'ScopeSection',
			 'DeltaSection',
			 'VoiceTagSection',
			 'SynchArraySection',
			 'AnnotationSection',
			 'StatsSection',
			 ]


protocolInfoDescription = [
		 ('nOperationMode','h'),
		 ('fADCSequenceInterval','f'),
		 ('bEnableFileCompression','b'),
		 ('sUnused1','3s'),
		 ('uFileCompressionRatio','I'),
		 ('fSynchTimeUnit','f'),
		 ('fSecondsPerRun','f'),
		 ('lNumSamplesPerEpisode','i'),
		 ('lPreTriggerSamples','i'),
		 ('lEpisodesPerRun','i'),
		 ('lRunsPerTrial','i'),
		 ('lNumberOfTrials','i'),
		 ('nAveragingMode','h'),
		 ('nUndoRunCount','h'),
		 ('nFirstEpisodeInRun','h'),
		 ('fTriggerThreshold','f'),
		 ('nTriggerSource','h'),
		 ('nTriggerAction','h'),
		 ('nTriggerPolarity','h'),
		 ('fScopeOutputInterval','f'),
		 ('fEpisodeStartToStart','f'),
		 ('fRunStartToStart','f'),
		 ('lAverageCount','i'),
		 ('fTrialStartToStart','f'),
		 ('nAutoTriggerStrategy','h'),
		 ('fFirstRunDelayS','f'),
		 ('nChannelStatsStrategy','h'),
		 ('lSamplesPerTrace','i'),
		 ('lStartDisplayNum','i'),
		 ('lFinishDisplayNum','i'),
		 ('nShowPNRawData','h'),
		 ('fStatisticsPeriod','f'),
		 ('lStatisticsMeasurements','i'),
		 ('nStatisticsSaveStrategy','h'),
		 ('fADCRange','f'),
		 ('fDACRange','f'),
		 ('lADCResolution','i'),
		 ('lDACResolution','i'),
		 ('nExperimentType','h'),
		 ('nManualInfoStrategy','h'),
		 ('nCommentsEnable','h'),
		 ('lFileCommentIndex','i'),
		 ('nAutoAnalyseEnable','h'),
		 ('nSignalType','h'),
		 ('nDigitalEnable','h'),
		 ('nActiveDACChannel','h'),
		 ('nDigitalHolding','h'),
		 ('nDigitalInterEpisode','h'),
		 ('nDigitalDACChannel','h'),
		 ('nDigitalTrainActiveLogic','h'),
		 ('nStatsEnable','h'),
		 ('nStatisticsClearStrategy','h'),
		 ('nLevelHysteresis','h'),
		 ('lTimeHysteresis','i'),
		 ('nAllowExternalTags','h'),
		 ('nAverageAlgorithm','h'),
		 ('fAverageWeighting','f'),
		 ('nUndoPromptStrategy','h'),
		 ('nTrialTriggerSource','h'),
		 ('nStatisticsDisplayStrategy','h'),
		 ('nExternalTagType','h'),
		 ('nScopeTriggerOut','h'),
		 ('nLTPType','h'),
		 ('nAlternateDACOutputState','h'),
		 ('nAlternateDigitalOutputState','h'),
		 ('fCellID','3f'),
		 ('nDigitizerADCs','h'),
		 ('nDigitizerDACs','h'),
		 ('nDigitizerTotalDigitalOuts','h'),
		 ('nDigitizerSynchDigitalOuts','h'),
		 ('nDigitizerType','h'),
		 ]


ADCInfoDescription = [
		 ('nADCNum','h'),
		 ('nTelegraphEnable','h'),
		 ('nTelegraphInstrument','h'),
		 ('fTelegraphAdditGain','f'),
		 ('fTelegraphFilter','f'),
		 ('fTelegraphMembraneCap','f'),
		 ('nTelegraphMode','h'),
		 ('fTelegraphAccessResistance','f'),
		 ('nADCPtoLChannelMap','h'),
		 ('nADCSamplingSeq','h'),
		 ('fADCProgrammableGain','f'),
		 ('fADCDisplayAmplification','f'),
		 ('fADCDisplayOffset','f'),
		 ('fInstrumentScaleFactor','f'),
		 ('fInstrumentOffset','f'),
		 ('fSignalGain','f'),
		 ('fSignalOffset','f'),
		 ('fSignalLowpassFilter','f'),
		 ('fSignalHighpassFilter','f'),
		 ('nLowpassFilterType','b'),
		 ('nHighpassFilterType','b'),
		 ('fPostProcessLowpassFilter','f'),
		 ('nPostProcessLowpassFilterType','c'),
		 ('bEnabledDuringPN','b'),
		 ('nStatsChannelPolarity','h'),
		 ('lADCChannelNameIndex','i'),
		 ('lADCUnitsIndex','i'),
		 ]

TagInfoDescription = [
	   ('lTagTime','i'),
	   ('sComment','56s'),
	   ('nTagType','h'),
	   ('nVoiceTagNumber_or_AnnotationIndex','h'),
	   ]

if __name__ == '__main__':
	f='/Users/arvind/Research/Experiments/jan_doublets/AS45_2 Kopie-e249-235_st.abf'

	[freq, hdr, bandwidth, gain, data]=abfload_gp(f)

	print freq, hdr, bandwidth, gain
	
	print len(data)

	import matplotlib.pyplot as plt

	plt.plot( data[:100000] )
	plt.show()

