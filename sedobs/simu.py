'''
############################
#####
##### The Spartan SIM Project
#####      R. THOMAS
#####        2017
#####
#####   Main of the simulation
#####        core
###########################
@License: GNU Public licence V3
'''

##### Python standard
import os
from pathlib import Path
import random

#python third party
import numpy

##### local
from . import messages as MTU
from . import simu_output
from . import units
from . import modif_LIB
from . import Photometry
from . import Spectroscopy
from . import Check_plots

class Main:
    '''
    This is the main class of SPARTAN - SIM
    '''

    def __init__(self, conf):
        '''
        Initialization, we define the attributes of the class and
        the name of the output files and directories
        '''

        self.home = str(Path.home())
        fileconf = os.path.join(self.home, '.sedobs/','sedobs_conf')
        self.inputdir = numpy.genfromtxt(fileconf, dtype='str')[1]
 
        
        self.conf = conf
        self.full_array = conf.General['full_array']
        self.final_dir = conf.General['PDir']
        self.filter_file = os.path.join(self.inputdir, 'SPARTAN_filters.hdf5') 
        self.DataT = conf.DataT

        ##directories and summary files
        if self.DataT == 'Combined' or self.DataT == 'Photo':
            self.PhotoDir = conf.General['PDir'] + '/photo_indiv'
            self.Photofinalfile = os.path.join(conf.General['PDir'], \
                    conf.General['PName'] + '_photo_file_final.txt')

        if self.DataT == 'Combined' or self.DataT == 'Spectro':
            self.SpectraDir = conf.General['PDir'] + '/spectra'
            self.Spectrofinalfile = os.path.join(conf.General['PDir'], \
                    conf.General['PName']+'_spectro_file_final.txt')

        if self.DataT == 'Combined':
            self.Combinedfinalfile = os.path.join(conf.General['PDir'], \
                    conf.General['PName']+'_Combined_file_final.txt')

        self.final_param_file = conf.General['PDir'] + '/' +\
                '%s_final_param_file.txt'%conf.General['PName']

        self.original_template_dir = os.path.join(conf.General['PDir'], 'original_template')

    def main(self, z, StN, mag, wave_rf, template, parameters, param_names, COSMOS):

        '''
        This method is the main engin of the simulation
        '''

        #### 1 -output files
        MTU.Info('1 - Check output files', 'Yes')
        self.prepare_files()

        #### 2 - We start the simulations
        MTU.Info('2 - Start simulations!!', 'Yes')

        for i in enumerate(z):

            #######
            z = i[1]
            NormMag = mag[i[0]]
            N = int(i[0])+1

            ###message to display

            MTU.Info('Start simulation #%s'%N, 'Yes')
            MTU.Info('z=%s, Normmag=%s'%(z, NormMag), 'No')
            ### a - create simulation names and check presence of files
            if self.DataT == 'Photo' or self.DataT == 'Combined':
                Name_photo = '%s_Photometry_N%s.dat'%(self.conf.General['PName'], N)

            if self.DataT == 'Spectro' or self.DataT == 'Combined':
                Name_spectro = '%s_spectro_N%s.dat'%(self.conf.General['PName'], N)

            if self.DataT == 'Combined':
                Name_Combined = '%s_comb_N%s.dat'%(self.conf.General['PName'], N)

            ####update library with emline and 
            ##1 Emission line
            ####check for Lyman alpha
            frac = self.conf.Template['Lyafrac']
            frac = numpy.random.choice([True, False], size=1, p=[frac, 1-frac])[0]
            if not frac:
                toskip = ['H_Lya']
            else:
                toskip = []

            MTU.Info('Addition of Emission line', 'Yes')
            Templates_emLine = modif_LIB.Emlineslib().main(template, wave_rf, parameters, \
                    param_names, self.conf, toskip)

            ##2 Dust
            DUST_dict = modif_LIB.DUSTlib().Dust_for_fit(self.conf.Template['DustUse'], wave_rf,\
                self.conf.Template['EBVList'])
            Dusted_template, Dusted_Parameters, \
                Dust_param_names = modif_LIB.DUSTlib().Make_dusted_library(Templates_emLine, \
                DUST_dict, parameters, param_names, wave_rf)

            #### b - we had the IGM if needed
            ### We check if we will use some IGM and if Yes, we prepare it
            IGM_dict = modif_LIB.IGMlib().IGM_for_fit(self.conf.Template['IGMUse'],\
                    z, wave_rf, self.conf.Template['IGMtype'])
            Templates_IGM, Parameter_IGM, IGM_param_names, \
                    appliedIGM = modif_LIB.IGMlib().Make_IGM_library(wave_rf, Dusted_template, \
                                 Dusted_Parameters, Dust_param_names, z, IGM_dict)

            MTU.Info('After IGM, we have %s Template in the library'%len(Templates_IGM), 'No')

            #### c - we redshift the library
            MTU.Info('Apply cosmology to the library', 'No')

            COSMO_obj = {'AgeUniverse':COSMOS.Age_Universe(z),  \
                     'DL':units.length().mpc_to_cm(COSMOS.dl(z))}

            MTU.Info('At z, the universe was %.4f years old'%COSMO_obj['AgeUniverse'], 'No')

            ### d - here we check the template with too old ages at the given redshift
            Cosmo_Templates, Cosmo_Parameters = modif_LIB.COSMO_lib().Make_cosmological_Lib(COSMO_obj, \
                Templates_IGM, Parameter_IGM, IGM_param_names, self.conf.COSMO)

            #### e - Random selection of a template
            MTU.Info('Randomely select Template in the left over set of template', 'No')
            Nrandom = random.choice(numpy.arange(0, len(Cosmo_Templates)))

            ## f - and redshift the library:
            Wave_at_z, Templates_at_z = \
                    modif_LIB.COSMO_lib().prepare_lib_at_z(Cosmo_Templates[Nrandom], wave_rf, \
                    z, COSMO_obj)

            simFlux = Templates_at_z
            simPara = Cosmo_Parameters[Nrandom]
            if appliedIGM == 'no':
                simPara.append(0.0)
                simPara.append(0.0)
                simPara.append(0.0)
                IGM_param_names.append('LyaTr')
                IGM_param_names.append('LybTr')
                IGM_param_names.append('LygTr')

            ##simPara -> MET, TAU, age, M*, SFR, EBV, Lya, Lyb, Lyg

            #### g - Normalize the template
            MTU.Info('Normalize Template', 'No')
            Photo = Photometry.Photometry(self.filter_file)
            if self.DataT == 'Photo' or self.DataT == 'Combined':
                Normfluxsim, Normalisation = Photo.Normalise_template(Wave_at_z, simFlux, \
                        self.conf.PHOT['Norm_band'], NormMag)

            if self.DataT == 'Spectro':
                blist = list(self.conf.SPEC['Norm_band'].keys())
                Normfluxsim, Normalisation = Photo.Normalise_template(Wave_at_z, \
                        simFlux, blist[0], NormMag)

            ###add the normalisation to the mass and SFR
            simPara[3] = numpy.log10(simPara[3]*Normalisation)
            simPara[4] = numpy.log10(simPara[4]*Normalisation)

            ### h - simulate
            spectro = Spectroscopy.Spectroscopy()
            if self.DataT == 'Photo' or self.DataT == 'Combined':
                Photo_sim = Photo.simulate_photo(Wave_at_z, Normfluxsim, self.conf.PHOT['Band_list'])
                MTU.Info('Photometry has been simulated', 'No')
                ####chekc with plot
                #plot().template_and_mags(Wave_at_z, Normfluxsim, Photo_sim, z)

            if self.DataT == 'Spectro':
                spectro_sim = spectro.simu_spec_main(self.conf, Wave_at_z, Normfluxsim, StN, z, i[0])
                MTU.Info('Spectroscopy has been simulated', 'No')
                Photo_sim_spec = Photo.simulate_photo(Wave_at_z, Normfluxsim, \
                        self.conf.SPEC['Norm_band'])
                #plot().spec_template_mag(Wave_at_z, Normfluxsim, spectro_sim, Photo_sim_spec, z)

            if self.DataT == 'Combined':
                spectro_sim = spectro.simu_spec_main(self.conf, Wave_at_z, Normfluxsim, StN, z, i[0])
                MTU.Info('Spectroscopy has been simulated', 'No')
                #Photo_sim_spec = spec().combined_spectro_photometry(Photo_sim, self.conf)
                Photo_sim_spec = Photo.simulate_photo(Wave_at_z, Normfluxsim, \
                        self.conf.SPEC['Norm_band'])

                #Check_plots.plot().combined_template_mag(Wave_at_z, \
                        #Normfluxsim, spectro_sim, Photo_sim, z)


            ### i - and write them down
            out = simu_output.Output()
            if self.DataT == 'Photo':
                out.add_to_final_mag_file(Name_photo, self.PhotoDir, Photo_sim, \
                        z, self.Photofinalfile)
                out.add_to_output_param_file(z, Name_photo, simPara, self.final_param_file, NormMag)

            if self.DataT == 'Spectro':
                out.add_to_output_param_file(z, Name_spectro, simPara, self.final_param_file, NormMag)
                out.add_to_final_spec_file(Name_spectro, spectro_sim, Photo_sim_spec, \
                        z, self.Spectrofinalfile, self.SpectraDir)

            if self.DataT == 'Combined':
                out.add_to_final_mag_file(Name_Combined, self.PhotoDir, Photo_sim, \
                        z, self.Photofinalfile)
                out.add_to_final_spec_file(Name_Combined, spectro_sim, Photo_sim_spec, \
                        z, self.Spectrofinalfile, self.SpectraDir)
                out.add_to_final_comb_file(Name_Combined, spectro_sim, Photo_sim_spec, Photo_sim, \
                        z, self.Combinedfinalfile, self.SpectraDir)
                out.add_to_output_param_file(z, Name_Combined, simPara, self.final_param_file, NormMag)
            ### h - write parameters in file
            Name_file_para = '%s_N%s'%(self.conf.General['PName'], N)
            out.create_original_template(Wave_at_z, Normfluxsim, Name_file_para, \
                    self.original_template_dir)

            #time.sleep(1)

    def prepare_files(self):
        '''
        This method checks all the output files before starting to simulate
        objects.
        '''
        Out = simu_output.Output()

        ###### a - parameter file
        Out.create_output_param_file(self.final_param_file)

        ###### b - photometric file
        if self.DataT == 'Combined' or self.DataT == 'Photo':
            Out.create_final_mag_file(self.Photofinalfile, self.conf)

        ###### c - Spectroscopic file
        if self.DataT == 'Combined' or self.DataT == 'Spectro':
            Out.create_final_spec_file(self.Spectrofinalfile, self.conf)

        ###### d - Combined file
        if self.DataT == 'Combined':
            Out.create_final_comb_file(self.Combinedfinalfile, self.conf)

        ###### e - create original template dire
        if not os.path.isdir(self.original_template_dir):
            os.makedirs(self.original_template_dir)
