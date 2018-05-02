It is generally a good practice to run |projname| from within a dedicated virtual environment. This minimizes conflicts with other installed programs. While we highly recommend this approach, it is not required to run |projname|. If you prefer to skip this, move on to the next step now.

To setup a virtual environment, we need two different packages: *virtualenv*, which creates the virtual environments, and *virtualenvwrapper*, a wrapper for *virtualenv* that simplifies set up and use.

To install these and set up the virtual enviroment wrapper, run the following in a shell:

.. code-block:: console
   
    $  pip install virtualenv virtualenvwrapper

.. hint:: 
	
	Under Ubuntu, you may need install virtualenv and virtualenvwrapper as root. Simply prefix the command above with sudo.

If you would like virtualenvwrapper to be available each time you open a new terminal window, add the line below to  ~/.bash_profile on OS X or ~/.bashrc on Linux.

.. code-block:: console
    
  source /usr/local/bin/virtualenvwrapper.sh

.. hint:: 

	Depending on the process used to install *virtualenv*, the path to virtualenvwrapper.sh may vary. Find the approporiate path by running ``$ find /usr -name virtualenvwrapper.sh``. Adjust the line in your .bash_profile or .bashrc script accordingly.


Open a new shell to make the new virtual environment available. Now we are ready to create a virtual environment.  You can choose any name for your virtual environment, here we name it |projname|:

.. code-block:: console

   $  mkvirtualenv -p <path to python>/python MOSAIC


.. hint::
	
	We explicitly specify the Python_ installation to use. This is not mandatory, but is useful if you have multiple Python_ installations on your computer. The `<path to python>` may vary according to the specific version of python you wish to use. In most cases, this will be either `/usr/local/bin/` or `/usr/bin`