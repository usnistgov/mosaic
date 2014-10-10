.. _scripting-page:

Scripting and Advanced Features
=================================


The analysis can be run from the command line by setting up a Python script. Scripting in Python allows one to build additional analysis tools on top of *<name>*. The first step is to import the relevant modules, which can be accomplished with the import command. All the relevant modules required to run an analysis are contained within the top level *<name>* module.


.. sourcecode:: python

    import <name>.qdfTrajIO as qdf
    import <name>.abfTrajIO as abf
    
    import <name>.SingleChannelAnalysis
    import <name>.eventSegment as es
    import <name>.stepResponseAnalysis as sra 
    import <name>.besselLowpassFilter as bessel


Basic Scripting
---------------------------------------------

Once the required modules are imported, a basic analysis can be run with the code snippet below. The top-level object that is used to configure and run a new analysis is *SingleChannelAnalysis*, which takes three arguments: i) a *TrajIO* object that reads in data, ii) a handle to a partitioning algorithm (e.g. *eventSegment*) that partitions the data and iii) a handle to a processing algorithm (e.g. *stepResponseAnalysis*) that processes individual blockade events.



.. sourcecode:: python

    # Process all ABF files in a directory
    <name>.SingleChannelAnalysis.SingleChannelAnalysis(
                abf.abfTrajIO(dirname='~/ReferenceData/abfSet1', filter='*abf'), 
                es.eventSegment,
                sra.stepResponseAnalysis
            ).Run()
    


The code listing above analyzes all ABF files in the specified directory. The *abfTrajIO* object requires the *dirname* argument that specifies the location of the data. The files included in the analysis can be filtered using the *filter* argument. The *filter* argument accepts `regular expressions <http://en.wikipedia.org/wiki/Regular_expression>`_ that allow the files included in the analysis to be further restricted. A detailed description of the  arguments allowed by *TrajIO* are included in the :ref:`api-docs-page`. 

.. sourcecode:: python

    # Process all QDF files in a directory
    <name>.SingleChannelAnalysis.SingleChannelAnalysis(
                qdf.qdfTrajIO(  dirname='~/ReferenceData/qdfSet1',filter='*qdf', 
                                Rfb=2.126E+9, Cfb=1.13E-12), 
                es.eventSegment,
                sra.stepResponseAnalysis
            ).Run() 

*<name>* also supports the QUB QDF file format used by the `Electronic Biosciences <http://electronicbio.com>`_ Nanopatch system. This is accomplished by replacing *abfTrajIO* in the previous example with *qdfTrajIO*.  Two additional parameters, the feedback resistance (Rfb) in Ohms and capacitance (Cfb) in Farads are required.

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


Filter Data
---------------------------------------------

.. sourcecode:: python

    # Filter data with a Bessel filter before processing
    <name>.SingleChannelAnalysis.SingleChannelAnalysis(
                abf.abfTrajIO(  dirname='~/ReferenceData/abfSet1',filter='*abf', 
                                datafilter=bessel.besselLowpassFilter), 
                es.eventSegment,
                sra.stepResponseAnalysis
            ).Run()

*<name>* supports filtering data prior to analysis. This is achieved by passing the *datafilter* argument to the *TrajIO* object. In the code above, the ABF data is filtered using a *BesselLowpassFilter*. Parameters for the filter are defined within the settings file as described in the :ref:`settings-page` section.

.. sourcecode:: javascript

    "besselLowpassFilter" : {
        "filterOrder"    : "6",
        "filterCutoff"   : "10000",
        "decimate"       : "1"   
    }

    

Leverage Python Scripting
---------------------------------------------

Scripting with Python allows transforming the output of the *<name>* further to generate plots, perform additional analysis or extend functionality. Moreover, individual components of the *<name>* module, which forms the back end code executed in the data processing pipeline, can be used for specific tasks. In this section, we highlight a few typical use cases. 

**Plot the Ionic Current Time-Series**

.. sourcecode:: python

    import <name>.abfTrajIO as abf
    import matplotlib.pyplot as plt
    import numpy as np
    
    abfDat=abf.abfTrajIO(dirname='~/abfSet1/', filter='*.abf')
    plt.plot( np.arange(0,1,1/500000.), b.previewdata(500000), 'b.', markersize=2 )
    plt.xlabel("t (s)", fontsize=14)
    plt.ylabel("-i (pA)", fontsize=14)
    plt.show()
    
    # Save the displayed data to disk as a comma separated text file.
    abfDat.popdata(500000).tofile('~/abfSet1/file1.csv',sep=',')

It is useful to visualize time-series data to highlight unique characteristics of a sample. For example the sample code above was used to load 1 second of monodisperse PEG28 data, sampled at 500 kHz. The data was read using a *abfTrajIO* object similar to the examples above. The *previewdata* command was used to preview 500k data points (or 1 second) and then plot a time-series using `matplotlib <http://matplotlib.org>`_ (see figure below). Finally, the *popdata* function of *abfTrajIO* was used to take the same 500k points and save them to a comma separated text file. Note that *popdata* removes the points from the data pipeline. Calling popdata second time will return the next *n* points.


.. image:: ../images/advancedFig2.png
   :width: 500 px
   :align: center

**Estimate the Channel Gating Duration**

.. sourcecode:: python

    import <name>.abfTrajIO as abf
    import numpy as np

    def estimateGatingDuration( trajioobj, gatingcurrentpa, blocksz, totaltime, fshz ):
        npts = int((fshz)*blocksz)
        nblk = int(totaltime/blocksz)-1

        gEvents = filter(  lambda x:x<float(gatingcurrentpa), 
                           [ np.mean(trajioobj.popdata(npts)) for i in range(nblk) ])

        return len(gEvents)*blocksz

    abfObj=abf.abfTrajIO(dirname='~/abfSet1',filter='*.abf')
    print estimateGatingDuration( abfObj, 20., 0.25, 100, abfObj.FsHz )

Scripting can be used to obtain statistics from the raw time-series. In the above code snippet, we estimate the amount of time a channel spends in a gated state by combining modules defined within *<name>*. The analysis is performed in blocks for efficiency. We first define a Python function that takes multiple arguments including  *TrajIO* object, the threshold at which we want to define the gated state in pA (gatingcurrentpa), the block size in seconds (blocksz), the total time of the time-series being processed in seconds (totaltime) and the sampling rate of the data in Hz (fshz). The code then calculates the number of blocks in which the channel was in a gated state and returns the time spent in that state in seconds.

**Plot the Output of an Analysis**

This final example shows how one can use *<name>* to process an ionic current time-series and then build a custom script that further analyses and plots the results. This example uses single-molecule mass spectrometry (SMMS) from `Robertson et al., PNAS 2007 <http://www.pnas.org/content/104/20/8207>`_.


.. sourcecode:: python

    import <name>.qdfTrajIO as qdf
    import <name>.abfTrajIO as abf
    
    import <name>.SingleChannelAnalysis
    import <name>.eventSegment as es
    import <name>.stepResponseAnalysis as sra 
    
    import glob
    import pylab as pl
    import numpy as np
    import <name>.sqlite3MDIO as sql
    
    # Process all ABF files in a directory
    <name>.SingleChannelAnalysis.SingleChannelAnalysis(
                abf.abfTrajIO(dirname='~/ReferenceData/abfSet1',filter='*abf'), 
                es.eventSegment,
                sra.stepResponseAnalysis
            ).Run()
    
    
    # Load the results of the analysis
    s=sql.sqlite3MDIO()
    s.openDB(glob.glob("~/ReferenceData/abfSet1/*sqlite")[-1])
    
    # Query the database to obtain the blockade depth and residence times
    q = "ProcessingStatus='normal' and ResTime > 0.2 and BlockDepth between 0.15 and 0.55"
    x=np.hstack( s.queryDB("select BlockDepth from metadata where " + q) )
    y=np.hstack( s.queryDB("select ResTime from metadata where + q") )
    
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
    pl.hist2d(x,y, bins=250)
    
    pl.xlabel("Blockade Depth", fontsize=14)
    pl.ylabel("Residence Time (ms)", fontsize=14)
    pl.ylim([0.19, 2])
    
    pl.show()

In the code above, we first process all the ABF files in a specified directory similar to the examples in previous sections. Upon completion of the analysis, the results are stored in a SQLite database, which can be then queried using the `structured query language (SQL) <http://en.wikipedia.org/wiki/SQL>`_. 

Next, we generate a two pane plot using `matplotlib <http://matplotlib.org>`_. The top pane contains a histogram of the blockade depth, while the bottom pane plots a 2D histogram of residence time vs. blockade depth.

.. image:: ../images/advancedFig3.png
   :width: 500 px
   :align: center
