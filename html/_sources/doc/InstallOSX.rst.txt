.. _installosx:

Install |projname| on Mac OS X
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the following guide, we provide step-by-step instructions on setting up and running |projname| on OS X. To simplify the isntallation, we use Homebrew_ to install some required dependencies. Homebrew_  
requires Apple command line tools, but will directly prompt you to install it on set up.

**1. Installing Homebrew**

First we will install Homebrew, a useful package manager, to help install some of the dependencies required by |projname|. You will need administrator access for this step. In the OS X Terminal, run the following command:

.. code-block:: console

  $  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"


Note, if the Apple command line tools are not installed, Homebrew_ will prompt you do so during installation. 

.. hint:: To test if Homebrew_ is properly installed, run the following in the terminal: ``brew doctor`` 

To ensure that Homebrew_ is set up correctly, add the Homebrew_ directory to ~/.bash_profile. This can be done using the following command:

.. code-block:: console

  $  echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bash_profile

.. hint::  If you don't have a .bash_profile file in your home directory, you can create one manually using a text editor. 

Restart the terminal to update your shell.


**2. Installing brewed Python and other neccessary packages**


|projname| is written in Python_ 2.7+ and utilizes a number of different packages and utilities. In the following we'll install a number of these (specifically, python, gcc, gfortran, qt, and pyQt4). With homebrew this is easy to do in one line! Run the following in the terminal:

.. code-block:: console
    
  $  brew install python gcc gfortran qt pyqt

At this point, it is a good idea to update the PYTHONPATH environment variable in ~/.bash_profile:

.. _setPYTHONPATHOSX:

.. code-block:: console
  
   $  export PYTHONPATH=$PYTHONPATH:/usr/local/lib/python2.7/site-packages


**3. (Optional) Install and Setup Virtual Environment**

.. include:: InstallVirtualenv.rst

**4. Installing MOSAIC**

.. include:: InstallMosaicSource.rst   
