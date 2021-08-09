.. _gettingstarted:

Getting Started
===============

Binary Installation
---------------------------------------------------


|projname| is available as a pre-compiled binary for Windows and Mac OS X (`download binaries`_). |projname| binaries do not need special installation. Under **Mac OS X** open the the downloaded disk image and drag the |projname| executable to the Applications folder. Under **Windows**, unzip downloaded zip file and move the |projname| executable to your hard disk. 

.. note::
	|projname| binaries are 64-bit. If you need 32-bit support, please build |projname| from source as described in the :ref:`sourceinstall` section.


.. _sourceinstall:

Source Installation
---------------------------------------------------

.. only:: latex

		.. include:: InstallOSX.rst


		.. include:: InstallUbuntu.rst


		.. include:: InstallWindows.rst


.. only:: html
	
	Install |projname| from source following the instructions for your platform below.


		:ref:`installosx`


		:ref:`installubuntu`


		:ref:`installwin`


.. _dockerinstall:

Docker Installation
---------------------------------------------------

|projname| can be installed using `Docker Desktop`_. This may be desirable in many cases because it provides a consistent experience across all operating systems. Installing |projname| using Docker is relatively straightforward and requires only a few steps as described below.


**1. Install Docker Desktop**

Download and install `Docker Desktop`_. Follow instructions for either `Windows <https://docs.docker.com/docker-for-windows/install/>`_ or `Mac OS X <https://docs.docker.com/docker-for-mac/install/>`_ installation.


**2. Create a configuration file** 

Copy the text below and paste into a file called ``docker-compose.yml.``

.. note::
	The filename and extension should be ``docker-compose.yml.``

Modify the data path and log file paths under the ``volumes`` line appropriately for your PC. 

Also note the version number in the ``image`` line.

Place the ``docker-compose.yml`` anywhere on your PC.


.. code-block:: yaml
    
  version: '3'
  services:
  mosaic:
    image: ghcr.io/usnistgov/mosaic:v2.2
    ports:
        - "5000:5000"
    volumes:
        - C:\\Users\\arvind\\Desktop:/src/data
        - C:\\Users\\arvind\\Desktop:/var/logs

**3. Run MOSAIC using Docker** 

Open the ``Command Prompt`` in Windows or ``Terminal`` on Mac OS. 

.. hint::
	You can launch the ``Command Prompt`` by typing ``cmd`` in the search bar on Windows.


In the ``Command Prompt``, navigate to the directory that you placed the ``docker-compose.yml`` file. For example if you place the file at ``C:\\Users\\arvind\Desktop`` then type:
	
.. code-block:: console

	c:
	cd Users\arvind\Desktop

Run the Docker |projname| image by typing:

.. code-block:: console

	docker compose up


You should see Docker download the image file and start |projname| similar to the figure below

.. figure:: ../images/Docker_CMD.png
  :width: 85 %
  :align: center


**4. Run MOSAIC Web UI**

Open a browser and type ``localhost:5000`` in the address bar. This should load the MOSAIC web UI as shown below.

.. figure:: ../images/Docker_Browser.png
  :width: 85 %
  :align: center



.. include:: ../aliases.rst