'''
The SPARTAN SIM project
-------------------
This module has been created during the 
development of SPARTAN SIM to check some 
steps with plots

@author: R. THOMAS
@year: 2017
@place: UV/LAM/UCBJ
@License: CeCILL-v2 licence - see LICENCE.txt
'''

##Python Libs
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy
from scipy.ndimage.filters import gaussian_filter
import random
plt.rcParams["font.family"] = "serif"

##SPARTAN modul
#from SIM_photo.Photometry import Photometry
#----------------------------------------------------------

class plot:
    '''
    plot maker
    '''

    def two_dist(self, dist1, bin1, legend1, dist2, bin2, legend2, xaxis):
        '''
        Module that plots 2 different distribution on top of
        eachother
        '''
        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(111)
        ##distribution 1
        aa.hist(dist1, bins=bin1, label=legend1, normed=True, color='0.6')
        ##distribution 2
        aa.hist(dist2, bins=bin2, label=legend2, normed=True, \
                histtype='step', hatch='X', color='r')

        ##properties of the subplot 
        aa.legend(fontsize=10)
        aa.set_xlabel(xaxis)
        aa.set_ylabel('N')
        aa.minorticks_on()
        #plot filter in frequency space 
        plt.show()

    def Filter_template(self,tempw, tempf, wave, flux, Leff, FWHM, Fluxmag):
        '''
        Method that plot the filter over the template region        
        '''
        w = []
        f = []
        for i in range(len(tempw)):
            if Leff - 2*FWHM < tempw[i] < Leff + 2*FWHM:
                w.append(tempw[i])
                f.append(tempf[i])
       

        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(111)
        ##plot the filter in wavelength space
        aa.scatter([Leff],[Fluxmag], marker='*', s=170, color='r')
        aa.plot(w, f, label='Template')
        aa.plot(wave, flux*max(f)/max(flux))
        aa.axvline(Leff, color='r')
        ##properties of the subplot 
        aa.legend(fontsize=5)
        aa.set_xlabel('wavelength (AA)')
        aa.set_ylabel('Transmission')
        aa.axis([Leff - 4*FWHM, Leff + 4*FWHM, min(flux*max(f)/max(flux)), max(f)])

        plt.show()





    def Filter_wave_hz(self, wave, Twave, Leff, Freq, Ffreq, Feff):
        '''
        Module that plot the filter in both spaces (wave and freq)
        '''
        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(121)
        ##plot the filter in wavelength space
        aa.plot(wave, Twave, label='wavelength space')
        aa.axvline(Leff)
        ##properties of the subplot 
        aa.legend(fontsize=5)
        aa.set_xlabel('wavelength (AA)')
        aa.set_ylabel('Transmission')

        #plot filter in frequency space 
        aa = fig.add_subplot(122)
        aa.plot(Freq, Ffreq, label='Frequency space' )
        aa.legend(fontsize = 5)
        aa.axvline(Feff)
        #properties
        aa.legend(fontsize=5)
        aa.set_xlabel('Frequency (Hz)')
        aa.set_ylabel('Transmission')

        plt.show()

    def filter_FWHM(self, Leff, wave, throughput, FWHM, HM):
        '''
        method that plot the filter (in lambda) with the FWHM
        '''
        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(111)
        ##plot the template and magnitudes
        aa.plot(wave, throughput, label='Template', color='k')
        aa.axvline(Leff)
        aa.plot([Leff-FWHM/2., Leff+FWHM/2.], [HM, HM], color='r')

        plt.show() 


    def template_and_mags(self, wave, template, photosim, Redshift):
        '''
        Module that plot a template with magnitude on top
        '''
        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(111)
        ##plot the template and magnitudes
        aa.plot(wave, template, label='Template', color='k')
        #print(photosim)
        magx = []
        magy = []
        for i in photosim:
            magy.append(photosim[i]['Flux'])
            magx.append(photosim[i]['Leff'])
        print(magy, magx)
        aa.scatter(magx, magy, label='Magnitudes', color='r')
        ##properties of the subplot 
        aa.legend(fontsize=5)
        aa.set_xlabel('wavelength (AA)')
        aa.set_ylabel('Flux density (erg/s/cm2/AA)')
        aa.set_xlim([min(magx)-500, max(magx)+500])
        aa.text((max(magx)-min(magx))/2+min(magx),\
                0.1*(max(template)-min(template))+min(template), 'z=%s'% Redshift)
        aa.axvline(4000*(1+Redshift), lw=0.1, color='b')
        aa.axvline(1215*(1+Redshift), lw=0.1, color='g')
        aa.axvline(3727*(1+Redshift), lw=0.1, color= 'r')

        plt.show() 

    def spec_sim(self, wavet, fluxt, wavec, fluxc, Redshift, specconf):

        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(111)
        ##plot the template original
        aa.plot(wavet, fluxt, label='Template', color='k', lw=2)
        aa.scatter(wavec, fluxc, label='Template cut', color='r')

        ##properties of the subplot 
        aa.legend(fontsize=5)
        aa.set_xlabel('wavelength (AA)')
        aa.set_ylabel('Flux density (erg/s/cm2/AA)')

        aa.set_xlim([min(wavec)-200, max(wavec)+200])

        #aa.text((max(magx)-min(magx))/2+min(magx),\
        #        0.1*(max(template)-min(template))+min(template), 'z=%s'% Redshift)
        aa.axvline(1215*(1+Redshift), lw=0.1, color='b')
        aa.axvline(3727*(1+Redshift), lw=0.1, color= 'r')

        plt.show() 

    def spec_noised(self, wavet, fluxt, waven, fluxn, Redshift, specconf):

        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(111)
        ##plot the template original
        aa.plot(waven, fluxn, label='Template cut', color='r', lw =2)
        aa.plot(wavet, fluxt, label='Template', color='b', lw=2)

        ##properties of the subplot 
        aa.legend(fontsize=5)
        aa.set_xlabel('wavelength (AA)')
        aa.set_ylabel('Flux density (erg/s/cm2/AA)')

        aa.set_xlim([min(waven)-200, max(waven)+200])

        #aa.text((max(magx)-min(magx))/2+min(magx),\
        #        0.1*(max(template)-min(template))+min(template), 'z=%s'% Redshift)
        aa.axvline(1215*(1+Redshift), lw=0.1, color='b')
        aa.axvline(3727*(1+Redshift), lw=0.1, color= 'r')

        plt.show() 

    def spec_template_mag(self, wavet, fluxt, spectro_sim, photo_sim, Redshift):

        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(111)
        ##plot the template original
        aa.plot(wavet, fluxt, label='Original template', color='r', lw =2, zorder=-1)
        for i in list(spectro_sim.keys()):
            aa.plot(spectro_sim[i]['wave'], spectro_sim[i]['flux'], color='k', lw=1,\
                    label='Spec %s'%i, zorder=-1)

        for i in photo_sim:
            aa.scatter(photo_sim[i]['Leff'], photo_sim[i]['Flux'], marker = 'o', \
                    s=60, label='Band %s'%i, zorder=1)
        ##properties of the subplot 

        aa.legend(fontsize=15)
        aa.set_xlabel('wavelength (AA)')
        aa.set_ylabel('Flux density (erg/s/cm2/AA)')
        aa.minorticks_on()
        aa.set_xlim([2000, 21000])

        aa.axvline(1215*(1+Redshift), lw=0.1, color='b')
        aa.axvline(3727*(1+Redshift), lw=0.1, color= 'r')

        plt.show() 


    def combined_hz(self, wavet, fluxt, spectro_sim, photo_sim, Redshift, filterfile):

        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(111)
        ##plot the template original
        ##convert it to freq
        ft, freqft = Photometry(filterfile).convert_wave_to_freq(wavet, fluxt)
        aa.plot(ft, numpy.array(freqft), label='Original template', color='b', lw =2, zorder=0)

        ##plot the spectra
        for i in list(spectro_sim.keys()):
            specf, specfluxfreq = Photometry(filterfile).convert_wave_to_freq(spectro_sim[i]['wave'], spectro_sim[i]['flux'])
            aa.plot(specf, specfluxfreq, color='k', lw=1, zorder=-1)
        
        ###fake
        aa.plot([0,0],[0,0],color='k',label='Spec')

        LM = []
        FM = []
        EM = []
        for i in photo_sim:
            freqmag, fluxfreqmag = Photometry(filterfile).convert_wave_to_freq(photo_sim[i]['Leff'], \
                    photo_sim[i]['Flux'])
            freqmag, fluxerrfreqmag = Photometry(filterfile).convert_wave_to_freq(photo_sim[i]['Leff'], \
                    photo_sim[i]['FluxErr'])

            LM.append(freqmag)
            FM.append(fluxfreqmag)
            EM.append(fluxerrfreqmag)

        aa.errorbar(LM, numpy.array(FM), yerr=[EM, EM],fmt='--o', color='r',\
                markersize='4',capsize=4, elinewidth=2, label='Phot')

        aa.legend(fontsize=15)
        aa.set_xlabel('wavelength (Hz)')
        aa.set_ylabel('Flux density (erg/s/cm2/Hz-1)')
        aa.minorticks_on()
        aa.set_xlim([min(ft), max(ft)])
        aa.set_ylim([min(freqft), max(freqft)])
        #aa.set_yscale('log')
        plt.gca().invert_xaxis()
        
        plt.show() 

    def combined_template_mag(self, wavet, fluxt, spectro_sim, photo_sim, Redshift):

        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(111)
        ##plot the template original
        aa.plot(wavet, numpy.array(fluxt), label='Original template', color='b', lw =2, zorder=0)
        colors = ['k', 'r']
        n = 0
        for i in list(spectro_sim.keys()):
            aa.plot(spectro_sim[i]['wave'], numpy.array(spectro_sim[i]['flux']), \
                    color=colors[n], lw=1, zorder=-1)
            n+=1
        
        ###fake
        aa.plot([0,0],[0,0],color='k',label='Spec')

        LM = []
        FO = []
        FM = []
        EM = []
        for i in photo_sim:
            LM.append(photo_sim[i]['Leff'])
            FM.append(photo_sim[i]['Flux'])
            FO.append(photo_sim[i]['Fluxori'])
            EM.append(photo_sim[i]['FluxErr'])

        aa.errorbar(LM, numpy.array(FM), yerr=[EM, EM],fmt='o', color='magenta', ls = 'None',\
                markersize=10,capsize=4, elinewidth=2, label='Phot', zorder=0)

        aa.scatter(LM, FO, marker='x' ,color='k', label='Original flux', s=30, zorder=1)

        aa.legend(fontsize=15)
        aa.set_xlabel('wavelength (AA)')
        aa.set_ylabel('Flux density (erg/s/cm2/AA)')
        aa.minorticks_on()
        aa.set_xlim([min(LM)-1000, max(LM)+10000])
        #aa.set_ylim([-1e-19, 2.5e-19])
        aa.axvline(1215*(1+Redshift), lw=0.1, color='b')
        aa.axvline(3727*(1+Redshift), lw=0.1, color= 'r')
        aa.set_xscale('log')
        plt.show() 


    def IGM_curves(self, TO_Use, wave_model, Curves, Wave, redshift):
        '''
        '''
        fig = plt.figure()
        ##first subplot
        aa = fig.add_subplot(111)
        ##distribution 1
        ##properties of the subplot 
        for i in TO_Use:
            aa.plot(wave_model, i[0])
        
        aa.legend(fontsize=10)
        aa.set_xlabel('$\lambda$')
        aa.set_ylabel('$F_{\lambda}$')
        aa.minorticks_on()
        #plot filter in frequency space 
        aa.set_xlim(0,2000)
        aa.axvline(1215*(1+redshift), lw = 3)
        plt.show()


