.. _Usage:


|Python36| |Licence| |numpy| |scipy| 

.. |Licence| image:: https://img.shields.io/badge/License-GPLv3-blue.svg
      :target: http://perso.crans.org/besson/LICENSE.html

.. |Opensource| image:: https://badges.frapsoft.com/os/v1/open-source.svg?v=103
      :target: https://github.com/ellerbrock/open-source-badges/

.. |Python36| image:: https://img.shields.io/badge/python-3.6-blue.svg
.. _Python36: https://www.python.org/downloads/release/python-360/

.. |numpy| image:: https://img.shields.io/badge/poweredby-numpy-orange.svg
   :target: http://www.numpy.org/

.. |scipy| image:: https://img.shields.io/badge/poweredby-scipy-orange.svg
   :target: https://www.scipy.org/


Getting started
---------------
---------------

First start up
^^^^^^^^^^^^^^

Once you installed SEDobs, you can start it with the sedobs command. Since it is your first start it will ask you to give the absolute path of the input SEDobs files directory. This files are crucial for the functionning of SEDobs (see :doc:`configuration` page for more information). Once you write it sedobs will create a folder in the home directory: **~/.sedobs**. This folder will contain the path to these external files, as well as the files for the test runs.  


The command line interface
^^^^^^^^^^^^^^^^^^^^^^^^^^

You start SEDobs from a terminal. SEDobs comes with a command line interface which includes a 'help' that you can display in your terminal using the help command. It must be called like this::

           [user@machine]$ sedobs --help

This command will display the help of the program::

      usage: sedobs [-h] [-p PROJECT] [--docs] [--version]

      SEDobs, R. Thomas, 2018, This program comes with ABSOLUTELY NO WARRANTY; and
      is distributed under the GPLv3.0 Licence terms.See the version of this Licence
      distributed along this code for details. website: 
      https://astrom-tom.github.io/SEDSIM/build/html/index.html

      optional arguments:
      -h, --help            Show this help message and exit
      -p PROJECT, --project PROJECT
                            Input configuration file
      --test                If you wanna try the test run of SEDobs
      --docs                Open the doc in web browser
      --version             Display version of photon.

In details it means:

SEDobs has 5 optionnal arguments. You can start SEDobs without any argument. Few arguments can be used:
	
* -h: Display this help in the terminal.
* -p or --project: Takes an configuration file as input. 
* use - -test: This is to run the test configuration of SEDobs. It is one already given with the code. SEDobs will ask you what kind of configuration you want to run: photo, spectro, multi-spectro or full (multi-spectroscopy and multi-photometry)
* use - -docs: Display in the web browser the documentation of the code. If you have a valid internet connection it will open the online documentation, if not it will open the local documentation.
* use - -version: Display in terminal the current version of the software.

The command line interface is made using the argparse library (part of the standard python library).




