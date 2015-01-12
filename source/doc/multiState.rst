.. _multistate-page:

Multi-state Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The multistate algorithm implements the  general case for identifying states in nanopore data :cite:`Balijepalli:2014ft`. The general form of the equation used in this algorithm is shown below, where *N* is the number of states. This functional form is fit to a time-series from a single event to recover optimal parameters for the mdoel.

.. math::
    i(t)=i_0 + \sum_{j=1}^{N} a_j\left(1-e^{-\left(t-\mu_j\right)/\tau_j}\right) H\left(t-\mu_j\right)


Upon successfully fitting the model to an event, :py:class:`~mosaic.multiStateAnalysis.multiStateAnalysis` generates meta-data the describes the individual states in the event. A representative example of one such event is shown in the figure below, followed by a list of the meta-data output by the algorithm. 

.. figure:: ../images/Multistate.png
   :width: 50 %
   :align: center


.. tabularcolumns:: |p{4cm}|p{4cm}|p{6cm}|

+-------------------+-----------------+---------------------------------+
|  **Column Name**  | **Column Type** | **Description**                 |
+===================+=================+=================================+
| recIDX            | INTEGER         | Record index.                   |
|                   |                 |                                 |
| ProcessingStatus  | TEXT            | Status of the analysis.         |
|                   |                 |                                 |
| OpenChCurrent     | REAL            | Open channel current in pA.     |
|                   |                 |                                 |
| NStates           | INTEGER         | Number of detected states.      |
|                   |                 |                                 |
| CurrentStep       | REAL_LIST       | Blocked current steps in pA.    |
|                   |                 |                                 |
| BlockDepth        | REAL_LIST       | BlockedCurrent/OpenChCurrent    |
|                   |                 | for each state.                 |
|                   |                 |                                 |
| EventStart        | REAL            | Event start in ms.              |
|                   |                 |                                 |
| EventEnd          | REAL            | Event end in ms.                |
|                   |                 |                                 |
| EventDelay        | REAL_LIST       | Start time of each state in ms. |
|                   |                 |                                 |
|                   |                 |                                 |
| ResTime           | REAL            | EventEnd-EventStart in ms.      |
|                   |                 |                                 |
| RCConstant        | REAL            | System RC constant in ms.       |
|                   |                 |                                 |
| AbsEventStart     | REAL            | Global event start time in ms.  |
|                   |                 |                                 |
| ReducedChiSquared | REAL            | Reduced Chi-squared of fit.     |
|                   |                 |                                 |
| TimeSeries        | REAL_LIST       | (OPTIONAL) Event time-series.   |
+-------------------+-----------------+---------------------------------+
