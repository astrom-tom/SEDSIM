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

.. warning::
 
        **Input Data**
 
        SEDobs relies on numerous input that are pre-computed (e.g. Simple Stellar Population, IGM extinction, etc). To make use of them you must download them at this link: 
        These are not being computed on the fly which save a lot of time in the simulating process. See details below on how to use them. 


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
The general section is the first of the configuration file. It is composed of 7 entries:

* **Project_name**: This is the name of your project. All the files created in the :doc:`output` writing part of the code will use this name as prefix. For example if you name your project 'my_simulation', all the files will start by ''my_simulation+ending.txt''. **It must not contain any space.**

* **Author**: This is your name. Here you can write whatever you want (like name + date). This is not use anywhere in the code. **It is more for a personnal note**.

* **Project Directory**: This is the (absolute) path of the directory where you want SEDobs to write all the outputs. Usually it is the directory where the configuration file is located. All the files an directory that are created by SEDobs will be written in that directory.

* **Nobj**: This is the number of objects you want SEDobs to create. Here you have to be careful. If you give a full array (see above), this parameter will not be taken into account. And SEDobs will simulate the number of object you have in the full_array file. 

* **filter_file**: This file is one of the additional data of SEDobs that you MUST download. You can download it here :download:`SEDobs_filters.hdf5 <./files/SEDobs_filters.hdf5>`. It contains more than 100 filters. You can find details in the :doc:`filters` page.


Data_type
^^^^^^^^^
This is where you tell SEDobs what kind of data you will use. Two entries are given: Photometry and Spectroscopy. If you want both of them you must write 'Yes' for each of them. If you just want one type, you must write 'Yes' to the one you want and 'No' to the other one. Example:

.. code-block:: shell

    [Data_Type]               [Data_Type]              [Data_Type]
    Photometry = Yes          Photometry = Yes         Photometry = No
    Spectro = No              Spectro = Yes            Spectro = Yes

Of course, if you put two 'No', SEDobs will not simulate anything.

Photo
^^^^^
This is where you tell SEDOBS what photometric data to simulate:

* **Norm_band**: This is the band SEDobs will use to normalise the selected model to the observed magnitude. It is a name of a filter (see :doc:`filters` page for all the filters available).
* **Norm_distribution**: If you are not using the full_array option, the is the magnitude distribution SEDobs will use to create your data. It is a one column only file with magnitude values (AB) in the band you gave in the **Norm_band** entry.
* **Nband**: The number of photometric band you want to be computed for a given simulation.
* **Band_list**: This is where you give the photometric configuration for each band. For each of them you must give multiple information **(name,offset,mean,sigma)**:

    * **name**: This is the name of the filter
    * **offset**: This is the offset of the band (in magnitude) that will be applied in all the magnitudes
    * **mean** and **sigma**: To compute the errors on the band, SEDobs created a gaussian and randomely select in that gaussian to create the simulated error. You must give for each band the mean and sigma of that gaussian.

An example is given below:

.. code-block:: shell

    Norm_band = r-megacam
    Norm_distribution = magnorm.txt
    Nband = 10
    Band_list = (u-megacam,0.0, 0.31, 0.38);(g-megacam,0.0,0.15,0.20);(r-megacam,0.0,0.19,0.09);(i-megacam, 0
    .0, 0.23, 0.12);(z-megacam,0.0, 0.38, 0.19);(J-wircam, 0.0, 0.68, 0.45);(H-wircam, 0.0, 0.71,0.37);(K-wir
    cam,0.0,0.55, 0.41);(IRAC1,0.0,0.08, 0.04);(IRAC2,0.0,0.09,0.06)



Spectro
^^^^^^^
This is where you precise the spectroscopic information of the simulations. Five entries are needed:

* **NSpec**: This is the number of spectroscopy per simulated galaxy you want to create. For a given template, randomely chosen in the library, you can ask to have 1, 2 or N spectra to be created (for example sdss-like and HST-like).
* **Norm_band**: For each spectrum that you want to create you must tell SEDobs in what band you want to normalize it. As in the case of photometry (see above), you must give an offset, and information about errors on that band. 
* **Noise_reg**: This is a region free of emission lines where the SNR will be adjusted. It is given in angstrom.
* **Norm_distribution**: You must give the normalisation file (see above for photometry). If you use the full_array option this can be ignored. 
* **types**: This is where you give the spectroscopic configuration. For each spectrum you want to simulate, you must give: **l1, l2, dl, R, SNR.txt**:
    
    * **l1**: The starting wavelength of your spectrum
    * **l2**: The end wavelength of your spectrum
    * **dl**: The delta lambda of your spectrum
    * **R**: The spectral resolution of your spectrum
    * **SNR.txt**: The file containing the Signal to noise ratio distribution

You must repeat that for each spectrum.

An example of this section is given below.

.. code-block:: shell

    [Spectro]
    NSpec = 2 
    Norm_band = (i-megacam,0.0, 0.1, 0.03);(J-wircam, 0.0, 0.2, 0.08)
    Noise_reg = (1080,1170);(3580,3680)
    Norm_distribution = magnorm.txt
    types = (3500,9500,7.25,240,opt.txt);(12000,16000,46.5,130,NIR.txt)


Cosmo
^^^^^
This part deals with the cosmological model used by SEDobs. When simulating a galaxy at redshift **z**, SEDobs is able to take into account a cosmological model. This means that at **z**, the template used for the simulation will be younger that the age of the Universe at **z** in the cosmological model you want use. The cosmological model is given by 3 parameters: the Hubble constant Ho and two comological parameters: the dark energy density: omega_L and the matter density parameter: omega_m. SEDobs checks that Omega_m + Omega_L =1. If not it will complain. If you want SEDobs to be able to use templates older than the age of the Universe at a given **z**, you can say 'No' to Use_Cosmo. This way, SEDobs will randomely choose templates in the set of template, regardless of their age.
An example of this section is given below:

.. code-block:: shell

    [Cosmo]
    Ho=70
    Omega_m=0.27
    Omega_L=0.73
    Use_Cosmo=Yes



Templates
^^^^^^^^^

