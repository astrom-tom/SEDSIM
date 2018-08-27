'''
############################
#####
##### The Spartan SIM Project
#####      R. THOMAS
#####        2017
#####
#####   source code that makes
#####        the output
#####    of the simulation
###########################
@License: GNU Public licence V3
'''

##### Python General Libraries
import os
import numpy
import time

##### SPARTAN modules
from . import messages as MTU

class Output:
    '''
    This class deals with all the output files that are written
    during the simulations
    '''
    def create_output_param_file(self, param_file):
        '''
        this method checks if the parameter file exists. If it does
        we check the last row to get the last name that was computed
        If it does not we create it
        Parameter
        ---------
        param_file  str, path/and/name to the parameter file
        conf        str, configuration dict from user

        Return
        ------
        last_row    int, number of the last row

        '''
        ###first we check presence
        if os.path.isfile(param_file):
            MTU.Info('Output Parameter file already exists, remove it', 'No')
            os.remove(param_file)

        MTU.Info('Output Parameter file does not exist, we create it', 'No')
        Header = '#ID_sim\tredshift\tMag\tSNR\tMet\tTAU\tAGE\tMass\tSFR\tEBV\tTrLya'
        par_file = open(param_file, 'w')
        par_file.write(Header)
        par_file.close()


    def add_to_output_param_file(self, redshift, Name, P, paramfile, Normmag):
        '''
        Method that add line to the parameter file
        Parameters:
        redshift    float, redshift
        name        str, name of the simu
        paramfile   str, parameter file (path/and/name)
        Normmag     float, nromalisation magnitude
        '''

        ###the line start by Name and redshift
        line = '\n%s\t%s'%(Name, redshift)
        MET = P[0]
        TAU = P[1]
        Age = P[2]
        Mst = P[3]
        SFR = P[4]
        EBV = P[5]
        TrLya = P[6]

        line += '\t%1.4f\t%1.4f\t%1.4f\t%1.4e\t%1.4f\t%1.4f\t%1.4f\t%1.4f'%(Normmag, MET,\
                TAU, Age, Mst, SFR, EBV, TrLya)

        with open(paramfile, 'a') as out:
            out.write(line)



################MAGfile######################
    def create_final_mag_file(self, photo_file, conf):
        '''
        this method checks if the photometric file exists. If it does
        we check the last row to get the last name that was computed
        If it does not we create it
        Parameter
        ---------
        photo_file  str, path/and/name to the photometric file
        conf        str, configuration dict from user

        Return
        ------
        last_row    int, number of the last row
        '''
        ###first we check presence
        if os.path.isfile(photo_file):
            MTU.Info('Output Photometric file already exists, we remove it', 'No')
            os.remove(photo_file)

        else:
            ##if not there we create it
            MTU.Info('Output Photometric file does not exist, we create it', 'No')

        listband = conf.PHOT['Band_list'].keys()
        Header = '# ident\tredshift\t'
        for i in listband:
            Header += '%s\t%s_err\t'%(i, i)
        pho_file = open(photo_file, 'w')
        pho_file.write(Header)
        pho_file.close()

    def add_to_final_mag_file(self, Name, Photodir, Photosim, redshift, Filemag):
        '''
        Method that add line to the photometric file
        Parameters:
        ----------
        redshift    float, redshift
        Name        str, name of the simu
        Filemag     str, photometric file (path/and/name)
        Photosim    dict, with photometric information
        '''
        ###the line start by Name and redshift
        line = '\n%s\t%s'%(Name[0:-4], redshift)
        self.create_indiv_phot_files(Name, Photodir, Photosim)

        for i in Photosim:
            if Photosim[i]['Meas'] != numpy.inf:
                line += '\t%.4f\t%.4f'%(Photosim[i]['Meas'], Photosim[i]['Err'])
            else:
                line += '\t-99.9\t-99.9'

        with open(Filemag, 'a') as out:
            out.write(line)


################SPECTRAL#####################
    def create_final_spec_file(self, spectro_file, conf):
        '''
        This method checks if the spectroscopy file exists. If it does
        we check the last row to get the last name that was computed
        If it does not we create it
        Parameter
        ---------
        spectro_file  str, path/and/name to the photometric file
        conf        str, configuration dict from user

        Return
        ------
        last_row    int, number of the last row
        '''
        ###first we check presence
        if os.path.isfile(spectro_file):
            MTU.Info('Output Spectroscopic file does exist, we remove it', 'No')
            os.remove(spectro_file)
        ##if not there we create it
        else:
            MTU.Info('Output Spectroscopic file does not exist, we create it', 'No')

        listspec = conf.SPEC['Norm_band']
        Header = '# ident\tredshift\t'
        for i in enumerate(listspec):
            Header += 'spec%s\t%s\t%s_err\t'%(i[0]+1, i[1], i[1])

        spec_file = open(spectro_file, 'w')
        spec_file.write(Header)
        spec_file.close()

    def add_to_final_spec_file(self, Name, Spectrosim, Photosim, redshift, Filemag, spectrodir):
        '''
        This method allows to add a file to the spectroscopic file
        '''
        ###the line start by Name and redshift
        line = '\n%s\t%s'%(Name[0:-4], redshift)
        N = 1
        for i, j in zip(Photosim, Spectrosim):
            name = Name[:-4]+'_%s'%N+'.spec'
            self.create_indiv_spec_files(name, spectrodir, Spectrosim[j])
            line += '\t' + name + '\t%.4f\t%.4f'%(Photosim[i]['Meas'], Photosim[i]['Err'])
            N += 1

        with open(Filemag, 'a') as out:
            out.write(line)



##############COMBINED#######################
    def create_final_comb_file(self, comb_file, conf):
        '''
        This method checks if the combined file exists. If it does
        we check the last row to get the last name that was computed
        If it does not we create it
        Parameter
        ---------
        comb_file   str, path/and/name to the photometric file
        conf        str, configuration dict from user

        Return
        ------
        last_row    int, number of the last row
        '''
        ###first we check presence
        if os.path.isfile(comb_file):
            MTU.Info('Output Combined file does exist, remove it and create new one', 'No')
            os.remove(comb_file)

        ##if not there we create it
        else:
            MTU.Info('Output Combined file does not exist, we create it', 'No')

        Header = '# ident\tredshift\t'
        ###add the spectram
        listspec = conf.SPEC['Norm_band']
        for i in enumerate(listspec):
            Header += 'spec%s\t\t%s\t%s_err\t'%(i[0]+1, i[1], i[1])
        ###add the band
        listband = conf.PHOT['Band_list'].keys()
        for i in listband:
            Header += '%s\t%s_err\t'%(i, i)

        comb_file = open(comb_file, 'w')
        comb_file.write(Header)
        comb_file.close()

    def add_to_final_comb_file(self, Name, Spectrosim, Photosimspec, \
            Photosim, redshift, File, spectrodir):
        '''
        This method allows to add a file to the spectroscopic file
        '''

        ###the line start by Name and redshift
        line = '\n%s\t%s'%(Name[0:-4], redshift)
        N = 1
        for i, j in zip(Photosimspec, Spectrosim):
            name = Name[:-4]+'_%s'%N+'.spec'
            self.create_indiv_spec_files(name, spectrodir, Spectrosim[j])
            line += '\t' + name + '\t%.4f\t%.4f'%(Photosimspec[i]['Meas'], Photosimspec[i]['Err'])
            N += 1

        for i in Photosim:
            if Photosim[i]['Meas'] != numpy.inf:
                line += '\t%.4f\t%.4f'%(Photosim[i]['Meas'], Photosim[i]['Err'])
            else:
                line += '\t-99.9\t-99.9'

        with open(File, 'a') as out:
            out.write(line)

##############################################################

    def create_indiv_phot_files(self, name, folder, photosim):
        '''
        Method that writes down the individual photometry file 
        as ascii data
        parameter:
        ---------
        name     str,  name of the photometry --> name of the file
        folder   str,  folder where the spectra will be stored
        photosim dict, with photometric simuation
        '''
        name = name + '_phot.txt'
        fullname = os.path.join(folder, name)
        ###header
        h = '#wavelength\twavelength_err\tmag_template\tmag_template_flux\tmagfinal\terrormag\tfluxfinal\terrorflux\n'
        ##open and write to file
        with open(fullname, 'w') as ff:
            ###first the header
            ff.write(h)
            #then the photometry
            for i in photosim:
                band = photosim[i]
                line = '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n'%(band['Leff'], band['wave_err'], \
                        band['Measori'], band['Fluxori'], band['Meas'], band['Err'], \
                        band['Flux'], band['FluxErr'])
                

                ff.write(line)



    def create_indiv_spec_files(self, name, folder, spectro):
        '''
        Method that writes down the spectrum as ascii data
        parameter:
        ---------
        name    str, name of the spectrum --> name of the file
        folder  str, folder where the spectra will be stored
        spectro dict, with spectroscopic simuation
        '''

        namedir = os.path.join(folder, name)
        wave = spectro['wave']
        flux = spectro['flux']
        noise = spectro['noise']
        with open(namedir, 'w') as ff:
            for i in enumerate(wave):
                w = wave[i[0]]
                f = flux[i[0]]
                n = noise[i[0]]
                line = '%s\t\t%s\t\t%s\n'%(w, f, n)
                ff.write(line)



    def create_original_template(self, wave, flux, name, dire):
        '''
        Method that creates the file with the original template

        Parameter
        ---------
        wave    list, of wavelength
        flux    list, of flux
        name    str, name
        dir     str, directory
        '''

        name = name + '_original.dat'
        fullname = os.path.join(dire, name)
        with open(fullname, 'w') as FF:
            for i in range(len(flux)):
                line = '%s\t%s\n'%(wave[i], flux[i])
                FF.write(line)
