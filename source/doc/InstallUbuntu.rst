.. _installubuntu:
Install |projname| on Ubuntu(14.04)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

|projname| can be run under Ubuntu using a procedure very similar to :ref:`installosx`. 


**1. Prerequisites**

Several prerequisites must be installed prior to building |projname| dependencies. This is easily accomplished in Ubuntu using the `aptitude` package manager.  

.. hint::  `superuser` privileges are needed when installing |projname| prerequisites.

.. code-block:: console

  $  sudo apt-get install python python-dev python-pip python-qt4 
     freetype* gfortran liblapack-dev libblas-dev

.. _setPYTHONPATHUbuntu:

Next add the following to ~/.bashrc

.. code-block:: console

 	export PYTHONPATH=/usr/lib/python2.7/dist-packages


**2. (Optional) Install and Setup Virtual Environment**

.. include:: InstallVirtualenv.rst   

**3. Installing MOSAIC**

.. include:: InstallMosaicSource.rst   
