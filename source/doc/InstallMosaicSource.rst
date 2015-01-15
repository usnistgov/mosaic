**Install using Setuptools**

|projname| can be installed using Python_ setuptools using *pip* as shown below.

.. code-block:: console

	pip install mosaic-nist


When installed in this manner, in addition to the dependencies noted above, you must manually install additional dependencies required for |projname| to run. This can also be accomplished using *pip* as shown below. The version numbers included in the command are recommended but not required.

.. code-block:: console

	pip install numpy==1.8.1 cython==0.20.1 scipy==0.15.0 matplotlib==1.3.1 lmfit==0.7.4 uncertainties==2.4.6 PyWavelets==0.2.2


**Install from a Downloaded Source Distribution**

First we need to obtain the |projname| source code. For analyzing publication data, we recommend downloading the latest stable version of the source code (`download source`_). Alternatively, the latest development version can be downloaded from the `MOSAIC page on Github`_. Here we will show you how to set up |projname| from the latest stable release:

1. Download the latest release (`download source`_) 

2. Create a directory for the project source. In this case we will create a directory called MOSAIC, located in ``~/projects/``, where '~' is your home directory.

   
.. code-block:: console
   
    $ mkdir ~/projects/MOSAIC
   
3. Navigate to the directory: 

.. code-block:: console

   $ cd ~/projects/MOSAIC


4. Extract the source into this folder.

5. Make sure you are working in the virtual environment we set up in the previous step by typing:
   
.. code-block:: console
   
   $ workon MOSAIC

.. note:: 
	
	You will notice that (|projname|) now appears in front of the $ prompt in your shell. This inidicates that the virtual environment is active. We have employed this notation to indicate commands that should be run from inside the virtual environment.

6. |projname| and its dependencies are built using setuptools via a custom command as described below. However, we  must first install cython manually. Run the following command:

.. code-block:: console
 
   (MOSAIC)$ pip install cython


7.  To install the needed dependencies, navigate to ~/projects/MOSAIC/ and run the following:
   
.. code-block:: console
  
   (MOSAIC)$ python setup.py mosaic_deps

8.  Finally, add the installation directory (~/projects/MOSAIC as set up previously) to your `PYTHONPATH` as shown below. This addition can be made permanent by adding the line below to your `.bash_profile` (OS X) or `.bashrc` (Ubuntu) script.

.. code-block:: console

	(MOSAIC)$ export PYTHONPATH=$PYTHONPATH:~/projects/MOSAIC