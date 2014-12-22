.. _scripting-page:

Scripting and Advanced Features
=================================


The analysis can be run from the command line by setting up a Python_ script. Scripting allows one to build additional analysis tools on top of |projname|. The first step is to import the relevant modules, which can be accomplished with the import command. All the relevant modules required to run an analysis are contained within the top level |projname| module.


.. sourcecode:: python

    import mosaic.qdfTrajIO as qdf
    import mosaic.abfTrajIO as abf
    
    import mosaic.SingleChannelAnalysis
    import mosaic.eventSegment as es
    import mosaic.stepResponseAnalysis as sra 
    import mosaic.besselLowpassFilter as bessel


Import Data and Run an Analysis
---------------------------------------------


Once the required modules are imported, a basic analysis can be run with the code snippet below. The top-level object that is used to configure and run a new analysis is :py:class:`~mosaic.SingleChannelAnalysis.SingleChannelAnalysis`, which takes five arguments: i) the path to the data directory, ii) a handle to a *TrajIO* object that reads in data (e.g. :py:class:`~mosaic.abfTrajIO.abfTrajIO`), iii) a handle to a data filtering algorithm (e.g. :py:class:`~mosaic.besselLowpassFilter.besselLowpassFilter` or `None` for no filtering), iv) a handle to a partitioning algorithm (e.g. :py:class:`~mosaic.eventSegment.eventSegment`) that partitions the data and v) a handle to a processing algorithm (e.g. :py:class:`~mosaic.stepResponseAnalysis.stepResponseAnalysis`) that processes individual blockade events.



.. sourcecode:: python

    # Process all ABF files in a directory
    mosaic.SingleChannelAnalysis.SingleChannelAnalysis(
                '~/ReferenceData/abfSet1',
                abf.abfTrajIO,
                None,
                es.eventSegment,
                sra.stepResponseAnalysis
            ).Run()

The code listing above analyzes all ABF files in the specified directory. Handles to trajectory I/O, data filtering, event partitioning and event processing are controlled with their corresponding sections in the :ref:`settings-page`. Default settings used to read ABF files are shown below.

.. sourcecode:: javascript
    
    "abfTrajIO" : {
        "filter"            : "*.abf", 
        "start"             : 0.0, 
        "dcOffset"          : 0.0
    }

|projname| also supports the QUB QDF file format used by the `Electronic Biosciences`_ Nanopatch system. This is accomplished by replacing :py:class:`~mosaic.abfTrajIO.abfTrajIO` in the previous example with :py:class:`~mosaic.qdfTrajIO.qdfTrajIO`.  Settings for QDF files require two additional parameters, the feedback resistance (Rfb) in Ohms and capacitance (Cfb) in Farads as described in the :ref:`api-docs-page`.

.. sourcecode:: python

    # Process all QDF files in a directory
    mosaic.SingleChannelAnalysis.SingleChannelAnalysis(
                '~/ReferenceData/qdfSet1',
                qdf.qdfTrajIO,
                None,
                es.eventSegment,
                sra.stepResponseAnalysis
            ).Run() 



Upon completion the analysis writes a log file to the directory containing the data. The log file summarizes the conditions under which the analysis were run, the settings used and timing information. 

::

    Start time: 2014-10-05 11:53 AM

    [Status]
        Segment trajectory: ***USER STOP***
        Process events: ***NORMAL***


    [Summary]
        Baseline open channel conductance:
            Mean    = 136.0 pA
            SD  = 5.5 pA
            Slope   = 0.0 pA/s

        Event segment stats:
            Events detected = 11306

            Open channel drift (max) = 0.0 * SD
            Open channel drift rate (min/max) = (-2.77/3.0) pA/s


    [Settings]
        Trajectory I/O settings: 
            Files processed = 27
            Data path = ~/ReferenceData/qdfSet1
            File format = qdf
            Sampling frequency = 500.0 kHz

            Feedback resistance = 9.1 GOhm
            Feedback capacitance = 1.07 pF

        Event segment settings:
            Window size for block operations = 0.5 s
            Event padding = 50 points
            Min. event rejection length = 5 points
            Event trigger threshold = 2.36363636364 * SD

            Drift error threshold = 999.0 * SD
            Drift rate error threshold = 999.0 pA/s


        Event processing settings:
            Algorithm = stepResponseAnalysis

            Max. iterations  = 50000
            Fit tolerance (rel. err in leastsq)  = 1e-07
            Blockade Depth Rejection = 0.9



    [Output]
        Output path = ~/ReferenceData/qdfSet1
        Event characterization data = ~/ReferenceData/qdfSet1/eventMD-20141005-115324.sqlite
        Event time-series = ***enabled***
        Log file = eventProcessing.log

    [Timing]
        Segment trajectory = 98.03 s
        Process events = 0.0 s

        Total = 98.03 s
        Time per event = 8.67 ms

.. _scripting-filter-sec:

Filter Data
^^^^^^^^^^^^^^^^^^^^^^^^


.. sourcecode:: python

    # Filter data with a Bessel filter before processing
    mosaic.SingleChannelAnalysis.SingleChannelAnalysis(
                '~/ReferenceData/abfSet1',
                abf.abfTrajIO,
                bessel.besselLowpassFilter, 
                es.eventSegment,
                sra.stepResponseAnalysis
            ).Run()

|projname| supports filtering data prior to analysis. This is achieved by passing the `dataFilterHnd` argument to the :py:class:`~mosaic.SingleChannelAnalysis.SingleChannelAnalysis` object. In the code above, the ABF data is filtered using a :py:class:`~mosaic.besselLowpassFilter.besselLowpassFilter`. Parameters for the filter are defined within the settings file as described in the :ref:`settings-page` section.

.. sourcecode:: javascript

    "besselLowpassFilter" : {
        "filterOrder"    : "6",
        "filterCutoff"   : "10000",
        "decimate"       : "1"   
    }

A similar approach can be used to filter data using a :py:class:`~mosaic.waveletDenoiseFilter.waveletDenoiseFilter` or a tap delay line (:py:class:`~mosaic.convolutionFilter.convolutionFilter`). Additional filters can be easily added to |projname| as described in :ref:`extend-page`.

Advanced Scripting
---------------------------------------------

Scripting with Python_ allows transforming the output of the |projname| further to generate plots, perform additional analysis or extend functionality. Moreover, individual components of the |projname| module, which forms the back end code executed in the data processing pipeline, can be used for specific tasks. In this section, we highlight a few typical use cases. 

**Plot the Ionic Current Time-Series**

.. sourcecode:: python

    import mosaic.abfTrajIO as abf
    import matplotlib.pyplot as plt
    import numpy as np
    
    abfDat=abf.abfTrajIO(dirname='~/abfSet1/', filter='*.abf')
    plt.plot( np.arange(0,1,1/500000.), b.popdata(500000), 'b.', markersize=2 )
    plt.xlabel("t (s)", fontsize=14)
    plt.ylabel("-i (pA)", fontsize=14)
    plt.show()


It is useful to visualize time-series data to highlight unique characteristics of a sample. For example the sample code above was used to load 1 second of monodisperse PEG28 data, sampled at 500 kHz. The data was read using a :py:class:`~mosaic.abfTrajIO.abfTrajIO` object similar to the examples above. The :py:meth:`~mosaic.metaTrajIO.metaTrajIO.popdata` command was used to take 500k data points (or 1 second) and then plot a time-series using matplotlib_ (see figure below). Calling popdata a second time will return the next *n* points.


.. figure:: ../images/advancedFig2.png
   :width: 50 %
   :align: center

**Estimate the Channel Gating Duration**

Scripting can be used to obtain statistics from the raw time-series. In the code snippet below, we estimate the amount of time a channel spends in a gated state by combining modules defined within |projname|. The analysis is performed in blocks for efficiency. We first define a Python function that takes multiple arguments including  *TrajIO* object, the threshold at which we want to define the gated state in pA (gatingcurrentpa), the block size in seconds (blocksz), the total time of the time-series being processed in seconds (totaltime) and the sampling rate of the data in Hz (fshz). The code then calculates the number of blocks in which the channel was in a gated state and returns the time spent in that state in seconds.

.. sourcecode:: python

    import mosaic.abfTrajIO as abf
    import numpy as np

    def estimateGatingDuration( trajioobj, gatingcurrentpa, blocksz, totaltime, fshz ):
        npts = int((fshz)*blocksz)
        nblk = int(totaltime/blocksz)-1

        # Iterate over the blocks of data and check if the channel was in a gated state.
        # The code below returns the mean ionic current of blocks that are below the gating
        # threshold (gatingcurrentpa)
        gEvents = filter(  lambda x:x<float(gatingcurrentpa), 
                           [ np.mean(trajioobj.popdata(npts)) for i in range(nblk) ])

        return len(gEvents)*blocksz

    abfObj=abf.abfTrajIO(dirname='~/abfSet1',filter='*.abf')
    print estimateGatingDuration( abfObj, 20., 0.25, 100, abfObj.FsHz )


**Plot the Output of an Analysis**

This final example shows how one can use |projname| to process an ionic current time-series and then build a custom script that further analyses and plots the results. This example uses single-molecule mass spectrometry (SMMS) data from `Robertson et al., PNAS 2007 <http://www.pnas.org/content/104/20/8207>`_.

In the code below, we first process all the ABF files in a specified directory similar to the examples in previous sections. Upon completion of the analysis, the results are stored in a SQLite_ database, which can be then queried using the structured query language (SQL_). 

.. sourcecode:: python

    import mosaic.qdfTrajIO as qdf
    import mosaic.abfTrajIO as abf
    
    import mosaic.SingleChannelAnalysis
    import mosaic.eventSegment as es
    import mosaic.stepResponseAnalysis as sra 
    
    import glob
    import pylab as pl
    import numpy as np
    import mosaic.sqlite3MDIO as sql
    
    # Process all ABF files in a directory
    mosaic.SingleChannelAnalysis.SingleChannelAnalysis(
                '~/ReferenceData/abfSet1',
                abf.abfTrajIO,
                None,
                es.eventSegment,
                sra.stepResponseAnalysis
            ).Run()
    
    
    # Load the results of the analysis
    s=sql.sqlite3MDIO()
    s.openDB(glob.glob("~/ReferenceData/abfSet1/*sqlite")[-1])
    
    # We first set up a string that holds the query to retrieve the analysis results. Note that {col} 
    # will be replaced with the name of the database column when we run the query below.
    q = "select {col} from metadata where ProcessingStatus='normal' and ResTime > 0.2 \
         and BlockDepth between 0.15 and 0.55"

    # Now we run two separate queries - the first returns the blockade depth
    # and the second returns the residence time. Note that we simply take the query
    # string 'q' above and replace {col} with the column name.
    x=np.hstack( s.queryDB( q.format(col='BlockDepth') ) )
    y=np.hstack( s.queryDB( q.format(col='ResTime') ) )
    
    # Use matplotlib to plot the results with 2 views: 
    # i)  a 1D histogram of blockade depths and
    # ii) a 2D histogram of the residence times vs. blockade depth
    fig = pl.gcf()
    fig.canvas.set_window_title('Residence Time vs. Blockade Depth')
    
    pl.subplot(2, 1, 1)
    pl.hist(x, bins=500, histtype='step', rwidth=0.1)
    pl.xticks(())
    pl.ylabel("Counts", fontsize=14)
    
    pl.subplot(2, 1, 2)
    pl.hist2d(x,y, bins=500)
    
    pl.xlabel("Blockade Depth", fontsize=14)
    pl.ylabel("Residence Time (ms)", fontsize=14)
    pl.ylim([0.2, 20])
    
    pl.show()


Next, we generate a two pane plot using matplotlib_. The top pane contains a histogram of the blockade depth, while the bottom pane plots a 2D histogram of residence time vs. blockade depth.

.. figure:: ../images/advancedFig3.png
   :width: 50 %
   :align: center


.. include:: ../aliases.rst

