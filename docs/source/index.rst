.. SEDSIM documentation master file, created by
   sphinx-quickstart on Tue Jul 24 12:34:41 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to SEDobs's documentation!
==================================

|Python36| |Licence| |zenodo| |numpy| |scipy| 

.. |Licence| image:: https://img.shields.io/badge/License-GPLv3-blue.svg
      :target: http://perso.crans.org/besson/LICENSE.html

.. |Opensource| image:: https://badges.frapsoft.com/os/v1/open-source.svg?v=103
      :target: https://github.com/ellerbrock/open-source-badges/

.. |zenodo| image:: https://zenodo.org/badge/142183334.svg
   :target: https://zenodo.org/badge/latestdoi/142183334

.. |Python36| image:: https://img.shields.io/badge/python-3.6-blue.svg
.. _Python36: https://www.python.org/downloads/release/python-360/

.. |numpy| image:: https://img.shields.io/badge/poweredby-numpy-orange.svg
   :target: http://www.numpy.org/

.. |scipy| image:: https://img.shields.io/badge/poweredby-scipy-orange.svg
   :target: https://www.scipy.org/

.. figure:: ./pics/Logo.png
    :width: 750px
    :align: center


Content
=======

.. toctree::
   :maxdepth: 1

   Home <self>
   installation
   usage
   configuration
   atmospheric
   tests
   photo
   Spectro
   MultiSpectro
   full
   output 


What is SEDobs?
===============
SEDobs is a program that aims at using state of the art theoretical gelaxy SED (spectral energy distribution) to create simulated observation of distant galaxies. It used BC03 and M05 theoretical models and allows the user to configure the simulated observation that are needed. For a given simulated galaxy, the user is able to simulate multi-spectral and multi-photometric observations. Number of inputs are needed and described in :doc:`configuration`. The outputs are very easy and directly usable, they are described in :doc:`output`. To get started with the use of SEDobs you must install it :doc:`installation`. And carefully look at the :doc:`usage` and :doc:`configuration` pages to understand how to use it. 

---- 

SEDobs has been accepted for Publication in Astronomy and Computing! More details to come!

----

**Contribute!**
SEDobs is not perfect! It has been primarily developed for my private research and I decided to release in the spirit of making the research process as transparent as possible and in the hope it can be used by other people. If you have any comment or anything you would like to be added to SEDobs, or, even better, if you want to modify you can either do it yourself or  please feel free to contact us! ---> @ **the.spartan.proj@gmail.com**

----

.. warning::
 
	**Copyright**
 
	SEDobs is a free software: you can redistribute it and/or modify it under 
	the terms of the GNU General Public License as published by the Free Software Foundation, 
	version 3 of the License.
 
	SEDobs is distributed without any warranty; without even the implied warranty of merchantability 
	or fitness for a particular purpose.  See the GNU General Public License for more details.
 
	You should have received a copy of the GNU General Public License along with the program.
	If not, see http://www.gnu.org/licenses/ .

