|projname|: |projlongname|
=================================

.. only:: html

   |projname| is a single molecule analysis toolbox that automatically decodes multi-state nanopore data. By modeling the nanopore system with an equivalent circuit, |projname| leverages the transient response of a molecule entering the channel to quantify pore-molecule interactions. In contrast to existing techniques such as ionic current thresholding :cite:`Pedone:2009ds,Robertson:2010gm` or Viterbi decoding :cite:`Viterbi:1967hq`, this technique allows the estimation of short-lived transient events that are otherwise not analyzed.

   Nanometer-scale pores have demonstrated potential use in biotechnology applications, including DNA sequencing :cite:`Kasianowicz:1996us`, single-molecule force spectroscopy :cite:`VanDorp:2009tg`, and single-molecule mass spectrometry :cite:`Robertson:2007jo`. The data modeling and analysis methods implemented in |projname| allow for considerable improvements in the quantification of molecular interactions with the channel in each of these applications.


.. toctree::
   :maxdepth: 2
   :numbered:

   doc/Introduction
   doc/Algorithms
   doc/GettingStarted
   doc/GraphicalInterface
   doc/settingsFile
   doc/DatabaseStructure
   doc/ScriptingandAdvancedFeatures
   doc/Extend
   doc/PublicationFigures
   doc/AdvancedAnalysis
   doc/Addons
   doc/DeveloperTools
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
