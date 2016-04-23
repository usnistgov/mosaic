.. _cusumlevel-page:

CUSUM+
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The CUSUM algorithm (used by OpenNanopore for example) :cite:`Raillon:2012is` is available in |projname|. In contrast with other algorithms available in |projname|, this approach does not leverage system information in the analysis. This however results in a faster estimation of single- and multi-level events, compared with :ref:`stepresponse-page` and :ref:`multistate-page`. You can read about the CUSUM algorithm `here <http://pubs.rsc.org/en/Content/ArticleLanding/2012/NR/c2nr30951c#!divAbstract>`_.

Some known issues with CUSUM:

	1. If the duration of a sub-event is shorter than a five RC constants, the averaging will underestimate the extent of the current change. For longer events, CUSUM should achieve very similar output to the fitting employed elsewhere in |projname|.
	2. CUSUM assumes an instantaneous transition between current states. As a result, if the RC rise time of the system is large, CUSUM can trigger and detect intermediate states. This can usually be mitigated by optimizing the algorithm sensitivity settings.
	3. If an event is very long, CUSUM will detect a state transistion even if there is no real change, leading to an artificially high number of states. This is a consequence of false positives from using a statistical t-test. In some cases this can be mitigated by reducing the sensitivity.


Settings that control the algorithm are defined through the settings file, as described the :ref:`algorithm-settings-sec` section. Upon successfully analyzing an event, :py:class:`~mosaic.cusumPlus.cusumPlus` generates meta-data the describes the individual states in the event. A representative example of one such event is shown in the figure below.

.. figure:: ../images/CUSUM.png
   :width: 50 %
   :align: center


.. Algorithm Settings
.. ##########################################
.. .. exec::
.. 	import mosaic.cusumPlus

.. 	print mosaic.cusumPlus.cusumPlus.__doc__


Metadata Output
##########################################
The :py:class:`~mosaic.cusumPlus.cusumPlus` algorithm outputs meta-data that characterizes every processed event. Similar to the :ref:`multistate-page` algorithm, this information is stored in a SQLite_ database and is available for further processing (see :ref:`database-page`). 

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
| AbsEventStart     | REAL            | Global event start time in ms.                 |
|                   |                 |                                                |
| TimeSeries        | REAL_LIST       | (OPTIONAL) Event time-series.                  |
+-------------------+-----------------+------------------------------------------------+
