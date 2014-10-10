.. _stepresponse-page:

Step Response Analysis
---------------------------------------------

This algorithm is a special case of the `Multistate Analysis <link?>`_ described in `Balijepalli et al., ACS Nano, 2014 <http://pubs.acs.org/doi/abs/10.1021/nn405761y>`_. The algorithm fits events using the equation below, with *N* =2


.. math::
    i(t)=i_0 + \sum_{j=1}^{N} a_j\left(1-e^{-\left(t-\mu_j\right)/\tau_j}\right) H\left(t-\mu_j\right)

