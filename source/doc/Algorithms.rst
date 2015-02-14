.. _algorithms-page:

Data Processing Algorithms in |projname|
=================================

There are three primary algorithms available in |projname| to process time-series data from single-molecule nanopore experiments. Fitting-based approaches are outlined in the :ref:`introduction-page`, are implemented in |projname| using two separate algorithms, i) StepResponseAnalysis is used for events that exhibit a single state, and ii) MultistateAnalysis for *N*-state events. In addition, the CUSUM algorithm is available for *N*-state events.

.. include:: ../doc/stepResponse.rst

.. include:: ../doc/multiState.rst

.. include:: ../doc/cusumLevels.rst

.. include:: ../aliases.rst