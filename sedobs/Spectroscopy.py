'''
The SPARTAN SIM Project
-------------------
Modul dealing with the spectroscopic computation

@Author R. THOMAS
@year   2017
@place  UV/LAM/UCBJ
@License: GNU public licence v3.0 - see LICENCE.txt
'''

####Python General Libraries
import os
import time
import copy

##third party
import numpy
import scipy.constants as const
from scipy.ndimage.filters import gaussian_filter, generic_filter


##local
from . import messages as MTU
from . import Check_plots as plot

class Spectroscopy:

    def __init__(self):
        """
        Class Constructor defining one attributes:
        """
        ###unit convertor
        ##speed of light
        c = const.c
        ##to angstrom/s
        ca = c * 1e10 
        #factor from l*l*F(l) to F(J)
        self.toJy = 1e23/ca

    def simu_spec_main(self, conf, wave, flux, STN, redshift, N, sky):
        '''
        Main of the spectroscopic simulation
        it loops over each spectrum to be simulated

        Parameters:
        ------------
        conf        global configuration of the project
        wave        1d array, template wavelength
        flux        1d array, template flux
        STN         float, required SNR
        redshift    float, redshift of the object
        N           int, number of the simulation
        sky         obj, sky properties for the current object

        Return
        ------
        spec_final  dict, with spectroscopic simulation

        '''
        spec_final = {}
        for i in range(int(conf.SPEC['NSpec'])):
            spec_indiv = {}
            blist = list(conf.SPEC['Norm_band'].keys())
            #spec_indiv['Norm_band'] = blist[i]
            spec_indiv['Noise_reg'] = conf.SPEC['Noise_reg'][i]
            spec_indiv['l0'] = conf.SPEC['types']['spec_%s'%str(i+1)]['l0']
            spec_indiv['lf'] = conf.SPEC['types']['spec_%s'%str(i+1)]['lf']
            spec_indiv['dl'] = conf.SPEC['types']['spec_%s'%str(i+1)]['dl']
            spec_indiv['res'] = conf.SPEC['types']['spec_%s'%str(i+1)]['res']
            spec_indiv['Atm'] = conf.SPEC['types']['spec_%s'%str(i+1)]['Atm']
            spec_indiv['skysub'] = conf.SPEC['types']['spec_%s'%str(i+1)]['skysub'] 
            spec_indiv['SNR'] = STN[i][N]
             
            ###simulate the spectrum
            wavespec, fluxnoised_skysub, noise_spec, OH = \
                self.simu_one_single_spec(spec_indiv, wave, flux, redshift, conf, sky)     

            spec_final[i+1] = {}
            if conf.SPEC['flux_unit'] == 'Jy':
                fluxnoised_skysub = fluxnoised_skysub * wavespec * wavespec * self.toJy 
                noise_spec = noise_spec * wavespec * wavespec * self.toJy 
                OH = OH * wavespec * wavespec * self.toJy

            if conf.SPEC['flux_unit'] == 'muJy':
                fluxnoised_skysub = fluxnoised_skysub * wavespec * wavespec * self.toJy * 1e6 
                noise_spec = noise_spec * wavespec * wavespec * self.toJy * 1e6
                OH = OH * wavespec * wavespec * self.toJy * 1e6
                
            if conf.SPEC['wave_unit'] == 'log_ang':
                wavespec = numpy.log10(wavespec)

            spec_final[i+1]['wave'] = wavespec
            spec_final[i+1]['flux'] = fluxnoised_skysub
            spec_final[i+1]['noise'] = noise_spec
            spec_final[i+1]['OH'] = OH
            spec_final[i+1]['skysub'] = spec_indiv['skysub']

            MTU.Info('Spectrum #%s with STN %s have been simulated'%(i+1, STN[i][N]), 'No')

        return spec_final

    def simu_one_single_spec(self, spec_conf, wave, flux, redshift, conf, sky):
        '''
        This function simulate the spectrum,
                #change the resolution
                #cut it
                #add noise
            All thes steps are in different function

        Parameters
        ----------
        spec_conf   dict, with spectral configuration for this spectru
        wave        1d array with wavelength
        flux        1d array with template flux
        redshift    float, redshift
        conf        global configuration
        sky         obj, sky properties

        Return
        ------
        wave_cut    1d array with spectral wavelegnth
        flux_noised 1d array with noisy flux
        noise_spec  1d array with noise spectrum
        '''
        fluxcp = copy.copy(flux)

        ###1 - Change the resolution
        ##### a - retrieve the resolution of the models
        Rmodel = self.model_res(conf.Template['BaseSSP']) 
        smoothed_template = self.change_resolution(fluxcp, wave, redshift, Rmodel, spec_conf)           

        ###2 - we cut the template in the regions of interest
        wave_cut, flux_cut = self.cut_spec(wave, smoothed_template, spec_conf['l0'],\
                spec_conf['lf'], spec_conf['dl'])

        ####3 - if sky is required, we change the resolution of the sky as well
        if spec_conf['Atm'] != 'none':
            ###OH emission
            Rsky = [[11500, 10., 100000.]]
            skywave = sky.sky[spec_conf['Atm']]['OH_full'][0]
            skyOH = sky.sky[spec_conf['Atm']]['OH_full'][1] 
            smoothed_sky = self.change_resolution(skyOH, skywave, 0, Rsky, spec_conf)           
            wave_cutsky, flux_cutsky = self.cut_spec(skywave, smoothed_sky, spec_conf['l0'],\
                spec_conf['lf'], spec_conf['dl'])
            #plot.plot().spec_sim(skywave, skyOH, wave_cutsky, flux_cutsky, 0, spec_conf)
            MTU.Info('OH lines are applied for spectroscopy simulation', 'No')
        else:
            ext_cut = numpy.ones(len(flux_cut))
            flux_cutsky = numpy.zeros(len(flux_cut))

        flux_cut = flux_cut + (1-spec_conf['skysub'])*flux_cutsky
        #plot().spec_sim(wave, flux, wave_cut, flux_cut, redshift, spec_conf)
        ###4 - we compute the noise 
        flux_noised_withsky, noise_spec = self.add_noise(wave_cut, flux_cut, spec_conf, redshift)

        return wave_cut, flux_noised_withsky, noise_spec, flux_cutsky 

    def add_noise(self, wave, flux, specconf, Redshift):
        '''
        This function add noise to the spectrum

        Parameter
        ---------
        wave    1d array with awvelength
        flux    1d array with flux
        specconf dictionnary with spectral configuration for this spectrum
        Redshift    float, redshift of the object
        

        Return
        -------
        flux_noised     1d array with noised flux
        noised_spectrum 1d array with noise spectrum
        '''
        
        ####first we extract the region where we compute the StN
        ####!!!WARNING they are given in rf
        Noise_reg = specconf['Noise_reg'].strip(')').strip('(').split(',')
        Noise_reg_i = float(Noise_reg[0])*(1+Redshift)
        Noise_reg_f = float(Noise_reg[1])*(1+Redshift)
        
        ####Select the region in the spectrum
        cut = numpy.where(numpy.logical_and(numpy.greater_equal(wave,Noise_reg_i),\
                numpy.less_equal(wave, Noise_reg_f)))

        wave_reg = wave[cut]
        flux_reg = flux[cut]
        ###and compute the mean flux in this region
        mu = numpy.mean(flux_reg) 

        ##now we use the SNR to compute the sigma of the flux
        sigma = mu / specconf['SNR']

        ##generate the error
        N = numpy.random.normal(0, numpy.abs(sigma), len(wave))

        ##and add it to the flux
        flux_noised = N + flux 
        
        ###create the final noise spectrum
        ###First we generate the noise spectrum 
        noise_spectrum = generic_filter(flux_noised, self.MAD, size=30)

        #plot().spec_noised(wave, flux, wave, noise_final, Redshift, specconf)

        return flux_noised, noise_spectrum
        
    def MAD(self, flux):
        '''
        This method compute the Median Aboslute Deviation from an array.
        Defined by MAD = median(|array_i - median(array)| 

        Parameter:
        ----------
        flux,  1d array of values from which we wanna compute the MAD

        Return:
        -------
        MAD     float, MAD
        '''
        MAD = numpy.median( numpy.abs( flux - numpy.median(flux) ) )
        return MAD


    def change_resolution(self, template, wave_template,  Redshift, R, specconf):
        '''
        This method adjust the resolution of the model to the resolution
        of the spectra.

        For data at a resolution of X (in Ang) and model at a resolution of Y (in Ang)
        we apply a gaussian filter to each template with a disperstion Z given by

        Z = sqrt(X*X - Z*Z)

        !!!!WARNING!!!!!
        This is applied IF AND ONLY IF the resolution of the data is smaller 
        than the one of the model

        Parameters:
        ----------
        template        numpy ndarray, library of template
        wave_template   1d array, of wavelength for the template
        Redshift        float, redshift of the observation
        R               list, resolution of the model (see self.model_res )
        specconf        dict, configuration of the spectrum to simulate
            
        Return
        --------
        flux_res        list of flux at the right resolution (same wave grid as original)
        '''
        
        minw = specconf['l0']
        maxw = specconf['lf']
        middle = minw + (maxw-minw)/2
        ### index of the wavelength in the templates we take slightly
        ###larger to make sure, we do it in the restframe
        index_min = (numpy.abs(wave_template-minw/(1+Redshift))).argmin()-1
        index_max = (numpy.abs(wave_template-maxw/(1+Redshift))).argmin()+1
        ###############we loop over the list of resolution
        ##number of different model resolution overlapping to the data
        N = 0 
        ###resolution list
        Rlist = []
        for i in R:
            ##retrieve models resolution wavelenth limits
            minRw = i[1]
            maxRw = i[2]
            ##check if the spectra wavels are all in the range
            ##defined by minRw and maxRw

            if minw/(1+Redshift)>minRw and maxw/(1+Redshift)<maxRw:
                #if this is the case we does not move anything
                N = 'ok'
                Rlist.append(i[0])
            else:
                if N !='ok':##if it is not ok we increment N
                    if (minRw<minw/(1+Redshift)<maxRw):
                        N+=1
                        Rlist.append([i[0], minw/(1+Redshift), maxRw])
                    if (minRw<maxw/(1+Redshift)<maxRw):
                        N+=1
                        Rlist.append([i[0], minRw, maxw/(1+Redshift)])

        ###if N==ok we need only one resolution
        if N == 'ok':
            
            #Resolution of the models in the rest frame
            Res_mod = middle / (1+Redshift) / Rlist[0]

            ##resolution of the data
            ResolvingPOwer = float(specconf['res'])
            Res_rf = middle/ResolvingPOwer/(1+Redshift)

            ####We apply it
            if Res_mod > Res_rf:
                ###we do not change the templates
                return template
            else:
                ###we have to smooth the templates
                ###FWHM to sigma :
                ratio = 2 * numpy.sqrt(2*numpy.log(2))
                smooth = numpy.sqrt((Res_rf)**2 - (Res_mod)**2)/ratio
                ###here come the tricks. My guess is that the gaussian_filter function
                ###in scipy works well only if the grid of wavelength is binned with 1A
                ###gaps. Tried with 20AA grid and it everything was washed out.
                ###therefore, here, for each template, we regrid the region of interest
                ###to one angstrom, then we smooth it, and finally we re-regrid it to
                ###the orginal grid---> might be faster way but this is that one for the
                ###moment

                ##we put back the template in restframe
                wave_rf = wave_template/(1+Redshift)
 
                ###create the rf 1-A binned grid                
                waveinterp = numpy.arange(wave_rf[0], wave_rf[-1], 1) 

                ###we interpolate to 1A in the rf
                temp = numpy.interp(waveinterp, wave_rf, template)
                
                ##and smooth it 
                smoothed_template = gaussian_filter(temp, smooth)
                
                ##and put it back to the normal grid
                smoothed_template = numpy.interp(wave_rf, waveinterp, smoothed_template)


                return smoothed_template

        #if N!= 'ok' we need more than one resolution
        if N != 'ok':
            a='tobedone'
            ##we put back the template in restframe
            wave_rf = wave_template/(1+Redshift)
           
            allwaves = []
            all_regions = []
            all_wave = []
            for r in Rlist:
                
                ###select the right wavelength range
                index_min_reg = (numpy.abs(wave_rf-r[1])).argmin()
                index_max_reg = (numpy.abs(wave_rf-r[2])).argmin()
                wave_rf_reg = wave_rf[index_min_reg:index_max_reg]
                region_template = template[index_min_reg:index_max_reg]

                allwaves.append(wave_rf_reg[0])
                allwaves.append(wave_rf_reg[-1])

                ###look at the resolution
                    ###observation
                ResolvingPOwer = float(specconf['res']) 
                Res_rf = middle/ResolvingPOwer/(1+Redshift)

                    #Resolution of the models in the rest frame
                Res_mod = middle / (1+Redshift) / r[0]

                if Res_mod > Res_rf:
                    all_regions.append(region_template)
                    all_wave.append(wave_rf_reg)
                else:
                    ##!!!!!!!!!!see above for explanation!!!!!!!!!!
                    ratio = 2 * numpy.sqrt(2*numpy.log(2))
                    smooth = numpy.sqrt((Res_rf)**2 - (Res_mod)**2)/ratio
                    ###create the rf 1-A binned grid                
                    waveinterp = numpy.arange(wave_rf_reg[0], wave_rf_reg[-1], 1) 

                    ###we interpolate to 1A in the rf
                    temp = numpy.interp(waveinterp, wave_rf_reg, region_template)
                
                    ##and smooth it 
                    smoothed_template = gaussian_filter(temp, smooth)
                
                    ##and put it back to the normal grid
                    smoothed_template = numpy.interp(wave_rf_reg, waveinterp, smoothed_template) 
                    all_regions.append(smoothed_template)
                    all_wave.append(wave_rf_reg)
            
            ### We concatenate all the regions
            final = numpy.concatenate(all_regions)
            all_wave = numpy.concatenate(all_wave)
            ##retrieve the external part of the template
            minin = min(allwaves)
            maxin = max(allwaves)

            ###and create the final spectrum
            fluxall = []
            finalwave = []
            for i in range(len(wave_rf)):
                if wave_rf[i]<=minin-1:
                    fluxall.append(template[i])
                    finalwave.append(wave_rf[i])

            for i in range(len(final)):
                fluxall.append(final[i])
                finalwave.append(all_wave[i])
                    
            for i in range(len(wave_rf)):
                if wave_rf[i]>maxin:
                    fluxall.append(template[i])
                    finalwave.append(wave_rf[i])
        

            return fluxall



    def cut_spec(self, wave, flux, l0, lf, dl):
        '''
        This method cuts the spectrum in the region of interest (lo -> lf)
        To do so we create the new grid from l0, lf and dl
        and interpolate the original template on it
        Parameter:
        ---------
        wave        list, of observed wavelength
        flux        list, of observed flux
        l0          flt, first wavelentght og the spectrum
        lf          flt, last      ''       ''
        dl          dl, size on the bin

        return:
        -------
        new_grid        list, of observed wavelength
        new_flux        list, of flux interpolated in new_grid
        '''

        ###prepare the grid
        new_grid = numpy.arange(l0, lf, dl)
        
        ###interpolate the flux in the new grid
        new_flux = numpy.interp(new_grid, wave, flux)
    
        return new_grid, new_flux

    def model_res(self, baseSSP):
        '''
        Method that give the resolution of the SSP chosen by the user

        The resolution is the median resolution of the full templates
        if there is one resolution only (like BC03 at low resolution)
        or a list of resolution if the resolution is varying drastically
        inside the template (like BC03 at high resolution)

        Parameter
        ---------
        baseSSP     str, of the baseSSP used by the user

        return
        ------
        R           list, of resolving power of the model with wavelength range
        '''
        
        name = os.path.basename(baseSSP)
        if name[4:8] == 'BC03':
            #if we find LR in the name
            if baseSSP.find('LR') != -1:
                #1 zone to define
                R = [[300, 91, 160000]]

            #if we find HR in the name
            else:
                #3 zines to define
                R = [[300,91,3200], [2000,3200,9500] , [300, 9500, 16000]]


        return R


    def combined_spectro_photometry(self, Photosim, conf):
        '''
        Method that select the photometric simulation for the spectroscopy
        when both have been asked by the user.

        Parameter
        ---------
        Photosim    dict, simulated photometry
        conf        dict, configuration of the run
        
        Return
        ------
        Photo_sim_spec  dict, of magnitude for spectroscopy
        '''
        specbands = conf.SPEC['Norm_band']
        Photo_sim_spec = {}
        for i in specbands:
            for j in Photosim:
                if i == j:
                    Photo_sim_spec[i] = {}
                    Photo_sim_spec[i]['Meas'] = Photosim[j]['Meas']
                    Photo_sim_spec[i]['Flux'] = Photosim[j]['Flux']
                    Photo_sim_spec[i]['Err'] = Photosim[j]['Err']
                    Photo_sim_spec[i]['Leff'] = Photosim[j]['Leff']

        return Photo_sim_spec
