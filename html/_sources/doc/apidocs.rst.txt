.. _api-docs-page:

API Documentation
=================================

|projname| is designed using object oriented tools, which makes it easy to extend. The API documentation provides class level descriptions of the different modules that can be used in customized code. Meta-Classes (*blue*) define interfaces to five key parts of MOSAIC: time-series IO (:py:class:`~mosaic.metaTrajIO.metaTrajIO`), time-series filtering (:py:class:`~mosaic.metaIOFilter.metaIOFilter`), analysis output (:py:class:`~mosaic.metaMDIO.metaMDIO`), event partition and segmenting (:py:class:`~mosaic.metaEventPartition.metaEventPartition`), and event processing (:py:class:`~mosaic.metaEventProcessor.metaEventProcessor`). Sub-classing any of these meta classes and implementing their interface functions allows one to extend |projname|, while maintaining compatibility with other parts of the program. The diagram below shows the class inheritence in |projname|, with top-level classes in *gray*.

.. only:: html

   .. graphviz:: inherit_graph_html.dot

.. only:: latex

   .. graphviz:: inherit_graph_latex.dot

|projname| Modules
---------------------------------------------

.. toctree::
   :maxdepth: 3

   ../api-doc/mosaic
   ../api-doc/mosaic.meta
   ../api-doc/mosaic.traj
   ../api-doc/mosaic.filter
   ../api-doc/mosaic.partition
   ../api-doc/mosaic.processing
   ../api-doc/mosaic.output
   ../api-doc/mosaic.misc
   ../api-doc/mosaicscripts
