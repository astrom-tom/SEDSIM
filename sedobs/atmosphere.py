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

#python third party
import numpy

##### local
from . import messages as MTU
from . import Photometry
from . import Spectroscopy


def required_atmosphere(conf):
    '''
    This function looks into the data configuration and defines if atmospherical are required
    Parameters:
    -----------
    conf
            obj, configuration from user conf file

    Returns:
    --------
    AMrange 
            list, of AM range required for the current simulated object
    '''

    AMrange = []
    for i in conf.PHOT['Band_list']:
        ##look at all the bands and get the airmass range
        am = conf.PHOT['Band_list'][i][-1]
        ##if we do not have it in the AMrange list we add it
        if am not in AMrange:
            AMrange.append(am)

    for i in conf.SPEC['types']:
        ###look at all spectra and get airmass range
        am = conf.SPEC['types'][i]['Atm']
        ##if we do not have it in the AMrange list we add it
        if am not in AMrange:
            AMrange.append(am)

    return AMrange

class sky:

    def __init__(self, conf, airmass_range):
        '''
        This function defines the airmass depending on the airmass range defined by the user
        Based on that airmass, it will select telluric absorption and skyline emission spectra

        Parameters:
        -----------
        conf
            obj, configuration from user conf file

        airmass_range
                        list, of airmass range required for the current simulated object

        '''
        self.home = str(Path.home())
        fileconf = os.path.join(self.home, '.sedobs/','sedobs_conf')
        self.inputdir = numpy.genfromtxt(fileconf, dtype='str')[1] 
        self.conf = conf 
        self.atmosphere_range = airmass_range

    def get_sky(self):
        '''
        This method get the telluric absorption and OH spectra for the required
        airmass ranges
        '''
        print(self.atmosphere_range)
