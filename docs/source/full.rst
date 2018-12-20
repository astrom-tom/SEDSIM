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


Full Simulation
---------------

.. note::

    This exact run can be started in the test of SEDobs. if you hit the command **sedobs -- --test** and select the multispectro simulation sedobs will run exactly this configuration.


Configuration
^^^^^^^^^^^^^

We describe here the process the SEDobs uses when doing a photo-spectroscopic simulation with Ns=2 spectra per galaxy and Np=10 photometric bands. This will work of course with higher N.
The configuration we use is the one given below (named: SEDobs_Test_run_full.conf):

.. code-block:: shell

	[General]
	Project_name= SEDobs_Test_run_full
	Author= R. THOMAS - 14/10/18
	Project_Directory= ~/.sedobs/test_run_full
	full_array =  
	z_distribution = dist_zspec_multi.txt
	Nobj = 1500 
	[Data_Type]
	Photometry = Yes
	Spectro = Yes
	[Spectro]
	NSpec = 2 
	Norm_band = (r-megacam, 0.0, 0.1, 0.03)
	Noise_reg =  (1080,1170);(3600,3700)
	Norm_distribution = dist_mag.txt 
	types = (3500,9500,7.25,240,dist_SNR1.txt);(12000,15000,50,100,dist_SNR2.txt)
	[Photo]
	Norm_band = r-megacam
	Norm_distribution = dist_mag.txt
	Nband = 10
	Band_list = (u-megacam,0.0, 0.31, 0.38);(g-megacam,0.0,0.15,0.20);(r-megacam,0.0,0.19,0.09);(i-megacam, 0.0, 0.23, 0.12);(z-megacam,0.0, 0.38, 0.19);(J-wircam, 0.0, 0.68, 0.45);(H-wircam, 0.0, 0.71,0.37);(K-wircam,0.0,0.55, 0.41);(IRAC1,0.0,0.08, 0.04);(IRAC2,0.0,0.09,0.06)
	[Cosmo]
	Ho=70
	Omega_m=0.27
	Omega_L=0.73
	Use_Cosmo=Yes
	[Templates]
	BaseSSP=LIB_BC03_Delayed_LR_Salp_SPARTAN.hdf5
	DustUse=calzetti.dat
	EBVList=0.0;0.1;0.2;0.30;0.4;0.50
	IGMUse = SPARTAN_Meiksin_Free_7curves.hdf5
	###IGM type free or mean or empty
	IGMtype = free 
	EMline= yes
	Lyafrac = 0.5
	Age = 0.1e+09;0.2e+09;0.3e+09;0.4e+09;0.5e+09;0.6e+09;0.7e+09;0.8e+09;0.9e+09;1.0e+09;1.0e+09;1.1e+09;1.2e+09;1.3e+09;1.4e+09;1.5e+09
	TAU = 0.10;0.2;0.3;0.4;0.5;0.6;0.7;0.8;0.9;1.0
	MET = 0.4;1.0;2.5

We choose to use individual files (and not the full_array option). 

Checking configuration
^^^^^^^^^^^^^^^^^^^^^^

We start sedobs with this file (*sedobs --SEDobs_Test_run_full*) sedobs start by checking your configuration. You can see the output of the terminal for the full checking of your configuration:

.. figure:: ./pics/fullcheck.png
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
* **4-Check the spectroscopic-photometric configuration**: SEDobs then start to check the spectroscopic configuration. It checks the number of spectra that will be simulated per galaxy, also the normalisation band (and magnitude distribution).  It will check that a SNR distribution is given per simulated spectrum (2 simulated spectra --> 2 distributions of SNR). Finally it will check that the types of spectra are given as well as the noise regions and it will look at all the bands that will be simulated.
* **5-Check template configuration**: Then SEDobs look at your template setting. It checks that all the input files are found (IGM, dust extinction, templates).

Preparation
^^^^^^^^^^^

After this checks, SEDobs is going to prepare the extra files:
    * The final redshift, normalisation magnitude and SNR distributions. From the four files given (see above), four new distributions will be created, matching the shape of the original ones with the number of object you want to create. Examples are given below for this run:

.. figure:: ./pics/fulldist.png
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

.. figure:: ./pics/fullobjectsingle.png
    :width: 950px
    :align: center
    :alt: GUI

SEDobs start to take the library of templates that was created and adds emission lines. If you asked to give a certain fraction of lyman alpha emitters it will take it into account. Then the dust extinction will be added and the IGM as well. SEDobs will also tell you how many templates there is after all extinction are applied. Next, it will apply the cosmology to the library. The templaes will be redshifted and if you decided to use the cosmology it will keep only the templates that are younger than the age of the universe at the redshift of the simulated galaxy.   

The template used for the simulated galaxy will then be chosen randomly in the left over templates. It will be normalize to the normalisation magnitude value in the normalisation band you choosed and apply sky emission (if used) to the template. After that, all the band in your configuration are computed. In each band, the error is computed from the mean and sigma of the gaussian given for each band. Then it will cut the right regions depending on all your spectral configuration and create the noise based on the noise regions that are given in the configuration and the sky emission (if used). This noise will be created so the SNR matches (see :doc:`configuration` page).

Finally, everything is saved (see :doc:`output`) for all the files that are created.


.. note::

    This exact run can be started in the test of SEDobs. if you hit the command **sedobs --test** and select the photometric simulation sedobs will run exactly this configuration.
