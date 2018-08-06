.. _configuration:


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


Configuration
-------------
-------------

In order to make a simulation run with SEDobs, a configuration file must be filled. An example is given below:

.. code-block:: shell

    [General]
    Project_name=
    Author= 
    Project_Directory= 
    full_array=
    z_distribution= 
    Nobj= 
    filter_file= 

    [Data_Type]
    Photometry= 
    Spectro= 

    [Spectro]
    NSpec= 
    Norm_band= 
    Noise_reg= 
    Norm_distribution= 
    types= 

    [Photo]
    Norm_band= 
    Norm_distribution= 
    Nband= 
    Band_list= 

    [Cosmo]
    Ho=
    Omega_m= 
    Omega_L= 
    Use_Cosmo= 

    [Templates]
    BaseSSP= 
    DustUse= 
    EBVList= 
    IGMUse= 
    IGMtype= 
    EMline= 
    Lyafrac= 
    Age= 
    TAU= 
    MET= 


This configuration file is composed of 6 mandatory sections. If one is missing, SEDobs can not run. We detail them below.


General
^^^^^^^




Data_type
^^^^^^^^^
This is where you tell SEDobs what kind of data you will use. Two entries are given: Photometry and Spectroscopy. If you want both of them you must write 'Yes' for each of them. If you just want one type, you must write 'Yes' to the one you want and 'No' to the other one. Example:

.. code-block:: shell

    [Data_Type]               [Data_Type]              [Data_Type]
    Photometry = Yes          Photometry = Yes         Photometry = No
    Spectro = No              Spectro = Yes            Spectro = Yes

Of course, if you put two 'No', SEDobs will not simulate anything.


 

Spectro
^^^^^^^

Photo
^^^^^

Cosmo
^^^^^
This part deals with the cosmological model used by SEDobs. When simulating a galaxy at redshift **z**, SEDobs is able to take into account a cosmological model. This means that at **z**, the template used for the simulation will be younger that the age of the Universe at **z** in the cosmological model you want use. The cosmological model is given by 3 parameters: the Hubble constant Ho and two comological parameters: the dark energy density: omega_L and the matter density parameter: omega_m. SEDobs checks that Omega_m + Omega_L =1. If not it will comnplain. If you want SEDobs to be able to use templates older than the age of the Universe at a given **z**, you can say 'No' to Use_Cosmo.
An example of this section is given below:

.. code-block:: shell

    [Cosmo]
    Ho=70
    Omega_m=0.27
    Omega_L=0.73
    Use_Cosmo=Yes



Templates
^^^^^^^^^

