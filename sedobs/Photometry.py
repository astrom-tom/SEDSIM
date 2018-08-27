'''
The SPARTAN SIM Project
-------------------
Modul dealing with the photometric computation

@Author R. THOMAS
@year   2017
@place  UV/LAM/UCBJ
@License: GNU public licence v3.0 - see LICENCE.txt
'''

####Python General Libraries
import numpy

##SPARTAN libraries
from . import units
from . import filters

class Photometry:
    """
    This class deals with action that need to retrieve
    a filter name or to get filter data
    It implements 3 methods:
    """

    def __init__(self, filterfile):
        """
        Class Constructor defining one attributes:

        self. Filterfile    The location of the filter file, and the file
        """

        self.filterfile = filterfile

    def Normalise_template(self, wave, flux, band, Norm):
        '''
        this methods normalise the template (wave, flux) to the
        maganitude (Norm) in the given band
        '''
        ##1 - Compute the magnitude
        magAB, fluxmag, Leff, FWHM = self.Compute_mag_from_template(wave, flux, band)

        ##2 - Convert the normalisation magnitude to flux
        fluxNormmag = self.mag2flux(Norm, Leff)

        ##3 - compute the ratio of flux
        r = fluxNormmag / fluxmag
        
        ##4 - normalise the template
        Norm_flux = r * flux

        ###for checking we recompute the magnitude from the normalized
        ###flux
        #newmag, newfluxmag, Leff, FWHM = self.Compute_mag_from_template(wave, Norm_flux, band)

        #print(newmag, newfluxmag)

        return Norm_flux, r

    def simulate_photo(self, wave, flux, band_list):
        '''
        Method that simulate the photometry. First we compute
        the magnitude in the bands and then the errors
        Parameter:
        ----------
        wave        list, of observed wavelength
        flux        list, of observed flux (normalised) 
        band_list   list, of band and error
        '''
        ###extract band names from the the list
        band_names = band_list.keys()

        ###loop over each band
        Photo_sim = {}
        for i in band_names:
            Photo_sim[i] = {}
            ##compute the magnitude in the band
            magAB, fluxAB, Leff, FWHM= self.Compute_mag_from_template(wave, flux, i)

            ###and simulate the error
            err = self.simulate_error_phot(band_list[i][1], band_list[i][2] )

            ###simulate offset
            zp = band_list[i][0]

            ###add the error to the measurement
            magABzp =  magAB+zp
            fluxABzp = self.mag2flux(magABzp, Leff)

            ##and save it
            Photo_sim[i]['Measori'] = magAB  ##Template real magnitude
            Photo_sim[i]['Fluxori'] = fluxAB ##Flux rea; Magnitude
            Photo_sim[i]['Meas'] = magABzp  ##magnitude with offset
            Photo_sim[i]['Flux'] = fluxABzp ## flux with offset
            Photo_sim[i]['Err']  = numpy.abs(err) ##err on the magnitude
            Photo_sim[i]['FluxErr'] = numpy.abs(err)*fluxAB*numpy.log(10)/2.5###error on the flux
            Photo_sim[i]['Leff'] = Leff ### effective wavelength of the filter 
            Photo_sim[i]['wave_err'] = FWHM / 2. 

        return Photo_sim

    def simulate_error_phot(self, m, sig):
        '''
        Method that simulate the error on the flux
        from the mean and sigma given by the user
        '''
        ##extract mean and sigma
        sigma = sig
        mu = m

        ##random generation of the error
        s = numpy.random.normal(mu, sigma, 1)
        return s[0]


    def Compute_mag_from_template(self, wave, flux, band):
        '''
        This method compute the magnitude from a template (wave, flux)

        Parameter:
        ----------
        wave    list, of redshifted wavelength
        flux    list, of redshifted flux
        band    str,  name of the band in which we want to normalize the template

        Return:
        -------
        flux_Norm list, of normlized and redshifted flux
        '''

        ###convert template to frequence space
        freqTemp, Template_hz = self.convert_wave_to_freq(wave, flux)

        ###retrieve filter information
        Lambda, Tran, Leff, FWHM = filters.Retrieve_Filter_inf(self.filterfile).retrieve_one_filter(band)

        ##interpolate the filter throughput to the wavelength grid
        Trans_wave_model = numpy.interp(wave, Lambda, Tran)
        ##and Normalise it
        ###WARNING!!: [::-1] because for the integration of y=f(x), x must be increasing
        Normalisation = numpy.trapz(Trans_wave_model, freqTemp[::-1])
        TranfreqNormed = Trans_wave_model / Normalisation
        
        ###make the integration
        integration = numpy.trapz(Template_hz*TranfreqNormed, freqTemp[::-1])

        ###and compute magnitude
        MagAB = -2.5*numpy.log10(integration)-48.60

        Fluxmag = self.mag2flux(MagAB, Leff)
        
        #plt().Filter_template(wave, flux, Lambda, Tran, Leff, FWHM, Fluxmag)
        return MagAB, Fluxmag, Leff, FWHM


    def convert_wave_to_freq(self, wave, Templates):
        '''
        Module that convert an array of Template in erg/s/cm2/Ang to
                            an array of Template in erg/s/cm2/Hz

        To make this computation we follow
              lambda*F(lambda) = nu * F(nu)
              so F(nu) = (lambda/nu) * F(lambda)
        and since nu = c / lambda
           --> So we have F(nu) = (lambda^2 / c) * F(lambda)

        Note: It works also for individual templates
        ----
        Parameter
        ---------
        wave        1D array, wavelength of the template
        Templates   ND array, of template flux in erg/s/cm2/Ang

        Return
        ------
        Template_hz NDarray, of template flux in erg/s/cm2/Ang
        freq        1Darray, of freq from the wavelength
        '''

        ## so we retrieve the speed of light and convert it to Ang/s
        c = units.length().m_to_ang(units.Phys_const().speed_of_light_ms())
        ##and finally we convert the array
        Template_hz = Templates * (wave**2/c)
        ## and the wavelength
        freq = c / wave

        return freq, Template_hz


    def mag2flux(self, mag, Leff):
        '''        
        Method that convert magnitude into flux in Ang
        Parameter
        ---------
        mag     float or list of float, of magnitude in AB system to compute
        Leff    float, effective wavelength of the filter

        Return
        ------
        flux_ang    float, corresponding flux in erg/s/cm2/Ang

        '''

        ##we convert the magniude (or array of magnitude). This gives a flux in 
        ## erg/s/cm2/Hz
        flux_hz = 10**((mag+48.6)/(-2.5))

        ## so we retrieve the speed of light and convert it to Ang/s
        c = units.length().m_to_ang(units.Phys_const().speed_of_light_ms())

        ## and then convert it into erg/s/cm2/ang
        flux_Ang = (c / Leff**2) * flux_hz 

        return flux_Ang