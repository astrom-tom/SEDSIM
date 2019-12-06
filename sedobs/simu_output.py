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

##third party
import numpy
import scipy.constants as const

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
        Header = '#ID_sim\tredshift\tMag\tMet\tTAU\tAGE\tMass\tSFR\tAvs\tRvs\tTrLya\tTrLyb\tTrLyg'
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
        Age = numpy.log10(P[2])
        Mst = P[3]
        SFR = P[4]
        Avs = P[5]
        Rvs = P[6]
        TrLya = P[7]
        TrLyb = P[8]
        TrLyg = P[9]

        line += '\t%1.4f\t%1.4e\t%1.4f\t%1.4f\t%1.4f\t%1.4f\t%1.4f\t%1.4f\t%1.4f\t%1.4f\t%1.4f'\
                %(Normmag, MET, TAU, Age, Mst, SFR, Avs, Rvs, TrLya, TrLyb, TrLyg)

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

    def add_to_final_spec_file(self, Name, Namesky, Spectrosim, Photosim, \
            redshift, Filemag, spectrodir):
        '''
        This method allows to add a file to the spectroscopic file
        '''
        ###the line start by Name and redshift
        line = '\n%s\t%s'%(Name[0:-4], redshift)
        N = 1
        for i, j in zip(Photosim, Spectrosim):
            name = Name[:-4] + '_%s'%N + '.spec'
            namesky = Namesky + '_%s'%N + '.spec'
            self.create_indiv_spec_files(name, namesky, spectrodir, Spectrosim[j])
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

    def add_to_final_comb_file(self, Name, Namesky, Spectrosim, Photosimspec, \
            Photosim, redshift, File, spectrodir):
        '''
        This method allows to add a file to the spectroscopic file
        '''

        ###the line start by Name and redshift
        line = '\n%s\t%s'%(Name[0:-4], redshift)
        N = 1
        for i, j in zip(Photosimspec, Spectrosim):
            name = Name[:-4] + '_%s'%N + '.spec'
            namesky = Namesky + '_%s'%N + '.spec'
            self.create_indiv_spec_files(name, namesky, spectrodir, Spectrosim[j])
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
        h = '#wavelength\twavelength_err\tmag_tempsky\tflux_tempsky\tmag_final\terror_mag\tflux_final\terror_flux\tmag_sky\tFlux_sky\n'
        ##open and write to file
        with open(fullname, 'w') as ff:
            ###first the header
            ff.write(h)
            #then the photometry
            for i in photosim:
                band = photosim[i]
                line = '%6.4f\t%6.4f\t%1.4f\t%.4E\t%1.4f\t%1.4f\t%.4E\t%.4E\t%1.4f\t%.4E\n'%(\
                        band['Leff'], band['wave_err'], band['Measori'], band['Fluxori'], \
                        band['Meas'], band['Err'], band['Flux'], band['FluxErr'], \
                        band['Mag_sky'], band['Flux_sky'])
                

                ff.write(line)



    def create_indiv_spec_files(self, name, namesky, folder, spectro):
        '''
        Method that writes down the spectrum as ascii data
        parameter:
        ---------
        name    str, name of the spectrum --> name of the file
        namesky str, name of the spectrum --> name of the file
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
        
        namedirsky = os.path.join(folder, namesky+'.dat')
        wave = spectro['wave']
        sky = spectro['OH']
        with open(namedirsky, 'w') as ff:
            for i in enumerate(wave):
                w = wave[i[0]]
                s = (1-spectro['skysub']) * sky[i[0]]
                line = '%s\t\t%s\n'%(w, s)
                ff.write(line)



    def create_original_template(self, wave, flux, name, dire, conf):
        '''
        Method that creates the file with the original template

        Parameter
        ---------
        wave    list, of wavelength
        flux    list, of flux
        name    str, name
        dir     str, directory
        conf    str, spectral confioguration (for unit)
        '''
        ##speed of light
        c = const.c
        ##to angstrom/s
        ca = c * 1e10
        #factor from l*l*F(l) to F(J)
        toJy = 1e23/ca

        if conf['flux_unit'] == 'Jy':
            flux = flux * wave * wave * toJy 

        if conf['flux_unit'] == 'muJy':
            flux = flux * wave * wave * toJy * 1e6 
            
        if conf['wave_unit'] == 'log_ang':
            wave = numpy.log10(wave)

        name = name + '_original.dat'
        fullname = os.path.join(dire, name)
        with open(fullname, 'w') as FF:
            for i in range(len(flux)):
                line = '%s\t%s\n'%(wave[i], flux[i])
                FF.write(line)

##############SKY########################
    def create_sky_cat(self, sky_file, conf):
        '''
        This method checks if the sky catalog exists. If it does
        we remove it. If it does not we create it
        Parameter
        ---------
        Sky_file    str, path/and/name to the sky catalog
        conf        str, configuration dict from user

        Return
        ------
        #nothing we just create a catalog
        '''

        ###first we check presence
        if os.path.isfile(sky_file):
            MTU.Info('Output Sky catalog file already exists, we remove it', 'No')
            os.remove(sky_file)

        else:
            ##if not there we create it
            MTU.Info('Output Sky catalog file does not exist, we create it', 'No')

        Header = '#This catalog display the type of sky that was used\n'+\
                '#giving the range that was considered and\n'+\
                '#the corresponding AM value\n'
        sky = open(sky_file, 'w')
        sky.write(Header)
        sky.close()

    def add_toskycat(self, sky, File, Namesim):
        '''
        Add the line to the sky catalog
        Parameters:
        -----------
        sky     obj, sky configuration
        File    str, file to which we are adding the line
        Namesim str, Name of the simulated galaxy
        '''
        ##for each range we take the AM
        line = ''
        line += '%s\t%1.4f\t%.4E\t'%(Namesim[:-4], sky.skymag, sky.skyflux)
        for i in sky.sky:
            line += '%s\t%s\t'%(i, sky.sky[i]['AM'])
        line += '\n' 

        ##and write the line
        with open(File, 'a') as out:
            out.write(line)

    def create_sky(self, sky, skydir, Name_sky_file, Photo_sim, conf):
        '''
        This method writes down the sky spectra used for the simulation
        This is done only if the photometry was simulated. In the case of 
        spectroscopy the skyspectrum, at the right resolution is saved 
        automatically
        Parameters
        ----------
        sky
                obj, sky configuration
        skydir
                str, path to the sky directory
        Name_sky_file
                str, name of the sky file
        Photo_sim
                dict, with photometric simuation
        conf
                dict, photometric configuration
        '''
        ###unit convertor
        ##speed of light
        c = const.c
        ##to angstrom/s
        ca = c * 1e10
        #factor from l*l*F(l) to F(J)
        toJy = 1e23/ca

        ##get limit of photometry
        allLeff = []
        for i in Photo_sim:
            band = Photo_sim[i]
            allLeff.append(band['Leff'])

        wmin = min(allLeff) - 1000
        wmax = max(allLeff) + 1000

        ##loop over sky configuration
        for i in sky.sky:
            if i != 'none':
                name = Name_sky_file + i + '.dat'
                header = '#For %s AM=%s\n'%(Name_sky_file, sky.sky[i]['AM'])
                wave = sky.sky[i]['OH'][0]
                flux = sky.sky[i]['OH'][1]

                if conf['flux_unit'] == 'Jy':
                    flux = flux * wave * wave * toJy 

                if conf['flux_unit'] == 'muJy':
                    flux = flux * wave * wave * toJy * 1e6 
                    
                if conf['wave_unit'] == 'log_ang':
                    wave = numpy.log10(wave)

                with open(os.path.join(skydir, name), 'w') as f:
                    f.write(header)
                    for j in range(len(wave)):
                        if wmin < wave[j] < wmax:
                            f.write('%s\t%s\n'%(wave[j], flux[j]))
