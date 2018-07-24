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

import configparser
import os
import sys


import messages as MTU
import filters

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
        General['N_obj']=config.getint('General', 'Nobj')
        General['filter_file'] = config.get('General', 'filter_file')
        self.General = General

        #####Data type
        DataT = {}
        DataT['Photometry'] = config.get('Data_Type', 'Photometry')
        DataT['Spectro'] = config.get('Data_Type', 'Spectro')
        self.DataT = DataT

        ###Spectro information
        SPEC = {}
        SPEC['NSpec'] = config.get('Spectro', 'NSpec')
        SPEC['Norm_band'] = config.get('Spectro', 'Norm_band')
        SPEC['Noise_reg'] = config.get('Spectro', 'Noise_reg')
        SPEC['Norm_distribution'] = config.get('Spectro', 'Norm_distribution')
        SPEC['types'] = config.get('Spectro', 'types')
        self.SPEC = SPEC

        ###Photo information
        PHOT = {}
        PHOT['Norm_band'] = config.get('Photo', 'Norm_band')
        PHOT['Norm_distribution'] = config.get('Photo', 'Norm_distribution')
        PHOT['Nband'] = config.get('Photo', 'Nband')
        PHOT['Band_list'] = config.get('Photo', 'Band_list')
        self.PHOT = PHOT

        ###Cosmology
        COSMO = {}
        COSMO['Ho'] = config.getfloat('Cosmo', 'Ho')
        COSMO['Omega_L'] = config.getfloat('Cosmo', 'Omega_L')
        COSMO['Omega_m'] = config.getfloat('Cosmo', 'Omega_m')
        COSMO['UseCo'] = config.get('Cosmo', 'Use_Cosmo')
        self.COSMO = COSMO

        Template = {}
        Template['BaseSSP'] = config.get('Templates', 'BaseSSP')
        Template['DustUse'] = config.get('Templates', 'DustUse')
        Template['EBVList'] = config.get('Templates', 'EBVList')
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

    def __init__(self, config):
        """
        Class Constructor
        """
        self.config = config

        ### 1- We check the general section
        MTU.Info('-1-###Check general section###---','No')
        gen_array = self.check_general(self.config.General)
        self.config.General['gen_array'] = gen_array 

        ### 2- Then the data types to simulate
        MTU.Info('-2-###Check data type section###---','Yes')
        dtype = self.check_dataT(self.config.DataT)
        self.config.DataT = dtype

        ### 3 - Check the cosmological module
        MTU.Info('-3-###Check Cosmo section###---','Yes')
        self.check_COSMO(self.config.COSMO)
        
        ## 4- simulated observation configuration
        MTU.Info('-4-###Check fake observation configuration section###---','Yes')
        if dtype == 'Photo' or dtype == 'Combined':
            MTU.Info('------###Check Photometric configuration###---','No')
            bands = self.check_PHOT(self.config.PHOT, gen_array, self.config.General['filter_file'])
            if not os.path.isdir(self.config.General['PDir']+'/photo_indiv'):
                 os.makedirs(self.config.General['PDir']+'/photo_indiv')
            else:
                MTU.Info('Photometric directory was already created', 'No') 

        if dtype == 'Spectro' or dtype == 'Combined':
            MTU.Info('------###Check Spectroscoptic configuration###---','No')
            spectra, specnorm, specs_noise = self.check_SPECTRO(self.config.SPEC, \
                    gen_array, self.config.General['filter_file'])

            self.config.SPEC['types'] = spectra
            self.config.SPEC['Norm_band'] = specnorm
            self.config.SPEC['Noise_reg'] = specs_noise
            if not os.path.isdir(self.config.General['PDir']+'/spectra'):
                 os.makedirs(self.config.General['PDir']+'/spectra')
            else:
                MTU.Info('Spectra directory already created', 'No') 

        ### 5 - Check the template configuration
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
        if General['filter_file']:
            if os.path.isfile(General['filter_file']):
                MTU.Info('filter file found','No')
            else:
                ###if it does not exist we create it
                MTU.Info('filter file not found','No')
        else:
            MTU.Error('No filter file given...exit', 'Yes')
            sys.exit()


        ###if full array given (z, STN, mag) then we don't
        ###need the Stn or z distribution
        if General['full_array']:
            ##if something is given we check if the file exist 
            MTU.Info('You choosed to give a Full array (z, StN, mag)','Yes')
            if os.path.isfile(General['full_array']):
                MTU.Info('Full array (z, StN, mag) file found','No')
                genarray = 'yes'
            else: 
                MTU.Error('Full array (z, StN, mag) not found...exit\n', 'Yes')
                sys.exit()
        else: 
            MTU.Info('You choosed individual distribution (z, STN, mag)','Yes')
            ###first we check if a distribution of redshift was given
            if General['z_dist'] != '' :
                if os.path.isfile(General['z_dist']):
                    MTU.Info('redshift distribution: file found','No')
                else: 
                    MTU.Error('redshift distribution: file not found...exit\n', 'Yes')
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
            MTU.Info('Photometry only will be simulated\n', 'No')
            return 'Photo'

        if dataT['Photometry'].lower() == 'no' and dataT['Spectro'].lower()== 'yes':
            MTU.Info('Spectroscopy only will be simulated\n', 'No')
            return 'Spectro'

        if dataT['Photometry'].lower() == 'yes' and dataT['Spectro'].lower()== 'yes':
            MTU.Info('Spectroscopy and Photometry will be simulated\n', 'No')
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


    def check_PHOT(self, PHOT, gen_array, filter_file):
        '''
        Method that checks the Phot configuration
        Parameters
        ----------
        PHOT        dict, with PHOT configuration fromn config file
        gen_array   str, yes or no to use full array. If no, we use individual
                         distribution
        '''
        ##extract list of filter from the filter file
        list_filt = filters.Retrieve_Filter_inf(filter_file).filter_list()

        ##check if the normalisation filter is in the filter file
        if PHOT['Norm_band']:
            if PHOT['Norm_band'] in list_filt:
                MTU.Info('%s for normalisation found in filter file'%PHOT['Norm_band'],'No') 
            else:
                MTU.Error('%s not found in filter file ... exit'%PHOT['Norm_band'], 'Yes')
                sys.exit()

        ##then we check if the user gave a general array
        if gen_array == 'no':
            ##if not we have to check the magnitude distribution
            if PHOT['Norm_distribution'] != '':
                if os.path.isfile(PHOT['Norm_distribution']):
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
            MTU.Error('Nband different from the number in band list ... exit', 'Yes')
            sys.exit()

        bands_to_simulate = {}
        for i in bandlist:
            indiv_band= i.strip("()").split(',')
            if len(indiv_band) != 4:
                MTU.Error('band configuration must be of the form (name, offset,mean_err, sigma_err) ... exit', 'Yes')
                sys.exit()

            name = indiv_band[0]
            if name in list_filt:
                MTU.Info('%s found in filter file'%name,'No') 
            else:
                MTU.Error('%s not found in filter file ... exit'%name, 'Yes')
                print(list_filt)
                sys.exit()
            bands_to_simulate[name] = [float(indiv_band[1]),float(indiv_band[2]), float(indiv_band[3])]
            #print(bands_to_simulate[name])

        return bands_to_simulate

    def check_SPECTRO(self, SPEC, gen_array, filter_file):
        '''
        Method that checks the spectroscopic configuration
        '''
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
                if len(indiv_band) !=4:
                    MTU.Error('Normalisation band configuration must be of the form (name,offset,mean_err,sigma_err) ... exit', 'Yes')
                    sys.exit()

                name = indiv_band[0]
                if name in list_filt:
                    MTU.Info('%s found in filter file'%name,'No') 
                else:
                    MTU.Error('%s not found in filter file ... exit'%name, 'Yes')
                    sys.exit()
                bands_to_simulate[name] = [float(indiv_band[1]),\
                        float(indiv_band[2]), float(indiv_band[3])]

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
                if os.path.isfile(SPEC['Norm_distribution']):
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
            if len(indiv_spec) != 5:
                MTU.Error('Spectral type must be of the form (li,lf,dl,res,StNfile) ... exit', 'Yes')
                sys.exit()

            indiv_spec[0] = float(indiv_spec[0])
            indiv_spec[1] = float(indiv_spec[1])
            indiv_spec[2] = float(indiv_spec[2])
            indiv_spec[3] = float(indiv_spec[3])

            if indiv_spec[0] < 0:
                MTU.Error('l0 must be strictly positive ... exit', 'Yes')
                sys.exit()
            
            if indiv_spec[0] >= indiv_spec[1]:
                MTU.Error('l0 must be < lf ... exit', 'Yes')
                sys.exit()
            
            if indiv_spec[2] < 0:
                MTU.Error('resolution element must be > 0 ... exit', 'Yes')
                sys.exit()
           
            if indiv_spec[3] < 0:
                MTU.Error('Rsolving power must be > 0 ... exit', 'Yes')
                sys.exit()

            if gen_array != 'yes' and not os.path.isfile(indiv_spec[4]):
                MTU.Error('StN file for spectra #%s not found... exit'%n, 'Yes')
                sys.exit()
            else:
                MTU.Info('StN file for spectra #%s found'%n, 'No')

            spectra_to_simulate['spec_%s'%n] = {}
            spectra_to_simulate['spec_%s'%n]['l0'] = indiv_spec[0]
            spectra_to_simulate['spec_%s'%n]['lf'] = indiv_spec[1]
            spectra_to_simulate['spec_%s'%n]['dl'] = indiv_spec[2]
            spectra_to_simulate['spec_%s'%n]['res'] = indiv_spec[3]
            spectra_to_simulate['spec_%s'%n]['Stnfile'] = indiv_spec[4]
            n += 1

        return spectra_to_simulate, bands_to_simulate, specs_noise

    def check_Template(self, Temp):
        '''
        Method that checks the template configuration
        '''
        ###check basessp
        if Temp['BaseSSP']:
            if os.path.isfile(Temp['BaseSSP']):
                MTU.Info('BaseSSP found', 'Yes')
            else:
                MTU.Error('BaseSSP not found ... exit', 'Yes')
                sys.exit()
        else:
            MTU.Error('No BaseSSP given ... exit', 'Yes')
            sys.exit()

        ###Dust Use
        if Temp['DustUse']:
            if os.path.isfile(Temp['DustUse']):
                MTU.Info('Dust file found (DustUse)', 'Yes')
            else:
                MTU.Error('Dust file not found (DustUse) ... exit', 'Yes')
                sys.exit()
 
            MTU.Info('Dust extinction used: %s'%Temp['DustUse'], 'No')

            if Temp['EBVList']:
                MTU.Info('%s E(B-V); list: %s'%(len(Temp['EBVList'].split(';')), Temp['EBVList'].split(';')), 'No')
                Temp['EBVList'] = Temp['EBVList'].split(';')
            else:
                MTU.Error('no E(B-V) list given ... exit', 'No')
                sys.exit()
        else:
            MTU.Info('No DUST extinction will be used', 'No')


        ##IGM Use
        if Temp['IGMtype']:
            MTU.Info('IGM file: %s'%Temp['IGMUse'], 'No')
            if os.path.isfile(Temp['IGMUse']):
                MTU.Info('IGM file found', 'No')
            else:
                MTU.Error('IGM file not found', 'Yes')
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

