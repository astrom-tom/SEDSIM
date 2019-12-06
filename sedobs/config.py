'''

The SEDSIM Project 
-------------------
File: config.py

This file read the configuration and prepares everything
for the simulations

@author: R. THOMAS
@year: 2018
@place:  ESO
@License: GPL v3.0 - see LICENCE.txt
'''

###Python standard library
import os
import sys
from pathlib import Path
from shutil import copyfile
import configparser

###third party
import numpy
import scipy.interpolate as interpolate

###local import
from . import messages as MTU
from . import filters

class read_config:
    """
    This class extract information from config file

    Attributes:
    ----------
        self.General    Python Dictionnary containing the general
                        configuration informations
        self.DataT      Python Dictionnary containing the Data types
                        to simulate
        self.SPEC       Python Dictionnary containing the Spectroscpic
                        configuration informations
        self.PHOT       Python Dictionnary containing the photometric
                        configuration informations
        self.COSMO      Python Dictionnary containing the cosmological model
                        configuration informations
        self.Template   Python Dictionnary containing the template type to use
                        configuration informations
    """

    def __init__(self, config_file):
        """
        Class Constructor
        """


        config = configparser.ConfigParser()
        config.read(config_file)

        #####General informations
        General = {}
        General['PName'] = config.get('General', 'Project_name')
        General['AName'] = config.get('General', 'Author')
        General['PDir'] = config.get('General', 'Project_Directory')
        General['full_array']=config.get('General','full_array')
        General['z_dist']=config.get('General', 'z_distribution')
        General['N_obj']=config.get('General', 'Nobj')
        if General['N_obj'] != '':
            General['N_obj'] = int(General['N_obj'])
        General['sizegal'] = config.getfloat('General', 'sizegal')
        self.General = General

        #####Data type
        DataT = {}
        DataT['Photometry'] = config.get('Data_Type', 'Photometry')
        DataT['Spectro'] = config.get('Data_Type', 'Spectro')
        self.DataT = DataT

        if DataT['Spectro'].lower() == 'yes':
            ###Spectro information
            SPEC = {}
            SPEC['NSpec'] = config.get('Spectro', 'NSpec')
            SPEC['Norm_band'] = config.get('Spectro', 'Norm_band')
            SPEC['Noise_reg'] = config.get('Spectro', 'Noise_reg')
            SPEC['Norm_distribution'] = config.get('Spectro', 'Norm_distribution')
            SPEC['types'] = config.get('Spectro', 'types')
            SPEC['flux_unit'] = config.get('Spectro', 'flux_unit')
            SPEC['wave_unit'] = config.get('Spectro', 'wave_unit')
            self.SPEC = SPEC

        ###Photo information
        PHOT = {}
        self.PHOT = PHOT
        if DataT['Photometry'].lower() == 'yes':
            PHOT['Norm_band'] = config.get('Photo', 'Norm_band')
            PHOT['Norm_distribution'] = config.get('Photo', 'Norm_distribution')
            PHOT['Nband'] = config.get('Photo', 'Nband')
            PHOT['Band_list'] = config.get('Photo', 'Band_list')
            PHOT['flux_unit'] = config.get('Photo', 'flux_unit')
            PHOT['wave_unit'] = config.get('Photo', 'wave_unit')
            PHOT['savesky'] = config.get('Photo', 'savesky').lower()

        ###Cosmology
        COSMO = {}
        COSMO['Ho'] = config.getfloat('Cosmo', 'Ho')
        COSMO['Omega_L'] = config.getfloat('Cosmo', 'Omega_L')
        COSMO['Omega_m'] = config.getfloat('Cosmo', 'Omega_m')
        COSMO['UseCo'] = config.get('Cosmo', 'Use_Cosmo')
        self.COSMO = COSMO

        Template = {}
        Template['BaseSSP'] = config.get('Templates', 'BaseSSP')
        Template['DustModel'] = config.get('Templates', 'DustModel')
        Template['Rv_sList'] = config.get('Templates', 'RvsList')
        Template['Av_sList'] = config.get('Templates', 'AvsList')
        #Template['DustUse_neb'] = config.get('Templates', 'DustUse_neb')
        #Template['Rv_nList'] = config.get('Templates', 'RvnList')
        #Template['Av_nList'] = config.get('Templates', 'AvnList')
        #Template['forcehigher_neb'] = config.get('Templates', 'force_ebvneb_higher')
        Template['IGMtype'] = config.get('Templates', 'IGMType').lower()
        Template['IGMUse'] = config.get('Templates', 'IGMUse')
        Template['EMline'] = config.get('Templates', 'EMline').lower()
        Template['Lyafrac'] = config.getfloat('Templates', 'Lyafrac')
        Template['Age'] = config.get('Templates', 'Age')
        Template['TAU'] = config.get('Templates', 'TAU')
        Template['MET'] = config.get('Templates', 'MET')
        self.Template = Template


class check_prepare:
    """
    This class check and prepare the program
    """

    def __init__(self, config, testarg, testtype):
        """
        Class Constructor
        """
        self.config = config
        self.testarg = testarg
        self.testtype = testtype
        self.home = str(Path.home())
        fileconf = os.path.join(self.home, '.sedobs/','sedobs_conf')
        self.inputdir = numpy.genfromtxt(fileconf, dtype='str')[1]
        self.hide_dir = os.path.join(self.home,'.sedobs/')

        ### 1- We check the general section
        MTU.Info('\033[91m'+'-1-###Check general section###---'+'\033[0m','No')
        gen_array = self.check_general(self.config.General)
        self.config.General['gen_array'] = gen_array 

        ### 2- Then the data types to simulate
        MTU.Info('\033[91m'+'-2-###Check data type section###---'+'\033[0m','Yes')
        dtype = self.check_dataT(self.config.DataT)
        self.config.DataT = dtype

        ### 3 - Check the cosmological module
        MTU.Info('\033[91m'+'-3-###Check Cosmo section###---'+'\033[0m','Yes')
        self.check_COSMO(self.config.COSMO)
        
        ## 4- simulated observation configuration
        MTU.Info('\033[91m'+'-4-###Check fake observation configuration section###---'+'\033[0m','Yes')
        if dtype == 'Photo' or dtype == 'Combined':
            MTU.Info('\033[94m'+'------###Check Photometric configuration###---'+'\033[0m','Yes')
            bands = self.check_PHOT(self.config, gen_array, os.path.join(self.inputdir, \
                    'SPARTAN_filters.hdf5'))
            self.config.PHOT['Band_list'] = bands
            if not os.path.isdir(self.config.General['PDir']+'/photo_indiv'):
                 os.makedirs(self.config.General['PDir']+'/photo_indiv')
            else:
                MTU.Info('Photometric directory was already created', 'No') 

        if dtype == 'Spectro' or dtype == 'Combined':
            MTU.Info('\033[94m'+'------###Check Spectroscoptic configuration###---'+'\033[0m','Yes')
            spectra, specnorm, specs_noise = self.check_SPECTRO(self.config, \
                    gen_array, os.path.join(self.inputdir, 'SPARTAN_filters.hdf5'))

            self.config.SPEC['types'] = spectra
            self.config.SPEC['Norm_band'] = specnorm
            self.config.SPEC['Noise_reg'] = specs_noise
            if not os.path.isdir(self.config.General['PDir']+'/spectra'):
                 os.makedirs(self.config.General['PDir']+'/spectra')
            else:
                MTU.Info('Spectra directory already created', 'No') 

        ### 5 - Check the template configuration
        MTU.Info('-5-###Check Template section###---','Yes')
        self.config.Template = self.check_Template(self.config.Template)


    def check_general(self, General):
        '''
        Method that checks the general configuration section
        Parameter
        ---------
        General     dict, of configuration of the general section
        '''
        ###check project name
        if General['PName']:
            MTU.Info('Project Name: %s' % General['PName'],'No')
        else:
            MTU.Error('No project name given...exit', 'Yes')
            sys.exit()


        ###check Project Directory
        if General['PDir']:
            if General['PDir'][0] == '~':
                General['PDir'] = os.path.join(self.home, General['PDir'][2:])

            MTU.Info('Project Directory: %s' % General['PDir'],'No')
            if os.path.isdir(General['PDir']):
                MTU.Info('----> Project Directory already exists','No')
            else:
                ###if it does not exist we create it
                MTU.Info('----> Project Directory does not exist and will be created','No')
                ##here!
                os.makedirs(General['PDir'])
                MTU.Info('----> DONE','No')
        else:
            MTU.Error('No Project directory given...exit', 'Yes')
            sys.exit()

        ###check filter file
        if os.path.isfile(os.path.join(self.inputdir, 'SPARTAN_filters.hdf5')):
            MTU.Info('Filter file found','No')
        else:
            ###if it does not exist we create it
            MTU.Info('Filter file not found','No')
            sys.exit()

        ###if test we dispatch the files in the directory
        if self.testarg:
            self.test_move_files(General['PDir'])

        ###if full array given (z, STN, mag) then we don't
        ###need the Stn or z distribution
        if General['full_array']:
            ##if something is given we check if the file exist 
            MTU.Info('You choosed to give a Full array (z, StNs, mags)','Yes')
            if os.path.isfile(os.path.join(General['PDir'], General['full_array'])):
                MTU.Info('Full array (z, StN, mag) file found','No')
                genarray = 'yes'
            else: 
                MTU.Error('Full array (z, StN, mag) not found...exit\n', 'Yes')
                sys.exit()
        else: 
            MTU.Info('You choosed individual distribution (z, STNs, mags)','Yes')
            ###first we check if a distribution of redshift was given
            if General['z_dist'] != '' :
                if os.path.isfile(os.path.join(General['PDir'], General['z_dist'])):
                    MTU.Info('redshift distribution: file found','No')
                else: 
                    MTU.Error('redshift distribution: file not found...exit\n', 'Yes')
                    MTU.Error('--> %s'% os.path.join(General['PDir'], General['z_dist']), 'Yes')
                    sys.exit()
            else:
                MTU.Error('No redshift distribution given...exit\n', 'Yes')
                sys.exit()
 

            ###finall we check if a number of simulation has been provided
            if General['N_obj'] != '':
                MTU.Info('%s simulated objects will be created' % General['N_obj'],'No')
            else:
                MTU.Error('No number of simulation you want to create passed...exit\n', 'Yes')
                sys.exit()
            
            genarray = 'no'

        return  genarray

    def test_move_files(self, directory):
        '''
        This function moves the test files into the hidden directory (in the home)
        
        Parameter
        ---------
        directory
                    str, path to the test project directory

        Returns
        -------
        None
        '''

        if self.testtype == 'p':
            listfile = ['dist_mag.txt', 'dist_z.txt']
            for i in listfile:
                copyfile(os.path.join(self.hide_dir, i), os.path.join(directory, i)) 

        if self.testtype == 'pg':
            listfile = ['SEDobs_Test_run_photo_full_array.txt']
            for i in listfile:
                copyfile(os.path.join(self.hide_dir, i), os.path.join(directory, i)) 

        if self.testtype == 's':
            listfile = ['dist_mag.txt', 'dist_z.txt', 'all_snr_lowz.txt']
            for i in listfile:
                copyfile(os.path.join(self.hide_dir, i), os.path.join(directory, i)) 

        if self.testtype == 'sg':
            listfile = ['SEDobs_Test_run_spectro_full_array.txt']
            for i in listfile:
                copyfile(os.path.join(self.hide_dir, i), os.path.join(directory, i)) 

        if self.testtype in ['m', 'f']:
            listfile = ['dist_mag.txt', 'dist_zspec_multi.txt', 'dist_SNR1.txt', 'dist_SNR2.txt']
            for i in listfile:
                copyfile(os.path.join(self.hide_dir, i), os.path.join(directory, i)) 

        if self.testtype == 'mg':
            listfile = ['SEDobs_Test_run_multispectro_full_array.txt']
            for i in listfile:
                copyfile(os.path.join(self.hide_dir, i), os.path.join(directory, i)) 

        if self.testtype == 'fg':
            listfile = ['SEDobs_Test_run_full_full_array.txt']
            for i in listfile:
                copyfile(os.path.join(self.hide_dir, i), os.path.join(directory, i)) 

    def check_dataT(self, dataT):
        '''
        Method that checks the data types that will be used
        Parameter:
        ----------
        dataT   dict, wioth types of data from config file

        Return:
        -------
        type    str, type of data to simulate
        '''

        if dataT['Photometry'].lower() == 'no' and dataT['Spectro'].lower()== 'no':
            MTU.Error('No data type chosen ... exit', 'No')
            sys.exit()

        if dataT['Photometry'].lower() == 'yes' and dataT['Spectro'].lower()== 'no':
            MTU.Info('Photometry only will be simulated', 'No')
            return 'Photo'

        if dataT['Photometry'].lower() == 'no' and dataT['Spectro'].lower()== 'yes':
            MTU.Info('Spectroscopy only will be simulated', 'No')
            return 'Spectro'

        if dataT['Photometry'].lower() == 'yes' and dataT['Spectro'].lower()== 'yes':
            MTU.Info('Spectroscopy and Photometry will be simulated', 'No')
            return 'Combined'


    def check_COSMO(self, COSMO):
        '''
        Method that checks the cosmological models 
        Parameter:
        ---------
        COSMO   dict, Cosmology configuration from config file 
        '''

        if COSMO['UseCo'].lower() == 'yes':
            if COSMO['Omega_m']+COSMO['Omega_L']!=1:
                MTU.Error('Omega_m + Omega_L must be =1 ... exit', 'Yes')
                sys.exit()
            else:
                MTU.Info('Cosmological configuration: OK', 'No')


    def check_PHOT(self, config, gen_array, filter_file):
        '''
        Method that checks the Phot configuration
        Parameters
        ----------
        PHOT        dict, with PHOT configuration fromn config file
        gen_array   str, yes or no to use full array. If no, we use individual
                         distribution
        filter_file str, path/and/file to the filter file

        Return
        -------
        bands_to_simulate dict, with the configuration of all the bands 
        '''

        ##extract from configuration
        PHOT = config.PHOT
        General = config.General

        ##extract list of filter from the filter file
        list_filt = filters.Retrieve_Filter_inf(filter_file).filter_list()

        ##check if the normalisation filter is in the filter file
        if PHOT['Norm_band']:
            if PHOT['Norm_band'].strip("()").split(',')[0]  in list_filt:
                MTU.Info('%s for normalisation found in filter file'%PHOT['Norm_band'].strip("()").split(',')[0],'No') 
            else:
                MTU.Error('%s for normalisation not found in filter file ... exit'%PHOT['Norm_band'], 'Yes')
                sys.exit()

        ##then we check if the user gave a general array
        if gen_array == 'no':
            ##if not we have to check the magnitude distribution
            if PHOT['Norm_distribution'] != '':
                if os.path.isfile(os.path.join(General['PDir'], PHOT['Norm_distribution'])):
                    MTU.Info('Normalisation magnitude file found ','No') 
                else:
                    MTU.Error('Normalisation magnitude file not found... exit', 'Yes')
                    sys.exit()
            else:
                MTU.Error('No Normalisation magnitude given... exit', 'Yes')
                sys.exit()
 
        ###then we check the number of band
        if PHOT['Nband'] != '':
            MTU.Info('N=%s bands will be computed in each simulated object'%(PHOT['Nband']),'No')
        else:
            MTU.Error('Number of bands not given ... exit', 'Yes')
            sys.exit()

        ###and then check the list of band
        bandlist = PHOT['Band_list'].split(';')
        if len(bandlist) != int(PHOT['Nband']):
            MTU.Error('Nband different from the number in given in band list ... exit', 'Yes')
            sys.exit()

        bands_to_simulate = {}
        for i in bandlist:
            indiv_band= i.strip("()").split(',')
            ###each band configuration has 6 values:
            ###name, offset, mean error, sigme arror, atmosphere,skysub
            ###the two last are predefined,
            if len(indiv_band) != 6:   
                MTU.Error('band configuration must be of the form '+ \
                        '(name,offset,mean_err,sigma_err,Atmosphere,skysub) ... exit', 'Yes')
                sys.exit()

            name = indiv_band[0]
            if name in list_filt:
                MTU.Info('%s found in filter file'%name,'No') 
            else:
                MTU.Error('%s not found in filter file ... exit'%name, 'Yes')
                print('The list of available filter is:',list_filt)
                sys.exit()
            if indiv_band[-2] not in ['none', 'low', 'int', 'high']:
                MTU.Error('Wrong Atmospheric parameter. Must be none or low or int or high ... exit', \
                        'Yes')
                sys.exit()
            else:
                bands_to_simulate[name] = [indiv_band[0], float(indiv_band[1]), \
                    float(indiv_band[2]), float(indiv_band[3]), indiv_band[-2], \
                    float(indiv_band[-1])/100]

        ###put the normalisation band in right format
        splitband = PHOT['Norm_band'].strip("()").split(',')
        if len(splitband) != 3:
            MTU.Error('Normalisation band for configuration must be of the form '+ \
                        '(name,atm,skysub) ... exit', 'Yes')
            sys.exit()
        else:
            #if splitband[-2] not in ['none', 'low', 'int', 'high']:
            #    MTU.Error('Wrong Atmospheric parameter. Must be none or low or int or high ... exit', \
            #            'Yes')
            #    sys.exit()
            #else:
            PHOT['Norm_band'] = [splitband[0], splitband[1], float(splitband[2])/100]

        if PHOT['flux_unit'] == 'Jy':
            MTU.Info('Flux unit will be Jansky', 'No')

        if PHOT['flux_unit'] == 'muJy':
            MTU.Info('Flux unit will be micro Jansky', 'No')

        if PHOT['flux_unit'] == '':
            MTU.Info('Flux unit will be erg/s/cm2/A', 'No')

        if PHOT['wave_unit'] == '':
            MTU.Info('Wavelength will be in Angtrom', 'No')
        
        if PHOT['wave_unit'] == 'log_ang':
            MTU.Info('Wavelength will be log(Angstrom)', 'No')
        
        if PHOT['savesky'] not in ['yes', 'no']:
            MTU.Error('Save sky data?...exit\n', 'Yes')
            sys.exit()

        return bands_to_simulate

    def check_SPECTRO(self, config, gen_array, filter_file):
        '''
        Method that checks the spectroscopic configuration
        '''

        ##extract from configuration
        SPEC = config.SPEC
        General = config.General

        ### SPEC
        if SPEC['NSpec']:
            MTU.Info('Number of spectra: %s'%SPEC['NSpec'], 'No')
        else:
            MTU.Error('No number of spectra given (NSpec) ... exit', 'Yes')
            sys.exit()

        ##extract list of filter from the filter file
        list_filt = filters.Retrieve_Filter_inf(filter_file).filter_list()

        ##check if the normalisation filter is in the filter file
        if SPEC['Norm_band']:

            if int(SPEC['NSpec']) > 1:
                specs_norm = SPEC['Norm_band'].split(';')
            else:
                specs_norm = [SPEC['Norm_band']]

            bands_to_simulate = {}
            for i in specs_norm:
                indiv_band= i.strip("()").split(',')
                if len(indiv_band) !=3:
                    MTU.Error('Normalisation band configuration must be of the form'+ \
                            '(name,atm,skysub) ... exit', 'Yes')
                    sys.exit()

                name = indiv_band[0]
                if name in list_filt:
                    MTU.Info('%s found in filter file'%name,'No') 
                else:
                    MTU.Error('%s not found in filter file ... exit'%name, 'Yes')
                    sys.exit()
                bands_to_simulate[name] = [indiv_band[0], indiv_band[1], float(indiv_band[2])/100]

            for i in bands_to_simulate:
                if i in list_filt:
                    MTU.Info('%s for normalisation found in filter file'%i,'No') 
                else:
                    MTU.Error('%s not found in filter file ... exit'%i, 'Yes')
                    sys.exit()

        if SPEC['Noise_reg']:

            if int(SPEC['NSpec']) > 1:
                specs_noise = SPEC['Noise_reg'].split(';')
                if len(specs_noise) != int(SPEC['NSpec']):
                    MTU.Error('Number of spectra different from number of noise region ... exit', 'Yes')
                    sys.exit()
                else:
                    MTU.Info('Found %s spectrum noise regions'%len(specs_noise),'No')
            else:
                specs_noise = [SPEC['Noise_reg']]

        ##then we check if the user gave a general array
        if gen_array == 'no':
            ##if not we have to check the magnitude distribution
            if SPEC['Norm_distribution'] != '':
                if os.path.isfile(os.path.join(General['PDir'], SPEC['Norm_distribution'])):
                    MTU.Info('Normalisation magnitude file found ','No') 
                else:
                    MTU.Error('Normalisation magnitude file not found... exit', 'Yes')
                    sys.exit()

            else:
                MTU.Error('Magnitude Normalisation file not given ... exit', 'Yes')
                sys.exit()


        ##check spectra types
        spectralist = SPEC['types'].split(';')
        if len(spectralist) != int(SPEC['NSpec']):
            MTU.Error('Nspec different from the number in types ... exit', 'Yes')
            sys.exit()

        spectra_to_simulate = {}
        n=1
        for i in spectralist:
            indiv_spec= i.strip("()").split(',')

            if gen_array == 'no':
                if len(indiv_spec) != 7:
                    MTU.Error('Spectral type must be of the form '+ \
                            '(li,lf,dl,res,StNfile,Atmosphere,skysub) ... exit', 'Yes')
                    sys.exit()
            else:
                if len(indiv_spec) != 6:
                    MTU.Error('Spectral type must be of the form '+\
                            '(li,lf,dl,res,Atmosphere,skysub) ... exit'\
                            , 'Yes')
                    sys.exit()

            indiv_spec[0] = float(indiv_spec[0])
            indiv_spec[1] = float(indiv_spec[1])
            indiv_spec[2] = float(indiv_spec[2])
            indiv_spec[3] = float(indiv_spec[3])

            if indiv_spec[0] < 0:
                MTU.Error('l0 must be strictly positive ... exit', 'Yes')
                sys.exit()
            
            if indiv_spec[0] >= indiv_spec[1]:
                MTU.Error('lf must be > l0 ... exit', 'Yes')
                sys.exit()
            
            if indiv_spec[2] < 0:
                MTU.Error('resolution element must be > 0 ... exit', 'Yes')
                sys.exit()
           
            if indiv_spec[3] < 0:
                MTU.Error('Resolving power must be > 0 ... exit', 'Yes')
                sys.exit()

            if indiv_spec[-2] not in ['none', 'low', 'int', 'high']:
                MTU.Error('Wrong Atmospheric parameter. Must be none or low or int or high ... exit', \
                        'Yes')
                sys.exit()
 
            if gen_array == 'no':
                if os.path.isfile(os.path.join(General['PDir'], indiv_spec[4])):
                    MTU.Info('StN file for spectra #%s found'%n, 'No')
                else:
                    MTU.Error('StN file for spectra #%s not found... exit'%n, 'Yes')
                    sys.exit()

            spectra_to_simulate['spec_%s'%n] = {}
            spectra_to_simulate['spec_%s'%n]['l0'] = indiv_spec[0]
            spectra_to_simulate['spec_%s'%n]['lf'] = indiv_spec[1]
            spectra_to_simulate['spec_%s'%n]['dl'] = indiv_spec[2]
            spectra_to_simulate['spec_%s'%n]['res'] = indiv_spec[3]
            spectra_to_simulate['spec_%s'%n]['Atm'] = indiv_spec[-2]
            spectra_to_simulate['spec_%s'%n]['skysub'] = float(indiv_spec[-1])/100

            if gen_array == 'no':
                spectra_to_simulate['spec_%s'%n]['Stnfile'] = indiv_spec[4]
            n += 1

        if SPEC['flux_unit'] == 'Jy':
            MTU.Info('Flux unit will be Jansky', 'No')

        if SPEC['flux_unit'] == 'muJy':
            MTU.Info('Flux unit will be micro Jansky', 'No')

        if SPEC['flux_unit'] == '':
            MTU.Info('Flux unit will be erg/s/cm2/A', 'No')

        if SPEC['wave_unit'] == '':
            MTU.Info('Wavelength will be in Angtrom', 'No')
        
        if SPEC['wave_unit'] == 'log_ang':
            MTU.Info('Wavelength will be log(Angstrom)', 'No')

        return spectra_to_simulate, bands_to_simulate, specs_noise

    def check_Template(self, Temp):
        '''
        Method that checks the template configuration
        '''
        ###check basessp
        if Temp['BaseSSP']:
            fullpath = os.path.join(self.inputdir, 'LIBS', Temp['BaseSSP'])
            if os.path.isfile(fullpath):
                MTU.Info('BaseSSP found', 'No')
            else:
                MTU.Error('BaseSSP not found ... exit', 'Yes')
                sys.exit()
        else:
            MTU.Error('No BaseSSP given ... exit', 'Yes')
            sys.exit()

        ###stellar Dust Use
        if Temp['DustModel']:
            fullpathdust = os.path.join(self.inputdir, 'EXT', Temp['DustModel'])
            if os.path.isfile(fullpathdust):
                MTU.Info('Dust file found (DustModel)', 'No')
            else:
                MTU.Error('Dust file not found (DustModel) ... exit', 'Yes')
                sys.exit()
 
            MTU.Info('Dust extinction used: %s'%Temp['DustModel'], 'No')

            if Temp['Av_sList']:
                MTU.Info('%s Av stellar ; list: %s'%(len(Temp['Av_sList'].split(';')),\
                        Temp['Av_sList'].split(';')), 'No')
                Temp['Av_sList'] = Temp['Av_sList'].split(';')
                for i in Temp['Av_sList']:
                    if float(i)<0:
                        raise Exception('Rv for nebular extinction should be positive')
 
            else:
                MTU.Error('no stellar Av list given ... exit', 'No')
                sys.exit()

            if Temp['Rv_sList']:
                MTU.Info('%s Rv stellar ; list: %s'%(len(Temp['Rv_sList'].split(';')),\
                        Temp['Rv_sList'].split(';')), 'No')
                Temp['Rv_sList'] = Temp['Rv_sList'].split(';')
                for i in Temp['Rv_sList']:
                    if float(i)<0:
                        raise Exception('Rv for nebular extinction should be positive')
 
            else:
                MTU.Info('no stellar Rv list given ... '+\
                        'will use the default value for the selected law', 'No')
        else:
            MTU.Info('No DUST extinction will be used', 'No')

            '''
            ###Nebular Dust Use
            if Temp['DustUse_neb'].lower() == 'yes':

                ###nebular extinction (emission line)
                if Temp['Av_nList']:
                    MTU.Info('%s Av nebular; list: %s'%(len(Temp['Av_nList'].split(';')),\
                            Temp['Av_nList'].split(';')), 'No')
                    Temp['Av_nList'] = Temp['Av_nList'].split(';')
                    for i in Temp['Av_nList']:
                        if float(i)<0:
                            raise Exception('Av for nebular extinction should be positive')
     
                else:
                    MTU.Error('no nebular Av list given ... exit', 'No')
                    sys.exit()

                if Temp['Rv_nList']:
                    MTU.Info('%s Rv nebullar ; list: %s'%(len(Temp['Rv_nList'].split(';')),\
                            Temp['Rv_nList'].split(';')), 'No')
                    Temp['Rv_nList'] = Temp['Rv_nList'].split(';')
                    for i in Temp['Rv_nList']:
                        if float(i)<0:
                            raise Exception('Rv for nebular extinction should be positive')
                    
                else:
                    MTU.Error('no nebular Rv list given ... exit', 'No')
                    sys.exit()

            else:
                MTU.Info('Nebular extinction will be equal to stellar extinction', 'No')

        if Temp['forcehigher_neb'].lower() == 'yes':
            Temp['forcehigher_neb'] = True
        '''
        ##IGM Use
        if Temp['IGMtype']:
            fullpathigm = os.path.join(self.inputdir, 'IGM', Temp['IGMUse'])
            MTU.Info('IGM file: %s'%Temp['IGMUse'], 'No')
            if os.path.isfile(fullpathigm):
                MTU.Info('IGM file found', 'No')
            else:
                MTU.Error('IGM file not found', 'Yes')
                sys,exit()
            MTU.Info('IGM type: %s'%Temp['IGMtype'], 'No')
        else:
            MTU.Info('No IGM will be used ', 'No')


        ##Emission lines
        if Temp['EMline'].lower() == 'yes':
            MTU.Info('Emission line will be added', 'No')
        else:
            MTU.Info('Emission line will not be used', 'No')

        if Temp['Lyafrac']:
            if Temp['Lyafrac']>1.0:
                MTU.Error('fraction of Lya emitters higher than 1!', 'Yes')
            else:
                MTU.Info('Fraction of Lya emitters:%s'%Temp['Lyafrac'],'No')
        else:
            MTU.Info('Fraction of Lya emitters: 100$\%$','No')


        ##Ages
        if Temp['Age']:
            MTU.Info('%s Age; list: %s'%(len(Temp['Age'].split(';')),Temp['Age'].split(';')) , 'No')
            Temp['Age'] = Temp['Age'].split(';')
        else:
            MTU.Error('No Ages were given', 'No')

        ##TAU
        if Temp['TAU']:
            MTU.Info('%s TAU; list: %s'%(len(Temp['TAU'].split(';')),Temp['TAU'].split(';')), 'No')
            Temp['TAU'] = Temp['TAU'].split(';')
        else:
            MTU.Error('No TAU values were given', 'No')

        ##MET
        if Temp['MET']:
            MTU.Info('%s MET; list: %s'%(len(Temp['MET'].split(';')),Temp['MET'].split(';')), 'No')
            Temp['MET'] = Temp['MET'].split(';')
        else:
            MTU.Error('No MET values were given', 'No')

        return Temp

class prepare_dis:
    """
    This class check and prepare the program
    """

    def __init__(self, testarg, test):
        """
        Class Constructor
        """
        self.testarg = testarg
        self.test = test
        self.home = str(Path.home())
        fileconf = os.path.join(self.home, '.sedobs/','sedobs_conf')
        self.inputdir = numpy.genfromtxt(fileconf, dtype='str')[1]
        self.hide_dir = os.path.join(self.home,'.sedobs/')


    def full_array(self, conf):
        '''
        Method that computes extract StN, redshift and normalisation
        Magnitude from the full array given by the user
        Parameter
        ---------
        conf        dict, from the config file

        Returns:
        --------
        redshift    list, of redshift
        StN         list, of Signal to noise
        mag         list, of normalisation magnitude
        '''
        
        A = numpy.loadtxt(os.path.join(conf.General['PDir'], conf.General['full_array'])).T        
        
        redshift = A[0]
        mag = A[1]

        if conf.DataT == 'Combined' or conf.DataT == 'Spectro':
            STN = []
            for i in range(int(conf.SPEC['NSpec'])):
                STN.append(A[2+i])
        else:
            STN = numpy.zeros(len(mag))

        return redshift, STN, mag

    def indiv_dist(self, conf):
        '''
        Method that computes random individual distribution of
        StN, redshift and normalisation magnitude from the 3 independant
        distribution given by the user
        Parameter
        ---------
        conf        dict, from the config file

        Returns:
        --------
        redshift    list, of redshift
        StN         list, of Signal to noise
        mag         list, of normalisation magnitude
        '''
        File = os.path.join(conf.General['PDir'],'final_array_z_StN_mag.txt')
        ###if it already exists then we have been there already
        if os.path.isfile(File):
            MTU.Info('final_array_z_StN_mag.txt already exist, load it', 'No')
            conf.General['full_array'] = File

            A = numpy.loadtxt(conf.General['full_array']).T
            redshift = A[0]
            mag = A[1]
            if conf.DataT == 'Combined' or conf.DataT == 'Spectro':
                STN = []
                for i in range(int(conf.SPEC['NSpec'])):
                    STN.append(A[2+i])
            else:
                STN = numpy.zeros(len(mag))

            return redshift, STN, mag

        else:
            ###Number of simulations
            Nsim = conf.General['N_obj']

            ####we start by the redshift distribution
            zdistuser = numpy.genfromtxt(os.path.join(conf.General['PDir'], conf.General['z_dist']))
            if zdistuser.size == 1:
                new_zdist = zdistuser * numpy.ones(Nsim)
            else:
                new_zdist = self.dist_from_user_dist(zdistuser,Nsim,int(len(zdistuser)/10))
            #plot().two_dist(zdistuser,20,'user, N=%s'%len(zdistuser), new_zdist, 20,\
            #        'final dist, N=%s'%Nsim, 'Redshift z')
            ##then the magnitudes 
            if conf.DataT in ['Combined', 'Photo']:
                Norm_distuser = numpy.loadtxt(os.path.join(conf.General['PDir'], \
                        conf.PHOT['Norm_distribution']))
            else:
                Norm_distuser = numpy.loadtxt(os.path.join(conf.General['PDir'], \
                        conf.SPEC['Norm_distribution']))

            if Norm_distuser.size == 1:
                new_Normdist = Norm_distuser * numpy.ones(Nsim)
            else:
                new_Normdist = self.dist_from_user_dist(Norm_distuser,Nsim,int(len(Norm_distuser)/10))
            ##then the StN
            if conf.DataT == 'Combined' or conf.DataT == 'Spectro':
                specs = list(conf.SPEC['types'])
                Ndist = []
                for i in range(int(conf.SPEC['NSpec'])):
                    StN_distuser = numpy.loadtxt(os.path.join(conf.General['PDir'], \
                            conf.SPEC['types'][specs[i]]['Stnfile']))

                    if StN_distuser.size == 1:
                        new_StNdist = StN_distuser *  numpy.ones(Nsim)
                    else:
                        new_StNdist = self.dist_from_user_dist(StN_distuser,Nsim,int(len(StN_distuser)/10))
                    #plot().two_dist(StN_distuser,20,'user, N=%s'%len(StN_distuser), new_StNdist, 20,\
                    #'final dist, N=%s'%Nsim, 'Signa-to-noise ratio')  
                    Ndist.append(new_StNdist) 
            else:
                Ndist = [numpy.zeros(len(new_zdist))]

            ##and write it down
            File = self.write_down_full_array(new_zdist, Ndist, new_Normdist, conf)
            conf.General['full_array'] =  'final_array_z_StN_mag.txt'
            return self.full_array(conf)



    def write_down_full_array(self, z, Stn, Norm, conf):
        '''
        This method writes down the full array made from the individual
        distributions
        '''
        File = conf.General['PDir']+'/final_array_z_StN_mag.txt'
        if not os.path.isfile(File):
            MTU.Info('Write down final_array_z_StN_mag.txt', 'No')
            with open(File, 'w') as FF:
                ##first we create the header
                head = '#redshift\tMagNorm'
                for i in range(len(Stn)):
                     head += '\tStN_%s'%str(i+1)
                head += '\n' 
                FF.write(head)

                for i in enumerate(z):
                    line = '%.4f\t%.4f\t'%(z[i[0]],Norm[i[0]])
                    for j in range(len(Stn)):
                        line += '\t%.4f'%(Stn[j][i[0]])
                    line += '\n'
                    FF.write(line)
            
            return File 
        else:
            MTU.Info('Final_array_z_StN_mag.txt, already exist', 'No')
            return File



    def dist_from_user_dist(self, user_dist, Nsim, binning):
        '''
        Method that draw from the user distribution another distribution
        with the Nsim object that has the same shape
        Parameter
        ---------
        user_dist   list, of values from the user distribution
        Nsim        int, number of simulation given by the user
        binning     binning, of the distribution

        Returns:
        -------
        new_dist    list, of Nsim value with the same distribution as
                          user_dist
        '''

        hist, bin_edges = numpy.histogram(user_dist, bins=binning, density=True)
        cum_values = numpy.zeros(bin_edges.shape)
        cum_values[1:] = numpy.cumsum(hist*numpy.diff(bin_edges))
        inv_cdf = interpolate.interp1d(cum_values, bin_edges)
        r = numpy.random.rand(Nsim)
        new_dist = inv_cdf(r)
        return new_dist
