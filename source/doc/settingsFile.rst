.. _settings-page:

Settings File
=================================


|projname| stores its settings in the JSON_ format. When using the graphical interface, a settings file is generated automatically upon starting an analysis, or by clicking *Save Settings* in the *File menu*  (see :ref:`gui-page`).

Settings Layout
---------------------------------------------

JSON_ is a human readable file format that consists of key-value pairs separated by sections. Each section in a JSON object consists of a section name and a list of string key-value pairs. 

.. sourcecode:: javascript

	{
		"<section name>" : {
			"key1" : "value1",
			"key2" : "value2",
			...
		}

	}

|projname| settings define a new section for each class, with key-value pairs corresponding to class attributes that are set upon initialization. This is illustrated below for the stepResponseAnalysis class. The *stepResponseAnalysis* section in the settings file holds parameters corresponding to the :class:`~mosaic.stepResponseAnalysis` class. Note that that the section name in the settings file is identical to the corresponding class name. Three parameters are then defined within the section that control the behavior of the class.

.. sourcecode:: javascript

	{
		"stepResponseAnalysis" : {
			"FitTol"			: "1.e-7",
			"FitIters"			: "50000",
			"BlockRejectRatio"		: "0.9"
		}
	}

Finally, :class:`~mosaic.stepResponseAnalysis` is initialized by defining class attributes corresponding to the key-value pairs in the settings file.

.. sourcecode:: python
	
	try:
			self.FitTol=float(self.settingsDict.pop("FitTol", 1.e-7))
			self.FitIters=int(self.settingsDict.pop("FitIters", 5000))

			self.BlockRejectRatio=float(self.settingsDict.pop("BlockRejectRatio", 0.8))
		
	except ValueError as err:
		raise commonExceptions.SettingsTypeError( err )



Default Settings
---------------------------------------------

.. sourcecode:: javascript

	{
		"eventSegment" : {
			"blockSizeSec" 			: "0.5",
			"eventPad" 			: "50",
			"minEventLength" 		: "5",
			"eventThreshold" 		: "6.0",
			"driftThreshold" 		: "999.0",
			"maxDriftRate" 			: "999.0",
			"meanOpenCurr"			: "-1",
			"sdOpenCurr"			: "-1",
			"slopeOpenCurr"			: "-1",
			"writeEventTS"			: "1",
			"parallelProc"			: "0",
			"reserveNCPU"			: "2"
		},
		"singleStepEvent" : {
			"binSize" 			: "1.0",
			"histPad" 			: "10",
			"maxFitIters"			: "5000",
			"a12Ratio" 			: "1.e4",
			"minEvntTime" 			: "10.e-6",
			"minDataPad" 			: "75"
		},
		"stepResponseAnalysis" : {
			"FitTol"			: "1.e-7",
			"FitIters"			: "50000",
			"BlockRejectRatio"		: "0.9"
		},
		"multiStateAnalysis" : {
			"FitTol"			: "1.e-7",
			"FitIters"			: "50000",
			"InitThreshold"			: "5.0"
		},
		"besselLowpassFilter" : {
			"filterOrder"			: "6",
			"filterCutoff"			: "10000",
			"decimate"			: "1"	
		},
		"waveletDenoiseFilter" : {
			"wavelet"			: "sym5",
			"level"				: "5",
			"thresholdType"			: "soft",
			"thresholdSubType"		: "sqtwolog"
		},
		,
		"abfTrajIO" : {
			"filter"			: "*.abf", 
			"start"				: 0.0, 
			"dcOffset"			: 0.0
		},
		"qdfTrajIO": {
			"Rfb"				: 9.1e+12, 
			"Cfb"				: 1.07e-12, 
			"dcOffset"			: 0.0, 
			"filter"			: "*.qdf", 
			"start"				: 0.0
		}
	}


.. include:: ../aliases.rst

