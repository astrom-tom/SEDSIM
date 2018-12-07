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
 
        **Input Files**
 
        SEDobs relies on numerous inputs that are pre-computed (e.g. Stellar Population, IGM extinction, etc). To make use of them you must download them at this `link <https://drive.google.com/open?id=0B6RLimXliDkhOG93ZzRSSDhvUUE>`_ 
        These are not being computed on the fly which save a lot of time in the simulating process. See details below on how to use them. 


In order to make a simulation run with SEDobs, a configuration file must be filled. An example is given below (filled fields are default values):

.. code-block:: shell

	[General]
	Project_name = 
	Author =
	Project_Directory= 
	full_array =  
	z_distribution = 
	Nobj =  
	sizegal = 

	[Data_Type]
	Photometry = 
	Spectro = 

	[Spectro]
	NSpec = 
	Norm_band = 
	Noise_reg =  
	Norm_distribution = 
	types = 
	flux_unit = 
	wave_unit = 

	[Photo]
	Norm_band = 
	Norm_distribution = 
	Nband = 
	Band_list = 
	flux_unit = muJy
	wave_unit = log_ang
	savesky = No

	[Cosmo]
	Ho=70
	Omega_m = 
	Omega_L = 
	Use_Cosmo = 

	[Templates]
	BaseSSP = 
	DustModel = 
	AvsList = 
	RvsList = 
	IGMUse = 
	IGMtype = 
	EMline= 
	EBVnList =
	Lyafrac = 
	Age = 
	TAU = 
	MET =  


This configuration file is composed of 6 mandatory sections. If one is missing, SEDobs can not run. We detail them below.


General
^^^^^^^
The general section is the first of the configuration file. It is composed of 7 entries:

* **Project_name**: This is the name of your project. All the files created in the :doc:`output` writing part of the code will use this name as prefix. For example if you name your project 'my_simulation', all the files will start by ''my_simulation+ending.txt''. **It must not contain any space.**

* **Author**: This is your name. Here you can write whatever you want (like name + date). This is not use anywhere in the code. **It is more for a personnal note**.

* **Project Directory**: This is the (absolute) path of the directory where you want SEDobs to write all the outputs. Usually it is the directory where the configuration file is located. All the files an directory that are created by SEDobs will be written in that directory.

* **full_array**: This is a file containing all the properties of the galaxies you want to simulate. This is optionnal (redshift, normalisation magnitude and signal to noise ratios). SEDobs will simulate exactly what is in this file. See the tutorial for more informations.

* **z_distribution**: Only if you do not use the previous ''full_array'' option. This file contains the distribution of redshift you want to mimick. It is a one column catalog with redshift values (with 4 decimal maximum). 

* **Nobj**: Only if you do not use the previous ''full_array'' option.  This is the number of objects you want SEDobs to create. This needs of course to be used with the **z_distribution** option. If the catalog given in the z_distribution option contains 500 redshifts and that you give N_obj=5000, SEDobs will create a redshift distribution of 5000 object with the same shape as your input redshift distribution. 

* **sizegal**: Averaged angular size of the galaxies that will be simulated, in arcsec. This is used to scale up the OH skyline spectrum (see :doc:`atmospheric` for more details). The default size is 1''.

An example of the version with the **full_array** option:

.. code-block:: shell

    [General]
    Project_name= Test_run_v2
    Author= R. THOMAS
    Project_Directory= /home/alien/Documents/SEDOBS/TESTS
    full_array = final_array_z_StN_mag.txt
    z_distribution =
    Nobj =
    sizegal = 1

An example without it:

.. code-block:: shell

    [General]
    Project_name= Test_run_v2
    Author= R. THOMAS
    Project_Directory= /home/alien/Documents/SEDOBS/TESTS
    full_array = 
    z_distribution = redshift.txt
    Nobj = 10000
    sizegal = 1


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

* **Norm_band**: This is the band SEDobs will use to normalise the selected model to the observed magnitude. It is a name of a filter (see :doc:`filters` page for all the filters available), an atmosphere range and a sky subrtaction estimation (see below).
* **Norm_distribution**: Only if you do not use the previous **full_array** option. This is the magnitude distribution SEDobs will use to create your data. It is a one column only file with magnitude values (AB) in the same band you gave in the **Norm_band** entry.
* **Nband**: The number of photometric band you want to be computed for a given simulation.
* **Band_list**: This is where you give the photometric configuration for each band. For each of them you must give multiple information **(name,offset,mean,sigma,atm,skysub)**:

    * **name**: This is the name of the filter
    * **offset**: This is the offset of the band (in magnitude) that will be applied in all the magnitudes
    * **mean** and **sigma**: To compute the errors on the band, SEDobs created a gaussian and randomely select in that gaussian to create the simulated error. You must give for each band the mean and sigma of that gaussian.
    * **atm**: This let SEDOBS know if this band is affected by atmsopherical effects. It can take four values: none, low, int, high (see :doc:`atmospheric` for details).
    * **skysub**: A number between 0 and 100. This is your estimation of the sky substraction efficiency (100[%] means perfect substraction, 0[%] means no sky is substracted). See :doc:`atmospheric` for more details.

* **flux_unit**: This is the unit of the output photometry. If empty it will be erg/s/cm2/A. You can also give *Jy* and *muJy* (micro Jensky).
* **wave_unit**: This is the unit of the wavelength of the output photometry. If empty it will be Angstrom. You can also give *log_ang* to get directly the logarithm (base 10) of the wavelength.
* **savesky**: Yes or No. This is if you want to save the full OHlines spectrum (this can take some disk space, to use wisely).

An example is given below, without full array:

.. code-block:: shell

    Norm_band = (r-megacam,low,98)
    Norm_distribution = magnorm.txt
    Nband = 10
    Band_list = (u-megacam,0.0,0.31,0.38,low,98);(g-megacam,0.0,0.15,0.20,low,98);(r-megacam,0.0,0.19,0.09,low,98);
    (i-megacam, 0.0, 0.23, 0.12,low,98);(z-megacam,0.0, 0.38, 0.19,low,98);(J-wircam, 0.0, 0.68, 0.45,low,99.5);
    (H-wircam,0.0,0.71,0.37,low,99.5);(K-wircam,0.0,0.55,0.41,low,99.5);(IRAC1,0.0,0.08,0.04,none,100);
    (IRAC2,0.0,0.09,0.06,none,100)


And with it

.. code-block:: shell

    Norm_band = (r-megacam,low,98)
    Norm_distribution = 
    Nband = 10
    Band_list = (u-megacam,0.0,0.31,0.38,low,98);(g-megacam,0.0,0.15,0.20,low,98);(r-megacam,0.0,0.19,0.09,low,98);
    (i-megacam, 0.0, 0.23, 0.12,low,98);(z-megacam,0.0, 0.38, 0.19,low,98);(J-wircam, 0.0, 0.68, 0.45,low,99.5);
    (H-wircam,0.0,0.71,0.37,low,99.5);(K-wircam,0.0,0.55,0.41,low,99.5);(IRAC1,0.0,0.08,0.04,none,100);
    (IRAC2,0.0,0.09,0.06,none,100)


Spectro
^^^^^^^
This is where you precise the spectroscopic information of the simulations. Seven entries are needed:

* **NSpec**: This is the number of spectroscopy per simulated galaxy you want to create. For a given template, randomely chosen in the library, you can ask to have 1, 2 or N spectra to be created (for example sdss-like and HST-like).
* **Norm_band**: For each spectrum that you want to create you must tell SEDobs in what band you want to normalize it. As in the case of photometry (see above) you must give the name of a filter, atmospheric range and a skysubstraction efficiency estimation.
* **Noise_reg**: This is a region free of emission lines where the SNR will be adjusted. It is given in angstrom.
* **Norm_distribution**: Only if you do not use the **full_array** option. You must give the normalisation file (see above for photometry). 
* **types**: This is where you give the spectroscopic configuration. For each spectrum you want to simulate, you must give: **l1, l2, dl, R [,SNR.txt], atm, skysub**:
    
    * **l1**: The starting wavelength of your spectrum
    * **l2**: The end wavelength of your spectrum
    * **dl**: The delta lambda of your spectrum
    * **R**: The spectral resolution of your spectrum
    * **SNR.txt**: Only if you do not use the **full_array** option. The file containing the Signal to noise ratio distribution (one column catalog).
    * **atm**: This let SEDOBS know if this spectrum is affected by atmsopherical effects. It can take four values: none, low, int, high (see :doc:`atmospheric` for details).
    * **skysub**: A number between 0 and 100. This is your estimation of the sky substraction efficiency (100[%] means perfect substraction, 0[%] means no sky is substracted). See :doc:`atmospheric` for more details.

* **flux_unit**: This is the unit of the output spectrum. If empty it will be erg/s/cm2/A. You can also give *Jy* and *muJy* (micro Jensky).
* **wave_unit**: This is the unit of the wavelength of the output spectrum. If empty it will be Angstrom. You can also give *log_ang* to get directly the logarithm (base 10) of the wavelength.

You must repeat that for each spectrum.

An example of this section is given below without full array option.

.. code-block:: shell

    	[Spectro]
	NSpec = 2 
	Norm_band = (r-megacam,low,98);(J-wircam,none,100)
	Noise_reg =  (1080,1170);(3600,3700)
	Norm_distribution = dist_mag.txt 
	types = (3500,9500,7.25,240,dist_SNR1.txt,low,90);(12000,15000,50,100,dist_SNR2.txt,none,100)
	flux_unit = 
	wave_unit =


And with it

.. code-block:: shell

    	[Spectro]
	NSpec = 2 
	Norm_band = (r-megacam,low,98);(J-wircam,none,100)
	Noise_reg =  (1080,1170);(3600,3700)
	Norm_distribution = dist_mag.txt 
	types = (3500,9500,7.25,240,low,98);(12000,15000,50,100,none,100)
	flux_unit = 
	wave_unit =


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
This is the section where you tell SEDobs what kind of templates you want to choose from to make the simulations. In order to speed-up the simulation process different types of templates and extinction have been pre-computed. You must download these files `here <https://drive.google.com/open?id=0B6RLimXliDkhOG93ZzRSSDhvUUE>`_. Be carefull of the file size as some files are more than 1Gb. The directories are: 

    * Directory EXT: Contains different dust extinction laws. You can freely add yours.
    * Directory EmLine: Contains emission lines related files.
    * Directory IGM: Contains all the IGM curves (in HDF5 format).
    * Directory LIBS: Contains pre-computed CSPs with different SFH, IGM and metallicities.
    * Directory Atmos: Contains pre-computed sky emission spectra.
    * File: SPARTAN_filters.hdf5 contains all the photometric filters curves.

It is very important to keep all these directories in the same parent directory (SEDobs has relative paths to that parent directory hardcoded). The layout should look like this:

.. code-block:: shell
    
    Parent_directory 
        |_IGM
        |_EXT
        |_LIBS
        |_EmLine
	|_Atmos
        |_SPARTAN_filters.hdf5

The path to the parent directory is the one you have to give when you start the SEDobs for the first time (see :doc:`usage`).

Once you have all the extra input files you can fill the template section:

* **BaseSSP**: This is the basic files with pre-computed templates. They are located in the LIBS input directory. Their format are LIB_BC03_[ SFH type ]_[ Resolution ]_[ IMF ]_SPARTAN.hdf5.

    * SFH type are for the moment exponentially delayed and exponentially declining.
    * Resolution: LR = low resolution; HR = high resolution 
    * IMF:  Chab for Chabrier IMG, Salp for Salpeter IMF.

* **Dust Use**: The dust extinction files that you want to use (located in the EXT directory).
* **IGMUse**: The IGM prescription you want to use. You can choose from Meiskin+06 and Madau+95.
* **IGMtype**: The type of IGM you want to use. Both previous extinction have been upgraded to allow 7 different IGM curves at a given redshift (see Thomas+17a). Here you can say **mean** or **free**. Mean means that you just want to use the mean IGM value at each redshift, free means that you allow SEDobs to apply one of the 7 IGM transmission curves at any redshift. Each file in the IGM directory contain all the 7 curves at any redshift from 1.5 to 7 (so 5500 redshift x 7 curves = 38500 curves).
* **EmLine**: yes or no if you want to add emission line to your templates (Presription of Schaerer+05).
* **LyaFrac**: As the Lyman alpha line can be both in emission and absorption we leave the user the choice of fraction of Lyman alpha emitters in the simulation. If you enter 1, it means that Lyman alpha will always be added to the template. If you put 0, it will never be added. If you write 0.5 it will be added 50% of the time. 

Physical parameters:
Each pre-computed library comes with already defined range of values for the galactic ages, SFH timescales amd metallity.

* **Age**: The ages that you want SEDobs to consider. The range of age is defined from 1e+06yr to 1.5e+10yr. You can five any age between these two limits. SEDobs will interpolate between the existing ages to match your list.
* **TAU**: The same as for the ages. TAUs are defined (for both delayed and declining) from 0.1Gyr to 9.9Gyr. You can give any values between these two limits.
* **MET**: Unlike the other parameters, SEDobs will not interpolate between existing values. Therefore you have to give one (or more) of these metallicites (in Z(solar) unit): 0.02;0.2;0.4;1.0;2.5.
* **EBVList**: The color excess values you want to apply. They must be positive (or equal to 0). 
* **AvsList**:  Total extinction in the V band. Must be positive.
* **RvsList**:  optical to selective extinction ratio (with Rv = Av/E(b-v))

For each list of parameters you have to separate values by ';' wihout spaces.

En example of such section is given here:

.. code-block:: shell

    	[Templates]
	BaseSSP = LIB_BC03_Delayed_LR_Salp_SPARTAN.hdf5
	DustModel = calzetti.dat
	DustUse_ste = yes
	AvsList = 0.0;0.4050;0.8100;1.2149;1.6200;2.0250
	RvsList = 4.05
	IGMUse = SPARTAN_Meiksin_Free_7curves.hdf5
	###IGM type free or mean or empty
	IGMtype = free 
	EMline= yes
	EBVnList =
	Lyafrac = 0.5
	Age = 0.5e+08;0.75e+08;0.1e+09;0.2e+09;0.3e+09;0.4e+09;0.5e+09;0.6e+09;0.7e+09;0.8e+09;0.9e+09;1.0e+09;1.0e+09;1.1e+09;1.2e+09;1.3e+09;1.4e+09;1.5e+09
	TAU = 0.10;0.2;0.3;0.4;0.5;0.6;0.7;0.8;0.9;1.0
	MET = 0.4;1.0;2.5



