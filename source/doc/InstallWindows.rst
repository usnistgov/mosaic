.. _installwin:

Install |projname| on Windows
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the following guide, we provide step-by-step instructions on setting up and running |projname| on Windows. To simplify the isntallation, we use Anaconda_ to install some required dependencies. 

**1. Installing Anaconda**

First we will install Anaconda_ to easily install the dependencies required by |projname|. Download the 64-bit Anaconda_ installer for Python 2.7 and use the graphical installer. 


.. warning:: |projname| is not yet compatible with Python_ 3. Please ensure that you install Anaconda_ for Python_ 2.7


**2. Installing MOSAIC dependencies within Anaconda**


|projname| is written in Python_ 2.7 and utilizes a number of different packages and utilities. In the following we'll install a number of these (specifically, python, gcc, gfortran, qt, and pyQt4). With Anaconda_ this is easy to do.


First, we create a self-contained environment to host the |projname| installation. Open the Anaconda_ prompt (Start Menu-->Anaconda 2-->Anaconda Prompt) and type:

.. code-block:: console
    
  $  conda create -n mosaicENV python=2.7

Activate the new environment: 


.. code-block:: console
    
  $  conda activate mosaicENV


Add a new installation source (conda-forge) for packages that are not included with Anaconda_ out of the box:

.. code-block:: console
    
  $  conda config --add channels conda-forge

Install all the dependencies by typing:

.. code-block:: console
    
  $  conda install 
  			cython=0.29 
  			pandas=0.20.3 
  			nose=1.3.7 
  			numpy=1.11.1 
  			scipy=0.18.1 
  			docutils=0.14 
  			flask=0.12.2 
  			matplotlib=1.5.3 
  			pyqt=4 
  			lmfit=0.9.3 
  			uncertainties=2.4.8.1 
  			PyWavelets=0.5.2 
  			coverage=4.5.1 
  			codecov=2.0.15


.. hint:: The latest dependency version numbers can be obtained from the `requirements.txt <https://github.com/usnistgov/mosaic/blob/devel-2.0/requirements.txt>`_ file.

Install the |projname| source by `cloning the Github <https://github.com/usnistgov/mosaic>`_ repository or using one of the methods below.


**3. Installing MOSAIC**

.. include:: InstallMosaicSource.rst   

**4. Testing MOSAIC**

.. include:: TestMosaicSource.rst   
