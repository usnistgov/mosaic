.. _introduction-page:

Introduction
=================================


|projname| is a modular toolbox for analyzing data from single molecule experiments. Primarily developed to analyze data from nanopore experiments :cite:`Reiner:2012bg`, |projname| can analyze any data that fit the form :cite:`Balijepalli:2014ft`: 


.. math::
    i(t)=i_0 + \sum_{j=1}^{N} a_j\left(1-e^{-\left(t-\mu_j\right)/\tau_j}\right) H\left(t-\mu_j\right)



The above functional form, which represents the response to a step change from one state to another is ubiqutous in many disciplines. By fitting individual state changes to the equation above, |projname| is able to automatically identify the states corresponding to each change. Moreover this approach allows us to accurately characterize transient events before they asymptotically approach a steady state. In nanopore applications, this has resulted in a 20-fold improvement in the number of states identified per unit time :cite:`Balijepalli:2014ft`.

|projname| offers tremendous flexibility in how it can be used. Nanopore data can be analyzed and visualized using the :ref:`gui-page` (GUI), which is available as a stand-alone application (`download binaries`_). This is a convenient way for most users to analyze nanopore data. Advanced users can write their own Python scripts to include |projname| in their analysis workflow (see :ref:`scripting-page`). Finally, because |projname| was designed from the start using object oriented design, developers can easily extend it by combining existing classes to define new functionality or writing their own classes (see :ref:`extend-page`).


Background
---------------------------------------------

The interactions of single molecules with nanopores are observed by measuring changes to the ionic current that occurs when the pore changes from an unoccupied (i.e., an open channel) to an occupied state.  The electrical nature of the measurement allows us to model components of the physical system with equivalent electrical elements, (see figure below), and describe system behavior collectively with the circuit response :cite:`Balijepalli:2014ft`.  The resistance from the electrolyte solution between the two electrodes, together with the access resistance near the entrance of the channel due to electrical field constriction :cite:`Bezrukov:1993ij,Bezrukov:1996uc`, is modeled by resistors :math:`R_{cis}` and :math:`R_{trans}`, on each side of the nanopore.  The nanopore itself is modeled as a resistor, :math:`R_p`, in series with :math:`R_s`. Finally, the lipid bilayer is assumed to be a capacitive circuit element, :math:`C_m`, in parallel with the nanopore.

.. figure:: ../images/NanoporeCircuit.png
   :width: 35 %
   :align: center


Electrical circuits described above are typically analyzed using external time-varying signal sources. In contrast, for the nanopore sensor system, the applied potential is fixed, and the net change in the current arises internally from the change in the nanopore resistance, :math:`R_p`, from single molecules that partition into the pore.  We first determine the overall circuit impedance for the case where the channel resistance is fixed, to verify the validity of the equivalent circuit model, and later relax that condition. 


For a predetermined pore resistance, the channel ionic current can be obtained by applying Ohm’s law to the impedance (Z) of the circuit in Figure 1A, given in Laplace-space by

.. math::
	Z(s)=(R_{cis}+R_{trans})+\frac{1}{1/R_p+sC_m}


The fluctuations of individual molecules when they interact with a nanopore are too fast to resolve with existing instrumentation. However, nanopore-molecule interactions result in a discrete changes in the measured conductance, for example from individual DNA bases translocating across the channel. This allows us to model single-molecule events, assuming a constant applied potential :math:`V_a`, using a series of *N* instantaneous step changes in the ionic current, each representing a transition from one state to another. In Laplace space, each transition is modeled with a Heaviside step function, :math:`Rp(s) = \Delta R_p/s`, where :math:`\Delta R_p` is the instantaneous change in pore resistance, per unit time. We can obtain an expression for the nanopore current response of a single transition by substituting Z(s) into I(s) = Va/Z(s) and simplifying, 

.. math::
	I(s)=\frac{\alpha s}{1+\tau s},

where :math:`\alpha=(1/\Delta R_p +C_m)V_a` and :math:`\tau=(R_{cis}+R_{trans})(1/\Delta R_p+C_m)`. The inverse Laplace transform of I(s), yields an exponentially decaying time-domain current response,

.. math::
	i(t)=-\frac{\alpha}{\tau^2}exp(-t/\tau)+i_0, t>0,

where :math:`i_0` is the open channel current offset.  The equation for i(t) suggests that the experimentally observed RC time constant (:math:`\tau`) is characteristic of the molecule interacting with the pore and related to the molecule’s physical properties (e.g., volume, charge, etc.)  :cite:`Reiner:2010kv,Balijepalli:2013gt`. The equation above then provides the basis for practical single molecule analysis as seen at the top of this page :cite:`Balijepalli:2014ft`. Practical implementations of these techniques are described in :ref:`algorithms-page`.


.. include:: ../aliases.rst


