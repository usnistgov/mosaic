|projname|: |projlongname|
=================================


|projname| is a single molecule analysis toolbox that automatically decodes multi-state nanopore data. By modeling the nanopore system with an equivalent circuit, |projname| leverages the transient response of a molecule entering the channel to quantify pore-molecule interactions. In contrast to existing techniques such as ionic current thresholding :cite:`Pedone:2009ds,Robertson:2010gm` or Viterbi decoding :cite:`Viterbi:1967hq`, this technique allows the estimation of short-lived transient events that are otherwise not analyzed.

Nanometer-scale pores have demonstrated potential use in biotechnology applications, including DNA sequencing :cite:`Kasianowicz:1996us`, single-molecule force spectroscopy :cite:`VanDorp:2009tg`, and single-molecule mass spectrometry :cite:`Robertson:2007jo`. The data modeling and analysis methods implemented in |projname| allow for considerable improvements in the quantification of molecular interactions with the channel in each of these applications.

.. |projname| is written in Python and developed in the `Semiconductor and Device Metrology`_ division, of the `Physical Metrology Laborotory`_ at the `National Institute of Standards and Technology`_.

.. .. only:: html

..    +------------------------------------------------------------------+------------------------------------------------------------------+------------------------------------------------------------------+
..    | .. figure:: images/examples/smms.png                             | .. figure:: images/examples/smms.png                             | .. figure:: images/examples/smms.png                             |
..    |      :align: center                                              |      :align: center                                              |      :align: center                                              |
..    |      :width: 150pt                                               |      :width: 150pt                                               |      :width: 150pt                                               |
..    |      :height: 150pt                                              |      :height: 150pt                                              |      :height: 150pt                                              |
..    |      :target: doc/examples.html#single-molecule-mass-spectrometry|      :target: doc/examples.html#single-molecule-mass-spectrometry|      :target: doc/examples.html#single-molecule-mass-spectrometry|
..    |                                                                  |                                                                  |                                                                  |
..    |      Single Molecule Mass Spectrometry                           |      A second example                                            |      A third example                                             |
..    +------------------------------------------------------------------+------------------------------------------------------------------+------------------------------------------------------------------+



.. .. note::  If you use |projname| in your work, please cite:

..    \A. Balijepalli, J., Ettedgui, A. T. Cornio, J. W. F. Robertson K. P. Cheung, J. J. Kasianowicz & C. Vaz, "`Quantifying Short-Lived Events in Multistate Ionic Current Measurements. <http://pubs.acs.org/doi/abs/10.1021/nn405761y>`_" *ACS Nano* 2014, **8**, 1547–1553.

.. Contents:

.. toctree::
   :maxdepth: 2
   :numbered:

   doc/Introduction
   doc/GettingStarted
   doc/Algorithms
   doc/GraphicalInterface
   doc/settingsFile
   doc/DatabaseStructure
   doc/ScriptingandAdvancedFeatures
   doc/Extend
   doc/PublicationFigures
   doc/AdvancedAnalysis
   doc/Addons
   doc/examples
   doc/apidocs
   doc/ChangeLog
   doc/References


.. .. toctree::
..    :hidden:

..    doc/Home
..    doc/WorkingWithSQLite
..    doc/dataFiltering
..    doc/eventPartition
..    doc/eventProcessing
..    doc/eventSegment
..    doc/multiState
..    doc/stepResponse
..    doc/trajectoryIO


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`


.. include:: aliases.rst
