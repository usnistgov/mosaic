Introduction
=================================


|projname| is a modular toolbox for analyzing data from single molecule experiments. Primarily developed to analyze data from nanopore experiments :cite:`Reiner:2012bg`, |projname| can analyze any data that fit the form :cite:`Balijepalli:2014ft`: 


.. math::
    i(t)=i_0 + \sum_{j=1}^{N} a_j\left(1-e^{-\left(t-\mu_j\right)/\tau_j}\right) H\left(t-\mu_j\right)



The above functional form, which represents the response to a step change from one state to another is ubiqutous in many disciplines. By fitting individual state changes to the equation above, |projname| is able to automatically identify the states corresponding to each change. Moreover this approach allows us to accurately characterize transient events before they asymptotically approach a steady state. In nanopore applications, this has resulted in a 20-fold improvement in the number of states identified per unit time :cite:`Balijepalli:2014ft`.

|projname| offers tremendous flexibility in how it can be used. Nanopore data can be analyzed and visualized using the :ref:`gui-page` (GUI), which is available as a stand-alone application (`download binaries`_). This is a convenient way for most users to analyze nanopore data. Advanced users can write their own Python scripts to include |projname| in their analysis workflow (see :ref:`scripting-page`). Finally, because |projname| was designed from the start using object oriented design, developers can easily extend it by combining existing classes to define new functionality or writing their own classes (see :ref:`extend-page`).


.. include:: ../aliases.rst


