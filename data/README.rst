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

Algorithm: MOSAIC StepResponse
OutputDB: eventMD-PEG28-Reference.sqlite
Settings:

{
    "stepResponseAnalysis": {
        "FitTol": 1e-07,
        "BlockRejectRatio": 0.9,
        "FitIters": 50000
    },
    "qdfTrajIO": {
        "filter": "*.qdf",
        "start": 0.0,
        "Cfb": 1.07e-12,
        "dcOffset": 0.0,
        "Rfb": 9100000000.0
    },
    "eventSegment": {
        "meanOpenCurr": -1.0,
        "slopeOpenCurr": -1.0,
        "eventPad": 50,
        "driftThreshold": 999.0,
        "maxDriftRate": 999.0,
        "eventThreshold": 3.9373285666187976,
        "writeEventTS": 1,
        "minEventLength": 5,
        "sdOpenCurr": -1.0,
        "reserveNCPU": 3,
        "parallelProc": 0,
        "blockSizeSec": 0.5
    }
}