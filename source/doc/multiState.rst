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

.. sourcecode:: python

	[recIDX, ProcessingStatus, OpenChCurrent, NStates, CurrentStep, BlockDepth, EventStart, EventEnd, EventDelay, ResTime, RCConstant, AbsEventStart, ReducedChiSquared, TimeSeries]