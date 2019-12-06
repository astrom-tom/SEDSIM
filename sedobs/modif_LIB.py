'''
The SPARTAN project
-------------------
Module dealing with library ingredients during the fit

@author: R. THOMAS
@year  : 2016 
@Place : UV/LAM/UCBJ
@License: CeCILL-v2 licence - see LICENCE.txt
'''

####Python General Libraries
import os
import time
from pathlib import Path


####Third party
import numpy
import h5py
from   scipy import interpolate
import scipy

####Local modules
from . import messages as MTU
from . import units
from . import Check_plots
#---------------------------------------------------------------------

class DUSTlib:
    '''
    Dust Preparation for the fit
    '''
    def __init__(self):
        '''
        class creation, define the input file directory
        '''
        self.home = str(Path.home())
        fileconf = os.path.join(self.home, '.sedobs/','sedobs_conf')
        self.inputdir = numpy.genfromtxt(fileconf, dtype='str')[1]
        self.hide_dir = os.path.join(self.home,'.sedobs/')

    def Dust_for_fit(self, Dustfile, wave_models, AvList, RvList):
        '''
        Method that prepares the final extinction curve to be used
        during the fit
        Parameter
        ---------
        Dustfile    str, /path/to/extinction curve file
        wave_model  1D array, wavelength of the templates
        AvLisrt     list of str, list of Av values given by the user
        RvLisrt     list of str, list of Rv values given by the user

        Return
        ------
        Dust_for_fit 2D array, with wavelength in the first clumn and 
                               extinction coefficient in the second
        '''
        DUSTdict = {}
        if Dustfile == 'none' or Dustfile == '':
            DUSTdict['Use'] = 'No'
        else:
            dustfile = os.path.join(self.inputdir, 'EXT', Dustfile)
            ##1- We extract the extinction curve
            WaveDust, CoefDust = numpy.loadtxt(dustfile).T
            ##2- Then we regrid to the model 
            DUSTdict['Use'] = 'Yes'
            DUSTdict['Coef'] = numpy.interp(wave_models, WaveDust, CoefDust)
            DUSTdict['Av'] = AvList
            DUSTdict['Rv'] = RvList

        return DUSTdict

    def Dust_ext(self, Av, Rv, Coef):
        '''
        Method that compute the coefficient from the extinction anf the EBV value
        Parameter
        ---------
        Av     float, Av value given by the user
        Rv     float, Rv value given by the user
        Coef    1D array, extinction coefficient regridded to the wave model grid (restframe)

        Return
        ------
        Dust_trans  1Darray, of the dust transmission computed as 10**(-0.4*E(B-V)*k(lambda))
                    See http://webast.ast.obs-mip.fr/hyperz/hyperz_manual1/node10.html for detail
        '''
        Dust_trans = 10**(-0.4*Av*Coef/Rv)

        return Dust_trans

    def Make_dusted_library(self, Templates, Dustdict, Parameters, Names, Wave_final):
        '''
        This method combine the free dust library and the dust prescription
        selected by the user to create a 'Dusted' library that contains the 
        Dust.
        Parameter
        ---------
        Template    2D array, with all the dust-free templates
        Dustdict    dict, with dust information
        Parameters  2D array, with the parameters corresponding to the Templates
        Names       list, of parameter names

        Return
        ------
        New_template_dust   NDarray, with all the template with extinction
        New_parameter_dust  NDarray, with all the parameters (original+Dust)
        '''
        if Dustdict['Use'] == 'No':
            #if the user does not want to use dust
            #we return the sames arrays as the input ones 
            return Templates, Parameters, Names

        elif Dustdict['Use'] == 'Yes':
            #Number of dust value 
            NDust = len(Dustdict['Av'])* len(Dustdict['Rv'])
            ##create the new array for the dusted library
            ## 1- for the template, we will have Ntemplate * Ndust, but same wavelength
            New_template_dust = numpy.empty((Templates.shape[0]*NDust, Templates.shape[1]))
            ## 2- for the parameters, we will have Ntemplate * Ndust of parameters sets
            ##    and NParameter + 2 parameters (Rv and Av)
            New_parameter_dust = numpy.empty((Parameters.shape[0]*NDust, Parameters.shape[1]+2))
            ## 3- and we add 'EBV' to the parameter names
            Names.append('EBV')
            N = 1
            for av in Dustdict['Av']:
                for rv in Dustdict['Rv']:
                #Create the transmission at the ebv value
                    MTU.Info('Add dust Av=%s and Rv=%s to the library [E(b-v)=%1.2f]'%(av, \
                            rv, float(av)/float(rv)), 'No')
                    Dust_trans = self.Dust_ext(float(av), float(rv), Dustdict['Coef'])
                    #print(len(New_Parameter_dust.T[(N-1)*len():][7])) 
                    #populate the dusted template array with the dusted templates
                    New_template_dust[(N-1)*len(Templates):N*len(Templates)] = Templates * Dust_trans
                    ##and the new parameter library first we add the dust value
                    New_parameter_dust[(N-1)*len(Templates):N*len(Templates),-1] = float(rv)
                    New_parameter_dust[(N-1)*len(Templates):N*len(Templates),-2] = float(av)
                    ##and the original parameters
                    New_parameter_dust[(N-1)*len(Templates):N*len(Templates),0:-2] = Parameters
                    N += 1
                 
            ##if plot:
            #plot.Dust_from_lib(Wave_final, New_template_dust, Dustdict, len(Templates))
            return New_template_dust, New_parameter_dust, Names
   
   

class IGMlib:
    '''
    Class preparing the IGM for the fit
    '''
    def __init__(self):
        '''
        class creation, define the input file directory
        '''
        self.home = str(Path.home())
        fileconf = os.path.join(self.home, '.sedobs/','sedobs_conf')
        self.inputdir = numpy.genfromtxt(fileconf, dtype='str')[1]
        self.hide_dir = os.path.join(self.home,'.sedobs/')

    def IGM_for_fit(self, IGMfile, Redshift, Wave_final, typeIGM):
        '''
        Method that make gives out the IGM dictionnary for the fit
        Parameter
        ---------
        IGMfile,    str, /path/and/name to the IGMfile to be used
        redshift    float, redshift of the object
        wave_model  1D array, restframe wavelength of the models
        typeIGM     str, 'free' or 'mean' type of IGM to be used 

        Return
        ------
        IGM_dict    dict, information about the IGM to use during the fit
        '''
       	IGM_dict = {}
        if IGMfile == 'none' or IGMfile == '' or typeIGM == '' or Redshift<1.5:
            IGM_dict['Use'] = 'No'
            IGM_dict['Curves'] = []

        else:
            IGM_dict['Use'] = 'Yes'
            igmfile = os.path.join(self.inputdir, 'IGM', IGMfile)
            IGM_dict['Curves'] = self.take_curve(igmfile, Redshift, Wave_final, typeIGM) 

        return IGM_dict

    def take_curve(self, IGMfile, redshift, wave_model, typeIGM):
        '''
        Method that prepares the IGM for the fit. It selects
        the right curve(s) and regrid them to the wavelength grid of the models
        Parameter
        ---------
        IGMfile     str, /path/and/name to the IGMfile to be used
        redshift    float, redshift of the object
        wave_model  1D array, restframe wavelength of the models
        typeIGM     str, 'free' or 'mean' type of IGM to be used 

        Return
        ------
        To_Use      list, of each curve interpolated to the wave_model grid
        '''
        To_Use = []
        ###here we round the redshift to 4 digits
        ###the IGM templates are not more details (and it 
        ###is probably useless to give more than 4 digits)
        redshift = round(redshift,4)
        ## Open the IGMfile
        with h5py.File(IGMfile, 'r') as IGM:
            Curves = numpy.array(IGM['%s/Curve'%str(redshift)])
            Wave = numpy.array(IGM['Wavelength/Wave'])
            Tr = numpy.array(IGM['%s/Transmissions'%str(redshift)])

        if typeIGM == 'free':
            ##if the user uses the free prescription
            ## we have 7 curves
            for i in range(len(Curves)):
                ##we interpolate each curve to the model grid
                ##and add it to To_Use with the transmissions (alpha beta and gamma)
                To_Use.append((numpy.interp(wave_model, Wave, Curves[i]), Tr[i]))
        
        if typeIGM == 'mean':
            ##if the user uses the mean prescription we need to extract the 
            ##mean curve
            ##we interpolate the curve to the model grid
            ##and add it to To_Use with the transmissions
            To_Use.append((numpy.interp(wave_model, Wave, Curves[3]), Tr[3]))
            #print(Tr)
            #print(Trm)
            #print(Trp)

        ###check plot:
        #Check_plots.plot().IGM_curves(To_Use, wave_model, Curves, Wave, redshift)

        return To_Use 

    def Make_IGM_library(self, Wave_rf, Templates_dust, \
            Parameters_dust, ParamNames,Redshift, IGM_dict):
        '''
        Methods that applies the IGM to the library
        Parameter
        ---------
        
        Return
        ------
        '''
        if IGM_dict['Use'] == 'Yes':
            MTU.Info('Applying IGM...', 'No')
            Nigm = len(IGM_dict['Curves'])
            #print(Nigm)
            ##create the new array for the IGM-dusted library
            ## 1- for the template, we will have Ntemplate * Ndust, but same wavelength
            New_template_IGM = numpy.empty((Templates_dust.shape[0]*Nigm, Templates_dust.shape[1]))
            ## 2- for the parameters, we will have Ntemplate * Nigm of parameters sets
            ##    and NParameter + 1 parameters
            New_parameter_IGM = numpy.empty((Parameters_dust.shape[0]*Nigm, Parameters_dust.shape[1]+3))
            ## 3- and we add the transmissions to the parameter names
            ParamIGMnames = []
            for i in ParamNames:
                ParamIGMnames.append(i)

            ParamIGMnames.append('LyaTr')
            ParamIGMnames.append('LybTr')
            ParamIGMnames.append('LygTr')
           
            #print(New_parameter_IGM.shape, Parameters_dust.shape, ParamIGMnames)
            N = 1
            for Igm in IGM_dict['Curves']:
                curve = Igm[0]
                Trans = Igm[1]
                #populate the IGM template array with the IGM templates
                New_template_IGM[(N-1)*len(Templates_dust):N*len(Templates_dust)] = Templates_dust * curve
                ##and the new parameter library first we add the dust value
                New_parameter_IGM[(N-1)*len(Templates_dust):N*len(Templates_dust),-3:] = Trans
                ##and the original parameters
                New_parameter_IGM[(N-1)*len(Templates_dust):N*len(Templates_dust),0:-3] = Parameters_dust
                N += 1
           
            return New_template_IGM, New_parameter_IGM, ParamIGMnames, 'yes'
            ##if plot:
            #plot.Dust_from_lib(Wave_final, New_template_dust, Dustdict, len(Templates))
            #return New_template_IGM, New_parameter_IGM, ParamNames 
        else:
            MTU.Info('No IGM applied (not selected by user or z<1.5)', 'No')
            return Templates_dust, Parameters_dust, ParamNames, 'no'
            

class Emlineslib:
    '''
    This module deals with the emission line addition to the template
    during the fit
    '''

    def __init__(self):
        '''
        Class initialization, retrieve input files for emission line
        treatment
        '''

        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.Ratios = os.path.join(current_dir, 'emlines/Anders_Fritze_2003.dat')
        self.Neb_cont = os.path.join(current_dir, 'emlines/Emission_coef.txt')

    def main(self, Templates_final, Wave_final, Parameter_array, Names, CONF, toskip):
        '''
        This method is the main function that adds the emission lines
        Parameter:
        ---------
        Templates_final , Nd array of template flux
        Wave_final      , 1d array of template wavelength
        Parameter_array , Nd array of template parameters (needed for metallicity)
        Names           , Nd array of parameter name
        CONF            , dict of configuration
        toskip          , list of line to skip
        Return:
        -------
        Template_emline  ,Nd array of template flux with emission line (or original if
                          emission line are not applied)
        '''

        #print(CONF.LIB['EMline'])

        if CONF.Template['EMline'].lower() == 'yes':
            ##initialize ionization edges
            wedge = self.init_edges()

            ##compute number of lyman continnuum photons
            LCP = self.NLym_cont_photons(wedge, Wave_final, Templates_final)
            #############################################
       
            ## Compute the nebular continuum Nebular continuum
            fgas = 1.0
            Nebular_cont = self.Nebular_continuum(LCP,fgas, Wave_final, len(Templates_final))
            ##############################################

            ###localize metallicity index
            for i in range(len(Names)):
                if Names[i]=='MET':
                    index = i
            #and create the metallicity array
            Metlist = numpy.zeros(len(Templates_final))
            Met = Parameter_array.T[index]
            for i in range(len(Metlist)):
                Metlist[i] = Met[i]
            ################################

            ###equivalent width and line flux computation
            EW, lumi, Name, lambdal, pos_line, l_line = self.EW_calcul(LCP, \
                    fgas, Metlist, Wave_final, Templates_final, Nebular_cont, toskip)

            ###and create the lines on the flux

#-->old one #flux_emLINE = self.Em_line_on_template1(l_line, pos_line, Templates_final, \
            #        Nebular_cont, Wave_final, Metlist)

            flux_emLINE2 = self.Em_line_on_template2(l_line, pos_line, Templates_final, \
                    Nebular_cont, Wave_final, Metlist)

            #####################################
            ###check with plots
            #X = 10
            #print(Parameter_array[X])
            #plot().EmLinecheck(Wave_final, Templates_final[X], Nebular_cont[X], flux_emLINE[X])
            #print(Templates_final.shape, flux_emLINE.shape)
            return flux_emLINE2

        else:
            return Templates_final
    
   

    def Em_line_on_template2(self, l_line, pos_line, flux, cont, wave, Metlist):
        '''
        This methods creates the emission line on the 
        template
        The line flux is added to the closest wavelength in
        the grid.

        Parameter
        ---------
        l_line      array, luminosity of each line
        pos_line    array, position of each line
        flux        array, flux of the templates
        cont        array, nebular continnuum 
        wave        array, wavelength grid

        Return
        ------
        '''

        i = 1

        flux_dirac = numpy.zeros( (len(flux), len(wave)))

        ###loop over spectrums and group lines which may be at adjacent positions.
        #We need to make sure that the continuum flux is maintained before and after the position
        #where the line is added! Otherwise several lines falling at neighbouring positions
        #will artificially create a broad (hence too strong) line. 

        
        Metunique = numpy.unique(Metlist)
        l_line2 = numpy.copy(l_line)
        pos_line2 = numpy.copy(pos_line)
        cont2 = numpy.copy(cont)
        flux2 = numpy.copy(flux)

        flux_dirac_arrays = []

        for k in Metunique:
            met_template = numpy.where(Metlist == k)[0]
            l_linemet = l_line2[met_template]
            pos_linemet = pos_line2[met_template]
            fluxmet = flux2[met_template]
            contmet = cont2[met_template]
            flux_dirac_met = numpy.zeros(l_linemet.shape)

            posi = numpy.where(pos_linemet[1] == 1)

            for j in range(len(pos_linemet[1])):
                if pos_linemet[1][j] == 1:

                    if pos_linemet[1][j-1] == 1:
                        l_linemet.T[j] = l_linemet.T[j] + l_linemet.T[j-1]
                        pos_linemet[1][j-1] = 0

                    if pos_linemet[1][j+1] == 1:
                        l_linemet.T[j] = l_linemet.T[j] + l_linemet.T[j-1]
                        pos_linemet[1][j-1] = 0
     
                    width = 0.5*abs(wave[j+1]-wave[j]) + 0.5*abs(wave[j]-wave[j-1])
                    fl_line = l_linemet.T[j] / width
                    
                    flux_dirac_met.T[j] = fluxmet.T[j]   + fl_line + contmet.T[j]

                else:

                    flux_dirac_met.T[j] = fluxmet.T[j] + contmet.T[j]
            flux_dirac_arrays.append(flux_dirac_met)

        fast = [ i for i in flux_dirac_arrays]
        F = numpy.concatenate(fast)
        return F
    
    def Em_line_on_template1(self, l_line, pos_line, flux, cont, wave, Metlist):

        '''
        This methods creates the emission line on the 
        template
        The line flux is added to the closest wavelength in
        the grid.

        Parameter
        ---------
        l_line      array, luminosity of each line
        pos_line    array, position of each line
        flux        array, flux of the templates
        cont        array, nebular continnuum 
        wave        array, wavelength grid

        Return
        ------
        '''


        flux_dirac = numpy.zeros( (len(flux), len(wave)))

        ###loop over spectrums and group lines which may be at adjacent positions.
        #We need to make sure that the continuum flux is maintained before and after the position
        #where the line is added! Otherwise several lines falling at neighbouring positions
        #will artificially create a broad (hence too strong) line. 

 

        t = time.time()
        for i in range(len(flux_dirac)):
            j = 1
            while j<len(wave)-1: 
                #if j!=0 and j!=len(wave):
                if pos_line[i][j] == 1:

                    if pos_line[i][j-1] == 1:
                        l_line[i][j] = l_line[i][j] + l_line[i][j-1]
                        pos_line[i][j-1] = 0

                    if pos_line[i][j+1] == 1:
                        l_line[i][j] = l_line[i][j] + l_line[i][j+1]
                        pos_line[i][j+1] = 0

                    width = 0.5*abs(wave[j+1]-wave[j]) + 0.5*abs(wave[j]  -wave[j-1])
                    fl_line = l_line[i][j] / width 
                    flux_dirac[i][j] = flux[i][j]   + fl_line + cont[i][j]

                else:

                    flux_dirac[i][j] = flux[i][j]+cont[i][j]

                j+=1



        return flux_dirac

    def init_edges(self):
        '''
        Initialises ionisation edges

        Parameters:
        ----------
        NONE

        Returns:
        -------
        wedge   array, wavelength list with ionisation edge in Ang
        '''
        wedge = 1.e+8 / 109678.758e+0  #H edge in Angstroem   =911.75AA 
                                          #    ground state (B-X)  
        return wedge 


    def NLym_cont_photons(self, wedge, wave, flux):
        '''
        Calculate the number of continuum photons shortward of ionising edges.

        Parameters:
        ----------
        wave    array, of wave from the SED in angstrom 
        flux    array, of flux from the SED in erg.s-1.A-1
        wedge   array, containing wavelength of edges [A]

        Returns:
        -------
        qi   array, array containing nedge ionising fluxes 
                         [#photons s^-1]
        '''

        ###
        qi = 0

        ###
        qsum  = numpy.zeros(len(flux))
        i     = 1  #2
 
        ### Planck cst in erg.s
        h = units.Phys_const().Planck_cst()  
        ##light speed in ang/s
        c = units.length().m_to_ang(units.Phys_const().speed_of_light_ms())

        while wave[i] <= wedge:
            ###trapz integration
            qsum = qsum + (flux.T[i]+flux.T[i-1])*0.5*(wave[i]-wave[i-1])*wave[i]/(h*c)
            qi=qsum
            i+=1
       
        return qi

    def Nebular_continuum(self, q0, fgas, wave, Ntemp):
        '''
        Calculates the nebular continuous emission

        Assumes electron temperature Te=10000 K, n(HeII)/n(HI) = 0.1
        and n(HeIII)/n(HI) = 0.

        Parameters:
        ----------
        q0:    number of Lyman continuum photons per second
        fgas:  fraction of Lyman cont.photons which is absorbed by gaz
              (rest assumed to be lost)
        wsed:  wavelength grid to calculate nebular emission [A]

        Returns:
        -------
        flux_neb: nebular flux in [ergs s^-1 A^-1] 
                    (on wavelength grid given by wave)
        '''

        ###CSt
        alpha_2 = 2.575e-13 # [cm^3 s^-1] total recombination coeff. for hydrogen for Te=10000 K 
                            # (except to groundstate)
        xn_hep  = 0.1       # n(HeII)/n(HI
       
        ##extract emission coefficient from file
        ga_h, ga_2q, ga_hei, wave_emc = numpy.loadtxt(self.Neb_cont).T
        new_wave_emc = wave

        ##interpolation ovewr the SED's wave grid 
        ga_h_interp = numpy.interp(new_wave_emc,wave_emc,ga_h)
        ga_2q_interp = numpy.interp(new_wave_emc, wave_emc, ga_2q) 
        ga_hei_interp = numpy.interp(new_wave_emc, wave_emc, ga_hei)
       
        ##Cst
        c = units.length().m_to_ang(units.Phys_const().speed_of_light_ms())
        ### the emission line coef are in 1e-40 erg.cm^3.s^-1.Hz^-1
        Factor = c*1e-40

        ##compute emission
        flux_nebular = []
        for i in range(len(wave)):
            a = numpy.where(new_wave_emc==wave[i]) 
            add_h = ga_h_interp[a]
            add_2q = ga_2q_interp[a]
            add_hei = ga_hei_interp[a]
            ga_tot = (add_h + add_2q + xn_hep * add_hei)
            ## all the coefficient are in 1e-40 erg/cm3/s/Hz,to put it back
            ## in erg/s/cm2/AA we use lFl=vFv --> Fl = c/l^2 * Fv 
            ## with c=2.9979 e18 AA/s
            fluxneb_i  = Factor*ga_tot/alpha_2/(wave[i]*wave[i])
            fluxneb_i  = fluxneb_i[0] * fgas  # *q0 but this is done below  
                                              ###this is in erg/cm2/s/A (q0 in cm-2.s-1)
            flux_nebular.append(fluxneb_i)

        ###multiply by q0[i] and save it
        Neb_cont_lib = numpy.zeros((Ntemp,len(wave)))
        '''
        t = time.time()
        for i in range(len(Neb_cont_lib)):
            for j in range(len(Neb_cont_lib.T)):
                Neb_cont_lib[i][j] = flux_nebular[j]*q0[i]
        '''
        ##above was the first version (two nested loops), replaced later by list comprehension (30% faster)
        Neb_cont_lib = numpy.array([[flux_nebular[j]*q0[i] for j in range(len(Neb_cont_lib.T))] for i in range(len(Neb_cont_lib)) ])

        return Neb_cont_lib


    def skipline(self, toskip):


        Name, lambdal, Z1, Z2, Z35 = numpy.genfromtxt(self.Ratios, dtype='str').T
        lambdal = lambdal.astype('float')
        Z1 = Z1.astype('float')
        Z2 = Z2.astype('float')
        Z35 = Z35.astype('float')

        Nameskip = []
        lambdalskip = []
        Z1skip = []
        Z2skip = []
        Z35skip = []

        for i in range(len(Name)):
            if Name[i] not in toskip:
                Nameskip.append(Name[i])
                lambdalskip.append(lambdal[i])
                Z1skip.append(Z1[i])
                Z2skip.append(Z2[i])
                Z35skip.append(Z35[i])

        return Nameskip, lambdalskip, Z1skip, Z2skip, Z35skip


    def EW_calcul(self, q0, fgas, metal, wave, flux, cont, toskip):
        '''
        Calculates the line luminosity and equivalent widths of nebular lines 
        and adds the corresponding flux to the spectrum at the 
        appropriate position.
        Note: to preserve correctly the total line flux this routine
              assumes that the trapezium rule is used when computing 
              the flux in different filters (see filter routine). 

        Parameter
        ---------
        q0:     float, number of Lyman continuum photons per second
        fgas:   float, fraction of Lyman cont.photons which is absorbed by gas (rest assumed to be lost)
        metal:  float, metallicity [in solar units] used to select different empirical line ratios
        wave:   array, wavelength grid of continuum 
        flux:   array, original continuum flux grid
        cont    array, nebular continuum 
        toskip  list, of line to skip
        Output:
        ------
        flux: at output the line flux is added to 'flux'
        ew_line: array with EW's
        f_line: array with line fluxes
        '''

        ###H_beta luminosity assuming Case B, Te=10000-K
        l_ref = 4.77e-13*q0*fgas
        
        #####extract line ratios
            ###first we check if some line have to be skept
        Name, lambdal, Z1, Z2, Z35 = self.skipline(toskip)
        ratio = [Z1, Z2, Z35]
       
        ###metal stuff
        metal_array = [0.02, 0.2, 0.4]
        #             1/50, 1/5, >1/2.5  in Zsolar units --> 1=Zsun     

        ##we check the values of the template and replace for high values
        metal_emLine = numpy.zeros(len(metal))
        for i in range(len(metal)):
            if metal[i] >= 0.4:
                metal_emLine[i] = 0.4
            else:
                metal_emLine[i] = metal[i]

        ##luminosity and EW array
        EW = numpy.zeros((len(metal), len(Name) ))
        lumi = numpy.zeros((len(metal), len(Name) ))

        ##initialize arrays
        ratio_line = numpy.zeros((len(metal), len(Name)))
        i_line = numpy.zeros((len(metal),len(wave)))
        l_line = numpy.zeros((len(metal),len(wave)))
      
        ####for Lya and Ha (see below)
        WWL = [1190.0, 1240.0]
        AA =    interpolate.interp1d(wave, flux+cont)(WWL)
        WWH = [6510.0, 6610.0]
        BB =    interpolate.interp1d(wave, flux+cont)(WWH)

        ###find position of lines
        pos = list(numpy.zeros(len(wave)))
        name_index_wave = []
        for j in range(len(Name)):
            rec_wave = lambdal[j] 
            ##find the place in the SED-s wavelength grid
            index_wave = self.find_pos(rec_wave, wave)
            name_index_wave.append(index_wave)
            ##save the index in the position
            pos[index_wave] = Name[j]

        for i in range(len(i_line)):
            id_pos = pos
            for j in range(len(Name)):
                index_wave = name_index_wave[j]

                for k in range(len(metal_array)):
                    if metal_array[k] == metal_emLine[i]:
                        ratio_line[i][j] = ratio[k][j]

                ##compute line luminosity
                l_line[i][index_wave] = l_line[i][index_wave] + l_ref[i]*ratio_line[i][j]
                ## signal a line at this position
                i_line[i][index_wave] = 1

                if Name[j] == 'H_Lya':
                    ##Special treatment --> Ly-a: absorption can be strong
                    ##need of different cont. point
                    central_cont = self.interpvalue(lambdal[j], WWL, AA[i])
                    ewi = l_line[i][index_wave] / central_cont
                    flinei = l_line[i][index_wave]

                elif Name[j] == 'H_alpha':
                    ##idem
                    central_cont = self.interpvalue(lambdal[j], WWH, BB[i])
                    ewi = l_line[i][index_wave] / central_cont 
                    flinei = l_line[i][index_wave]

                else:
                    ewi = l_line[i][index_wave] / (flux[i][index_wave]+cont[i][index_wave])
                    flinei = l_line[i][index_wave]

                ###save line flux and EW
                EW[i][j] = ewi
                lumi[i][j] = flinei

        return EW, lumi, Name, lambdal, i_line, l_line  

    def interpvalue(self, X, wave, flux):
        '''
        Find the value of flux(X)

        Parameter
        ---------
        X       float, wave where we want the value of X
        wave    array, SED's wave grid
        flux    array, flux of the SED
        '''
        new_wave = numpy.round(numpy.arange(wave[0], wave[-1]+1, 1),2)
        new_flux = numpy.interp(new_wave, wave, flux)
        a = numpy.where(new_wave==float(X))
        return new_flux[a][0]


    def find_pos(self, lambda_line, waveSED):
        '''
        This methods finds the position (index) of the line
        in the wavelength grid of the SED. It looks for the nearest 
        wavelength.

        Parameter
        ---------
        lambda_line     float, wavelength in Ang of the line
        wave            array, wavelength grid of the SED
        '''
        ##we substract the wavelength of the line to all the 
        ##wavelength of the grid and we keep the index of
        ##the smallest difference.
        index_i = (numpy.abs(waveSED-lambda_line)).argmin()

        return index_i


class COSMO_lib:
    '''
    Class that redshift the library
    '''
    def Make_cosmological_Lib(self, Cosmo_obj, template, Parameters, Param_name, COSMO_conf):
        '''
        This method makes the cosmological library, i-e, it removes the ages above
        of the age of the universe from the given redshifted library .

        Parameter
        ---------
        Cosmo_obj   dict, cosmological information at the redshift of the object
                          we are studying
        template    NDarray, of template from which we want to remove bad ages
        Parameters  NDarray, of template parameters """""
        Param_name  list   , of parameter names
        COSMO_conf  dict   , of cosmological configuration by the user
        '''
        ##first we check if we must use the cosmology
        if COSMO_conf['UseCo'].lower() == 'no':
            MTU.Info('No cosmological constraints applied', 'No')
            return template, Parameters
        else:
            ##first we find the age position in the list of parameters
            Index_age = Param_name.index('age')
            ##this gives the row of the age in the parameter array

            ##then we must find all the column where age <= AgeUniverse
            ##WARNING!!! the age in the cosmo lib is given in Gyr while
            ##           for the template it is given in yr.

            Index_good_ages = numpy.where(Parameters.T[Index_age] <= Cosmo_obj['AgeUniverse']*10**9)[0] 
            ##compute the difference for information
            Dif = len(template)-len(Index_good_ages)
            Left = len(template)-Dif
            MTU.Info('We remove %s template due to cosmological constraints'%Dif, 'No')
            MTU.Info('Left:  %s templates '%Left, 'No')         
            ##then select the right template
            Cosmo_templates = template[Index_good_ages]
            ##and the right paramters
            Cosmo_param = Parameters[Index_good_ages]

            return Cosmo_templates, Cosmo_param


    def prepare_lib_at_z(self, Template_Lib, Waves, Redshift, COSMO):
        '''
        Take the Library with dust and put it at the right redshift
        
        Parameter
        ---------
        Template_Lib        NDarray, with all the template to redshift
        Waves               List, of restframe wavelength for the templates
        redshift            float, redshift of the observation
	COSMO               dict, COSMO properties at the redshift
        
        Return
        ------
        Wave_at_z       1Darray, redshifted wavelength
        Templates_at_z  NDarray, of redshifted flux
        '''
        ### first we redshift the waves 
        Wave_at_z = Waves*(1+Redshift)

        ## then we must redshift the fluxes. 
        ## WARNING: The models are in Lsolar.A^-1 therefore
        ## we must put them back in erg/s/AA (multiply by solar_lumino_erg_s)
        ## and Then we apply F(z [erg/s/cm2/AA]) = F(z=0, erg/s/AA) / (4 * pi * Dl^2 * (1+z)) 
        A = units.Phys_const().solar_lumino_erg_s() / \
                (4*scipy.constants.pi*(COSMO['DL']**2)*(1+Redshift))
        Templates_at_z = Template_Lib * A

        return Wave_at_z, Templates_at_z
