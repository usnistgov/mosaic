.. _multistate-page:

Multi-state Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The multistate algorithm implements the  general case for identifying states in nanopore data :cite:`Balijepalli:2014ft`. The general form of the equation used in this algorithm is shown below, where *N* is the number of states. This functional form is fit to a time-series from a single event to recover optimal parameters for the mdoel.

.. math::
    i(t)=i_0 + \sum_{j=1}^{N} a_j\left(1-e^{-\left(t-\mu_j\right)/\tau_j}\right) H\left(t-\mu_j\right)


Settings that control the fit are defined through the settings file and are described in more detail in the :ref:`algorithm-settings-sec` section. Upon successfully fitting the model to an event, :py:class:`~mosaic.multiStateAnalysis.multiStateAnalysis` generates meta-data the describes the individual states in the event. A representative example of one such event is shown in the figure below.

.. figure:: ../images/Multistate.png
   :width: 50 %
   :align: center


Algorithm Settings
##########################################
.. exec::
	import mosaic.multiStateAnalysis

	print mosaic.multiStateAnalysis.multiStateAnalysis.__doc__


Metadata Output
##########################################
The :py:class:`~mosaic.multiStateAnalysis.multiStateAnalysis` algorithm outputs meta-data that characterizes every processed event. Similar to the :ref:`stepresponse-page` algorithm, this information is stored in a SQLite_ database and is available for further processing (see :ref:`database-page`). Notably, the data output by :py:class:`~mosaic.multiStateAnalysis.multiStateAnalysis` differs from :py:class:`~mosaic.stepResponseAnalysis.stepResponseAnalysis` in one important way. Because the number of states (*NStates*) detected in each event is not pre-determined, key meta-data (e.g. *BlockDepth*, *EventDelay*, etc.) are stored as arrays of real numbers with length equal to *NStates*. 

.. tabularcolumns:: p{4cm}p{4cm}p{8cm}

+-------------------+-----------------+------------------------------------------------+
|  **Column Name**  | **Column Type** | **Description**                                |
+===================+=================+================================================+
| recIDX            | INTEGER         | Record index.                                  |
|                   |                 |                                                |
| ProcessingStatus  | TEXT            | Status of the analysis.                        |
|                   |                 |                                                |
| OpenChCurrent     | REAL            | Open channel current in pA.                    |
|                   |                 |                                                |
| NStates           | INTEGER         | Number of detected states.                     |
|                   |                 |                                                |
| CurrentStep       | REAL_LIST       | Blocked current steps in pA.                   |
|                   |                 |                                                |
| BlockDepth        | REAL_LIST       | BlockedCurrent/OpenChCurrent for each state.   |
|                   |                 |                                                |
| EventStart        | REAL            | Event start in ms.                             |
|                   |                 |                                                |
| EventEnd          | REAL            | Event end in ms.                               |
|                   |                 |                                                |
| EventDelay        | REAL_LIST       | Start time of each state in ms.                |
|                   |                 |                                                |
| ResTime           | REAL            | EventEnd-EventStart in ms.                     |
|                   |                 |                                                |
| RCConstant        | REAL            | System RC constant in ms.                      |
|                   |                 |                                                |
| AbsEventStart     | REAL            | Global event start time in ms.                 |
|                   |                 |                                                |
| ReducedChiSquared | REAL            | Reduced Chi-squared of fit.                    |
|                   |                 |                                                |
| TimeSeries        | REAL_LIST       | (OPTIONAL) Event time-series.                  |
+-------------------+-----------------+------------------------------------------------+
