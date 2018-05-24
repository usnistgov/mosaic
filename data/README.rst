PEG 28 Reference Data
=================================

Sample
----------------------------

Analyte: PEG28, PolyPure Norway
Electrolyte: 4 M KCl, 10 mM TRIS, pH 7.0

Instrumentation
----------------------------

Electronic Biosciences AC Amplifier
Bandwidth=100 kHz
Sampling Frequency=500 kHz

Analysis
----------------------------

Algorithm: MOSAIC ADEPT 2-State
OutputDB: eventMD-PEG28-ADEPT2State.sqlite
Settings:

{
    "qdfTrajIO": {
        "end": -1, 
        "start": 0, 
        "Cfb": 1.07e-12, 
        "dcOffset": 0, 
        "filter": "*.qdf", 
        "Rfb": 9100000000
    }, 
    "adept2State": {
        "FitTol": "1.e-7", 
        "LinkRCConst": "0", 
        "FitIters": "50000"
    }, 
    "eventSegment": {
        "meanOpenCurr": 136.251, 
        "slopeOpenCurr": -1, 
        "eventPad": 50, 
        "driftThreshold": -1, 
        "maxDriftRate": -1, 
        "writeEventTS": 1, 
        "minEventLength": 5, 
        "eventThreshold": 4.000441696113075, 
        "reserveNCPU": 3, 
        "parallelProc": 0, 
        "blockSizeSec": 0.5, 
        "sdOpenCurr": 6.792
    }
}