
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
