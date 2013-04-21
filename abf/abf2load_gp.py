import struct
import os

import numpy as np

class struct_file(file):
    def read_f(self, format , offset = None):
        if offset is not None:
            self.seek(offset)
        return struct.unpack(format , self.read(struct.calcsize(format)))

    def write_f(self, format , offset = None , *args ):
        if offset is not None:
            self.seek(offset)
        self.write( struct.pack( format , *args ) )

class ABF2():
    def __init__(self, filename):
        """
        """
        self.fname=filename
        self.header = self.read_header()

    def abf2load(self):
        """
        """
        if self.version < 2.:
            raise NotImplementedError("ABF version < 2.0 is not supported")
        
        if self.header['protocol']['nOperationMode'] == 3:  # gap-free mode
            self.data = self.read_gapfree()
        else:
            raise NotImplementedError("Only gapfree mode is supported.")

    @property 
    def version(self):
        return self.header['fFileVersionNumber']

    @property
    def samplingRateHz(self):
        return 1.e6/self.header['protocol']['fADCSequenceInterval']
        
    def read_header(self):
        """
        read the header of the file
        
        The strategy differ here from the original script under Matlab.
        In the original script for ABF2, it complete the header with informations
        that are located in other structures.
        
        In ABF2 this function return header with sub dict :
            sections             (ABF2)
            protocol             (ABF2)
            listTags             (ABF1&2) 
            listADCInfo          (ABF2)
            listDACInfo          (ABF2)
            dictEpochInfoPerDAC  (ABF2)
        that contain more information.
        """
        fid = struct_file(self.fname,'rb')
        
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
                header[key] = np.array(val)
        
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
                        tag[key] = np.array(val)
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
                        ADCInfo[key] = np.array(val)
                ADCInfo['ADCChNames'] = strings[ADCInfo['lADCChannelNameIndex']-1]
                ADCInfo['ADCChUnits'] = strings[ADCInfo['lADCUnitsIndex']-1]
                
                header['listADCInfo'].append( ADCInfo )
        
            # protocol sections
            protocol = { }
            fid.seek(sections['ProtocolSection']['uBlockIndex']*BLOCKSIZE)
            for key, format in protocolInfoDescription :
                val = fid.read_f(format )
                if len(val) == 1:
                    protocol[key] = val[0]
                else :
                    protocol[key] = np.array(val)
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
                        tag[key] = np.array(val)
                listTag.append(tag)
                
            header['listTag'] = listTag
            
            # DAC sections
            header['listDACInfo'] = [ ]
            for i in range(sections['DACSection']['llNumEntries']) :
                #  read DACInfo
                fid.seek(sections['DACSection']['uBlockIndex']*\
                            BLOCKSIZE+sections['DACSection']['uBytes']*i)
                DACInfo = { }
                for key, format in DACInfoDescription :
                    val = fid.read_f(format )
                    if len(val) == 1:
                        DACInfo[key] = val[0]
                    else :
                        DACInfo[key] = np.array(val)
                DACInfo['DACChNames'] = strings[DACInfo['lDACChannelNameIndex']-1]
                DACInfo['DACChUnits'] = strings[DACInfo['lDACChannelUnitsIndex']-1]
                
                header['listDACInfo'].append( DACInfo )
            
            
            # EpochPerDAC  sections
            # header['dictEpochInfoPerDAC'] is dict of dicts: 
            #  - the first index is the DAC number
            #  - the second index is the epoch number 
            # It has to be done like that because data may not exist and may not be in sorted order
            header['dictEpochInfoPerDAC'] = { }  
            for i in range(sections['EpochPerDACSection']['llNumEntries']) :
                #  read DACInfo
                fid.seek(sections['EpochPerDACSection']['uBlockIndex']*\
                            BLOCKSIZE+sections['EpochPerDACSection']['uBytes']*i)
                EpochInfoPerDAC = { }
                for key, format in EpochInfoPerDACDescription :
                    val = fid.read_f(format )
                    if len(val) == 1:
                        EpochInfoPerDAC[key] = val[0]
                    else :
                        EpochInfoPerDAC[key] = np.array(val)
                        
                DACNum = EpochInfoPerDAC['nDACNum']
                EpochNum = EpochInfoPerDAC['nEpochNum']
                # Checking if the key exists, if not, the value is empty 
                # so we have to create empty dict to populate
                if not header['dictEpochInfoPerDAC'].has_key(DACNum):
                    header['dictEpochInfoPerDAC'][DACNum] = { }
                
                header['dictEpochInfoPerDAC'][DACNum][EpochNum] = EpochInfoPerDAC  
            
        fid.close()
        
        return header

    def read_gapfree(self):
        """
            nOperationMode== 3
        """
        h = self.header
        fid = struct_file(self.fname,'rb')

        start = 0.0
        stop = 'e'
        channels = 'a'
        # the size of data chunks (see above) in Mb. 0.05 Mb is an empirical value
        # which works well for abf with 6(1,1)6 channels and recording durations of 
        # 5-30 min
        chunk = 0.05
        machineF = '<' #'ieee-le'
        
        verbose = 1
        # if first and only optional input argument is string 'info' the user's
        # request is to obtain information on the file (header parameters), so set
        # flag accordingly
        doLoadData = True 


        sampling_rate = 1.e6/h['protocol']['fADCSequenceInterval']
        nADCChans = h['sections']['ADCSection']['llNumEntries']
        lActualAcqLength = h['sections']['DataSection']['llNumEntries']
        si = sampling_rate * nADCChans

        # determine offset at which data start
        if h["nDataFormat"] == 0:    
            dataSz = 2    # bytes/point
            precision = 'i2' #int16   
        elif h["nDataFormat"] == 1:    
            dataSz = 4    # bytes/point
            precision = 'f'    
        else:    
            fid.close()    
            print 'invalid number format'


        # channel index
        # the numerical value of all recorded channels (numbers 0..15)
        # the corresponding indices into loaded data d
        recChInd = range(0, nADCChans)

        # check whether requested channels exist
        chInd = []
        eflag = 0
        if isinstance(channels, basestring):    
            if channels == 'a':        
                chInd = recChInd        
            else:        
                fid.close()        
                print 'input parameter \'channels\' must either be a cell array holding channel names or the single character \'a\' (=all channels)'     
                
        else:    
            for i in range(len(channels)):        
                tmpChInd = h["recChNames"].find(channels[i])        
                if len(tmpChInd) > 0:            
                    chInd = [chInd, tmpChInd]            
                else:            
                    # set error flag to 1
                    eflag = 1            
        if eflag:    
            fid.close()    
            print'**** available channels:'    
            print h["recChNames"]    
            print' '    
            print'**** requested channels:'    
            print channels 
            print 'at least one of the requested channels does not exist in data file (see above)'    


        #print'data were acquired in gap-free mode'    
        # from start, stop, headOffset and h["fADCSampleInterval"] calculate first point to be read 
        #  and - unless stop is given as 'e' - number of points
        startPt = np.floor(1e6 * start * (1 / sampling_rate))    
        # this corrects undesired shifts in the reading frame due to rounding errors in the previous calculation
        startPt = np.floor(startPt / nADCChans) * nADCChans
        # if stop is a char array, it can only be 'e' at this point (other values would have 
        # been caught above)
        if isinstance(stop,basestring):        
            h["dataPtsPerChan"] = lActualAcqLength / nADCChans - np.floor(1e6 * start / si)        
            h["dataPts"] = h["dataPtsPerChan"] * nADCChans
        else:        
            h["dataPtsPerChan"] = np.floor(1e6 * (stop - start) * (1 / si))        
            h["dataPts"] = h["dataPtsPerChan"] * nADCChans        
            if h["dataPts"] <= 0:            
                fid.close()            
                print 'start is larger than or equal to stop'            
                    
            
        if h["dataPts"] % nADCChans > 0:        
            fid.close()        
            print 'number of data points not OK'        
            
        tmp = 1e-6 * lActualAcqLength * sampling_rate
    #           if verbose:        
    #              print 'total length of recording: '), num2str(tmp, '%5.1f')), ' s ~ '), num2str(tmp / 60, '%3.0f')), ' min')      
            # 8 bytes per data point expressed in Mb
    #             print 'memory requirement for complete upload in matlab: '), num2str(round(8 * lActualAcqLength / 2 ** 20)), ' MB')      
            
        # recording start and stop times in seconds from midnight
        h["recTime"] = h["lFileStartTime"]    
        h["recTime"] = np.hstack([h["recTime"], h["recTime"] + tmp])    
        #if fid.seek(startPt * dataSz + headOffset) != 0:        
        #    fid.close()        
        #    print 'something went wrong positioning file pointer (too few data points ?)'        
            
        if doLoadData:        
            # *** decide on the most efficient way to read data:
            # [i] all (of one or several) channels requested: read, done
            # [ii] one (of several) channels requested: use the 'skip' feature of
            # fread
            # [iii] more than one but not all (of several) channels requested:
            # 'discontinuous' mode of reading data. Read a reasonable chunk of data
            # (all channels), separate channels, discard non-requested ones [if
            # any), place data in preallocated array, repeat until done. This is
            # faster than reading the data in one big lump, separating channels and
            # discarding the ones not requested
            if len(chInd) == 1 and nADCChans > 1:            
                # --- situation [ii]
                # jump to proper reading frame position in file
                if fid.seek((chInd - 1) * dataSz) != 0:                
                    fid.close()                
                    print 'something went wrong positioning file pointer (too few data points ?)'                
                skip = dataSz * (nADCChans - 1)
                prec = precision + 'x'*skip #pad bytes
                nbytes=struct.calcsize(prec)            
                # read, skipping nADCChans-1 data points after each read
                d = struct.unpack(prec, fid.read(h["dataPtsPerChan"]*nbytes))         
            #    if n != h["dataPtsPerChan"]:                
             #       fid.close()                
              #      print 'something went wrong reading file ('+ str(h["dataPtsPerChan"])+ ' points should have been read, '+str(n)+ ' points actually read'                
                            
            elif len(chInd) / nADCChans < 1:            
                # --- situation [iii]
                # prepare chunkwise upload:
                # preallocate d
                d = np.empty((h["dataPtsPerChan"], len(chInd)))            
                # the number of data points corresponding to the maximal chunk size,
                # rounded off such that from each channel the same number of points is
                # read (do not forget that each data point will by default be made a
                # double of 8 bytes, no matter what the original data format is)
                chunkPtsPerChan = floor(chunk * 2 ** 20 / 8 / nADCChans)            
                chunkPts = chunkPtsPerChan * nADCChans            
                # the number of those chunks..
                nChunk = floor(h["dataPts"] / chunkPts)            
                # ..and the remainder
                restPts = h["dataPts"] - nChunk * chunkPts            
                restPtsPerChan = restPts / nADCChans            
                # chunkwise row indices into d
                dix = range(1,chunkPtsPerChan,h["dataPtsPerChan"])           
                dix[:, 2] = dix[:, 1] + chunkPtsPerChan - 1            
                dix[-1, 2] = h["dataPtsPerChan"]            
          #      if verbose and nChunk:                
           #         printmcat(['reading file in '), int2str(nChunk), ' chunks of ~'), num2str(chunk), ' Mb')]))                
                            
                # do it
                for ci in mslice[1:size(dix, 1) - 1]:                
                    tmpd = struct.unpack(precision, fid.read(chunkPts))                
          #          if n != chunkPts:                    
           #             fid.close()                    
            #            print mcat(['something went wrong reading chunk #'), int2str(ci], ' ('), int2str(chunkPts), ' points should have been read, '), int2str(n), ' points actually read')]))                    
                                    
                    # separate channels..
                    tmpd = tmpd.reshape((nADCChans, chunkPtsPerChan))            
                    d[dix[ci, 1]:dix[ci, 2], :] = tmpd[chInd, :].cT                
                            
                # collect the rest, if any
                if restPts:                
                    tmpd = struct.unpack(precision, fid.read(restPts))                
                   # if n != restPts:                    
                    #    fid.close()                    
                     #   print mcat(['something went wrong reading last chunk ('), int2str(restPts), ' points should have been read, '), int2str(n), ' points actually read')]))                    
                                    
                    # separate channels..
                    tmpd = tmpd.reshape((nADCChans, restPtsPerChan))           
                    d[dix[-1, 1]:dix[-1, 2], :] = tmpd[chInd, :].cT                
                            
            else:            
                # --- situation [i]
                #d = struct.unpack(precision, fid.read(h["dataPts"])
                d = np.fromfile(file=fid, dtype=precision, count = int(h["dataPts"])).reshape((nADCChans, int(h["dataPtsPerChan"])))
               # if n != h["dataPts"]:                
                #    fid.close()                
                 #   print mcat(['something went wrong reading file ('), int2str(h["dataPts"]), ' points should have been read, '), int2str(n), ' points actually read')]))                
                            
                # separate channels..
              #  d = reshape(d,             
                #d = d'            
                    
            # if data format is integer, scale appropriately, if it's 'f', d is fine
            if not h["nDataFormat"]:            
                for ch in chInd:
                    # gain of telegraphed instruments, if any
                    if h["fFileVersionNumber"] >= 1.65:    
                        addGain = h['listADCInfo'][ch]["nTelegraphEnable"] * h['listADCInfo'][ch]["fTelegraphAdditGain"]    
                        addGain = np.where(addGain==0, 1, addGain)#addGain(addGain == 0] = 1    
                    else:    
                        addGain = h['listADCInfo'][ch]["fTelegraphAdditGain"]

                    scaling_factor = 1.0/ ((h['listADCInfo'][ch]["fInstrumentScaleFactor"] * h['listADCInfo'][ch]["fSignalGain"] * h['listADCInfo'][ch]["fADCProgrammableGain"] * addGain) * h['protocol']["fADCRange"] / h['protocol']["lADCResolution"] + h['listADCInfo'][ch]["fInstrumentOffset"] - h['listADCInfo'][ch]["fSignalOffset"])                
                    #print "scaling data with scaling factor of %f" % scaling_factor
                    #print d
                    tmp = np.empty(d.shape, dtype=np.float64)

                    tmp[:][ch] = d[:][ch] / (h['listADCInfo'][ch]["fInstrumentScaleFactor"] * h['listADCInfo'][ch]["fSignalGain"] * h['listADCInfo'][ch]["fADCProgrammableGain"] * addGain) * h['protocol']["fADCRange"] / h['protocol']["lADCResolution"] + h['listADCInfo'][ch]["fInstrumentOffset"] - h['listADCInfo'][ch]["fSignalOffset"]

                    return tmp

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

DACInfoDescription = [
       ('nDACNum','h'),
       ('nTelegraphDACScaleFactorEnable','h'),
       ('fInstrumentHoldingLevel', 'f'),
       ('fDACScaleFactor','f'),
       ('fDACHoldingLevel','f'),
       ('fDACCalibrationFactor','f'),
       ('fDACCalibrationOffset','f'),
       ('lDACChannelNameIndex','i'),
       ('lDACChannelUnitsIndex','i'),
       ('lDACFilePtr','i'),
       ('lDACFileNumEpisodes','i'),
       ('nWaveformEnable','h'),
       ('nWaveformSource','h'),
       ('nInterEpisodeLevel','h'),
       ('fDACFileScale','f'),
       ('fDACFileOffset','f'),
       ('lDACFileEpisodeNum','i'),
       ('nDACFileADCNum','h'),
       ('nConditEnable','h'),
       ('lConditNumPulses','i'),
       ('fBaselineDuration','f'),
       ('fBaselineLevel','f'),
       ('fStepDuration','f'),
       ('fStepLevel','f'),
       ('fPostTrainPeriod','f'),
       ('fPostTrainLevel','f'),
       ('nMembTestEnable','h'),
       ('nLeakSubtractType','h'),
       ('nPNPolarity','h'),
       ('fPNHoldingLevel','f'),
       ('nPNNumADCChannels','h'),
       ('nPNPosition','h'),
       ('nPNNumPulses','h'),
       ('fPNSettlingTime','f'),
       ('fPNInterpulse','f'),
       ('nLTPUsageOfDAC','h'),
       ('nLTPPresynapticPulses','h'),
       ('lDACFilePathIndex','i'),
       ('fMembTestPreSettlingTimeMS','f'),
       ('fMembTestPostSettlingTimeMS','f'),
       ('nLeakSubtractADCIndex','h'),
       ('sUnused','124s'),
       ]

EpochInfoPerDACDescription = [
       ('nEpochNum','h'),
       ('nDACNum','h'),
       ('nEpochType','h'),
       ('fEpochInitLevel','f'),
       ('fEpochLevelInc','f'),
       ('lEpochInitDuration','i'),
       ('lEpochDurationInc','i'),
       ('lEpochPulsePeriod','i'),
       ('lEpochPulseWidth','i'),
       ('sUnused','18s'),
       ]

EpochInfoDescription = [
       ('nEpochNum','h'),
       ('nDigitalValue','h'),
       ('nDigitalTrainValue','h'),
       ('nAlternateDigitalValue','h'),
       ('nAlternateDigitalTrainValue','h'),
       ('bEpochCompression','b'),
       ('sUnused','21s'),
       ]

if __name__ == '__main__':
    f = '/Users/balijepalliak/Research/Experiments/StepRespData/p29pure/'
    fn = '06710009.abf'
    a=ABF2(f+fn)
    #a=ABF2('/Users/balijepalliak/Google Drive/13102009.abf')
    a.abf2load()

    d=a.data

    print len(a.data), len(d[0]), a.samplingRateHz, a.version
    #d[0][:5000000].tofile('2012_09_10_0010.csv', sep=',')

    import matplotlib.pyplot as plt
    plt.plot(d[0][:500000])
    plt.ylabel('current (pA)')
    #plt.title(fn)
    plt.show()
