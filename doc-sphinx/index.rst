.. documentation master file, created by
   sphinx-quickstart on Thu Oct  9 15:51:16 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

<name>: Single-Molecule Analytical Research Toolbox
=================================


<name> is a single molecule analysis toolbox that automatically decodes multi-state nanopore data. By modeling the nanopore system with an equivalent circuit, <name> leverages the transient response of a molecule entering the channel to quantify pore-molecule interactions. In contrast to existing techniques such as ionic current thresholding {REFS} or Viterbi decoding {REFS}, this technique allows the estimation of short-lived transient events that are otherwise not analyzed.

Nanometer-scale pores have demonstrated potential use in biotechnology applications, including DNA sequencing {REFS}, single-molecule force spectroscopy {REFS}, and single-molecule mass spectrometry {REFS}. The data modeling and analysis methods implemented in <name> allow for dramatic improvements in the quantification of molecular interactions with the channel in each of these applications.

<name> is written in Python and developed in the Semiconductor and Device Metrology (`SDMD <http://www.nist.gov/pml/div683/about.cfm>`_) division, in the Physical Metrology Laborotory (`PML <http://www.nist.gov/pml/>`_) at the National Institute of Standards and Technology (`NIST <http://www.nist.gov>`_).

.. note:: If you use <name> in your work, please cite:

	A. Balijepalli, J., Ettedgui, A. T. Cornio, J. W. F. Robertson K. P. Cheung, J. J. Kasianowicz & C. Vaz, "`Quantifying Short-Lived Events in Multistate Ionic Current Measurements. <http://pubs.acs.org/doi/abs/10.1021/nn405761y>`_" *ACS Nano* 2014, **8**, 1547–1553.


.. Contents:

.. toctree::
   :maxdepth: 3

   doc/Introduction
   doc/GraphicalInterface
   doc/ScriptingandAdvancedFeatures
   doc/settingsFile
   doc/DatabaseStructure
   doc/trajectoryIO
   doc/dataFiltering
   doc/eventPartition
   doc/eventProcessing
   doc/WorkingWithSQLite
   doc/ChangeLog
   doc/examples
   doc/apidocs

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

