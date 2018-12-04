'''
############################
#####
##### The Spartan SIM Project
#####      R. THOMAS
#####        2017
#####
#####   Atmospehrical module
#####
###########################
@License: GNU Public licence V3
'''

##### Python standard
import os
from pathlib import Path
import random
import pickle

#python third party
import numpy

##### local
from . import messages as MTU
from . import Spectroscopy


def required_atmosphere(conf, DataT):
    '''
    This function looks into the data configuration and defines if atmospherical are required
    Parameters:
    -----------
    conf
            obj, configuration from user conf file
    DataT
            str, data type to be simulated

    Returns:
    --------
    AMrange 
            list, of AM range required for the current simulated object
    '''

    AMrange = []
    if DataT in ['Combined', 'Photo']:
        for i in conf.PHOT['Band_list']:
            ##look at all the bands and get the airmass range
            am = conf.PHOT['Band_list'][i][-2]
            ##if we do not have it in the AMrange list we add it
            if am not in AMrange:
                AMrange.append(am)

    if DataT in ['Combined', 'Spectro']:
        for i in conf.SPEC['types']:
            ###look at all spectra and get airmass range
            am = conf.SPEC['types'][i]['Atm']
            ##if we do not have it in the AMrange list we add it
            if am not in AMrange:
                AMrange.append(am)

    return AMrange

class sky(object):

    def __init__(self, conf):
        '''
        This function defines the airmass depending on the airmass range defined by the user
        Based on that airmass, it will select telluric absorption and skyline emission spectra

        Parameters:
        -----------
        conf
            obj, configuration from user conf file
        '''
        self.home = str(Path.home())
        fileconf = os.path.join(self.home, '.sedobs/','sedobs_conf')
        self.inputdir = numpy.genfromtxt(fileconf, dtype='str')[1] 
        self.conf = conf 
        self.rangesAM = {}
        self.rangesAM['low'] = [1., 1.05, 1.1, 1.15]
        self.rangesAM['int'] = [1.2, 1.2, 1.3, 1.3, 1.4]
        high = list(range(15, 20, 1)) + list(range(20, 31, 2))
        self.rangesAM['high'] = [i/10 for i in high]

    def get_sky(self, Amrange):
        '''
        This method get the telluric absorption and OH spectra for the required
        airmass ranges

        Parameters:
        -----------
        Amrange    
            list, of AM range required for the current simulated object

        Return
        ------
        None

        New Attribute
        --------------
        sky
            dict, for each airmass range we select randomly the airmass and assign OHspectrum
                    and absorption curve to it
        '''

        ###prepare for resolution change
        Spectro = Spectroscopy.Spectroscopy()
        Rsky = [[11500, 10., 100000.]]

        self.sky = {}
        for i in Amrange:
            self.sky[i] = {}
            if i == 'none':
                self.sky[i]['AM'] = -99.9
            else:
                #select the randomely the AM
                AMsim = random.choice(self.rangesAM[i])
                self.sky[i]['AM'] = AMsim
                MTU.Info('AM=%s for %s airmass range'%(AMsim, i), 'No')
                ###retrieve right curves
                ##get tell absorption
                #alltell = pickle.load(open(os.path.join(self.inputdir, 'Atmos', \
                #        'telluric_abs.pickle'), 'rb'))
                #get right index 
                #indextell = numpy.where(numpy.array(alltell['AM']) == AMsim)[0]
                ###get the right curve
                #self.sky[i]['tell'] = [alltell['wave'], alltell['array'][indextell][0]]

                ##same for skylines
                allOH = pickle.load(open(os.path.join(self.inputdir, 'Atmos', \
                        'skylines_em.pickle'), 'rb')) 
                ##get right index
                indexOH = numpy.where(numpy.array(allOH['AM']) == AMsim)[0]

                ###change resolution
                resolution = Spectro.model_res(self.conf.Template['BaseSSP'])[0][0]
                spec_conf = {'l0':min(allOH['wave']), 'lf':max(allOH['wave']), 'res':resolution}
                smoothed_sky = numpy.array(Spectro.change_resolution(allOH['array'][indexOH[0]], \
                        allOH['wave'], 0, Rsky, spec_conf))

                ##get right curve
                self.sky[i]['OH'] = [allOH['wave'], \
                        self.conf.General['sizegal'] * smoothed_sky]
