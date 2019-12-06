.. _Spectroscopic simulations:


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


Multi-Spectroscopic Simulation
------------------------------

.. note::

    This exact run can be started in the test of SEDobs. if you hit the command **sedobs -- --test** and select the multispectro simulation sedobs will run exactly this configuration.


Configuration
^^^^^^^^^^^^^

We describe here the process the SEDobs uses when doing a purely spectroscopic simulation with N=2 spectra per galaxy. This will work of course with higher N.
The configuration we use is the one given below (named: SEDobs_Test_run_multispectro.conff):

.. code-block:: shell

	[General]
	Project_name= SEDobs_Test_run_multispectro
	Author = R. THOMAS - 6/12/18
	Project_Directory= ~/.sedobs/test_run_multispectro
	full_array =  
	z_distribution = dist_zspec_multi.txt
	Nobj = 2500 
	sizegal = 1

	[Data_Type]
	Photometry = No
	Spectro = Yes

	[Spectro]
	NSpec = 2 
	Norm_band = (r-megacam,low,98);(J-wircam,none,100)
	Noise_reg =  (2900,3200);(8000,8200)
	Norm_distribution = dist_mag.txt 
	types = (3500,9500,7.25,240,dist_SNR1.txt,low,98);(12000,15000,50,100,dist_SNR2.txt,none,100)
	flux_unit = muJy
	wave_unit = log_ang

	[Photo]
	Norm_band = 
	Norm_distribution = 
	Nband = 
	Band_list = 
	flux_unit = 
	wave_unit =
	savesky = 

	[Cosmo]
	Ho=70
	Omega_m = 0.27
	Omega_L = 0.73
	Use_Cosmo = Yes

	[Templates]
	BaseSSP = LIB_BC03_Delayed_LR_Salp_SPARTAN.hdf5
	DustModel = calzetti.dat
	AvsList = 0.0;0.4050;0.8100;1.2149;1.6200;2.0250
	RvsList = 4.05
	IGMUse = SPARTAN_Meiksin_Free_7curves.hdf5
	IGMtype = free 
	EMline= yes
	EBVnList =
	Lyafrac = 0.5
	Age = 0.5e+08;0.75e+08;0.1e+09;0.2e+09;0.3e+09;0.4e+09;0.5e+09;0.6e+09;0.7e+09;0.8e+09;0.9e+09;1.0e+09;1.0e+09;1.1e+09;1.2e+09;1.3e+09;1.4e+09;1.5e+09
	TAU = 0.10;0.2;0.3;0.4;0.5;0.6;0.7;0.8;0.9;1.0
	MET = 0.4;1.0;2.5

We choose to use individual files (and not the full_array option). 

Checking configuration
^^^^^^^^^^^^^^^^^^^^^^

We start sedobs with this file (*sedobs -p SEDobs_Test_run_multispectro.conf*) sedobs start by checking your configuration. You can see the output of the terminal for the full checking of your configuration:

.. figure:: ./pics/multispec_check.png
    :width: 750px
    :align: center
    :alt: GUI

* **1-General section checking**:  First it tells you what file you loaded. Then it checks the general section of the configuration file. It makes sure that your directory exist and that the filter file is found. Since we do not give a full array, it assumes we give individual distribution (in the spectroscopic case the redshift distribution, normalisation magnitude distribution and SNR distribution). It checks that the redshift distribution is found and that the number of objects is given. In the project directory you will have this files (of course this has to be adapted to your project):

.. code-block:: shell

    Project Directory
	|_SEDOBS.conf
        |_dist_zspec_multi.txt
        |_dist_mag.txt
	|_dist_SNR1.txt
	|_dits_SNR2.txt

* **2-Check data type**: Then SEDobs check what type of data you want to simulate, in this case single spectroscopy
* **3-Check Cosmology module**: The cosmology configuration is verified
* **4-Check the spectroscopic configuration**: SEDobs then start to check the spectroscopic configuration. It checks the number of spectra that will be simulated per galaxy, also the normalisation band (and magnitude distribution).  It will check that a SNR distribution is given per simulated spectrum (2 simulated spectra --> 2 distributions of SNR). Finally it will check that the types of spectra are given as well as the noise regions.
* **5-Check template configuration**: Then SEDobs look at your template setting. It checks that all the input files are found (IGM, dust extinction, templates).

Preparation
^^^^^^^^^^^

After this checks, SEDobs is going to prepare the extra files:
    * The final redshift, normalisation magnitude and SNR distributions. From the four files given (see above), four new distributions will be created, matching the shape of the original ones with the number of object you want to create. Examples are given below for this run:

.. figure:: ./pics/multispec_all.png
    :width: 750px
    :align: center
    :alt: GUI


These four distributions will be joined in one file called 'final_array_z_StN_mag.txt' and placed in your project directory. This file can be re-used for another run using the *final array option*.

    * From the Ages, Tau and metallicities that you give in your configuration SEDobs recompute a library of templates and save it in *SEDobs_Test_run_multispectro.hdf5* (this name depends on the name of your project). 

    * SEDobs starts to create the output files (with header). In this case it will be the parameter file, and the photometric (list of spectrum, redshift, normalisation magnitude) file. It also creates the spectra and original_template sub-directories

.. warning::
    if you change some of the template parameters (Age, Tau, met) you must delete the *.hdf5 file that was created previously because SEDobs try to look for an already computed library of template before creating one.
    It is the same for the *final_array_z_StN_mag.txt* file. If you change your redshift distribution of your normalisation band distribution you have to delete this file. SEDobs try to look for it to check if one is already here. If it finds it it will not recalculate it. 

	

Simulation
^^^^^^^^^^
After all these checking and preparations SEDobs starts to simulate. It will go throught the final_array_z_StN_mag.txt, one object at a time. For each object, SEDobs passes by different steps that are displayed in the terminal, an example is given below:

.. figure:: ./pics/multisimobj.png
    :width: 950px
    :align: center
    :alt: GUI

SEDobs start to take the library of templates that was created and adds emission lines. If you asked to give a certain fraction of lyman alpha emitters it will take it into account. Then the dust extinction will be added and the IGM as well. SEDobs will also tell you how many templates there is after all extinction are applied. Next, it will apply the cosmology to the library. The templaes will be redshifted and if you decided to use the cosmology it will keep only the templates that are younger than the age of the universe at the redshift of the simulated galaxy.   

The template used for the simulated galaxy will then be chosen randomly in the left over templates. It will be normalize to the normalisation magnitude value in the normalisation band you selected and taking into account if you want to use sky emission. After that, it will create the noise based on the noise region that is given in the configuration and on the SNR . (see :doc:`configuration` page).

Finally, everything is saved in different catalog and individual files (see :doc:`output` for all the files that are created).


.. note::

    This exact run can be started in the test of SEDobs. if you hit the command **sedobs --test** and select the photometric simulation sedobs will run exactly this configuration.
