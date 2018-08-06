#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
############################
#####
#####       SEDObs
#####      R. THOMAS
#####        2018
#####     entry-point
###########################
@License: GPL - see LICENCE.txt
'''

###import libraries
import sys
import os
from subprocess import call
import socket


###Local modules
from . import cli
from . import __info__ as info
from . import config
from . import messages as MTU
from . import cosmo
from . import simu
from . import library

def main():
    '''
    This is the main function of the code.
    if loads the command line interface and depending
    on the options specified by the user, start the 
    main window.
    It does not take any argument nor return anything
    '''
    ###load the command line interface
    args = cli.CLI().arguments

    if args.docs == False and args.version == False and args.project == None:
        MTU.Info('\tNothing was asked...quit...', 'No')
        sys.exit()

    ###if the user wants to display the version
    if args.version == True:
        MTU.Info('\tSEDobs version %s'%info.__version__, 'No')
        sys.exit()

    ###if the user wants to display the internal documentation
    if args.docs == True:
        
        ##check if there is any internet connection
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            url = info.__website__
        ##if not we use the local documentation distributed along the software
        except: 
            MTU.Info('No internet connection detected, open local documentation', 'No')
            dir_path = os.path.dirname(os.path.realpath(__file__))
            url = os.path.join(dir_path, 'docs/build/html/index.html')

        for i in ['falkon', 'firefox', 'open', 'qupzilla', 'chromium', 'google-chrome']:
            ##we check if the command exist in the system
            exist = call(['which', i])
            if exist == 0:
                ##if it does then we use it to load the documentation
                call([i, url])
                ##and we stop the loop
                sys.exit()
                break

    if args.project != None:
        print('----------------------------------------------------------')
        MTU.Info('LOAD: %s\n'%args.project, 'No')
        full_conf = config.read_config(args.project)
        final = config.check_prepare(full_conf)
        print('----------------------------------------------------------')

        ###### Prepare the distribution of z, StN, mag
        if final.config.General['gen_array'] == 'no':
            MTU.Info('Prepare distributions (stn, mag, z) for the %s objects'\
                %(final.config.General['N_obj']),'Yes') 
            redshift, StN, mag = config.prepare_dis().indiv_dist(final.config)
        else:
            MTU.Info('Extract full array', 'Yes')
            redshift, StN, mag = config.prepare_dis().full_array(final_config)
            MTU.Info('SPARTAN SIM will simulate %s objects'%len(mag), 'No')

        ###Prepare Cosmological module
        MTU.Info('Prepare comology module', 'Yes')
        COSMOS = cosmo.Cosmology(final.config.COSMO['Ho'], \
               final.config.COSMO['Omega_m'], \
               final.config.COSMO['Omega_L'])

        ### Prepare library
        Name_LIB = os.path.join(final.config.General['PDir'],\
                        final.config.General['PName']+'.hdf5')
        final.config.General['Name_LIB'] = Name_LIB
        ###check if the library was already created
        if os.path.isfile(Name_LIB):
            wave, template, parameters, param_names = library.from_Lib(final.config).main()
            MTU.Info('Library loaded from file : %s'%Name_LIB, 'Yes')
        else:
            ##if not we remake it
            wave, template, parameters, param_names = library.from_SSP().main(final.config)
            MTU.Info('Library created : %s'%Name_LIB, 'Yes')

        start = input('Start Simulation? [Press enter for Yes]')
        if start == '':
            #start simulating
            SIM = simu.Main(final.config)
            SIM.main(redshift, StN, mag, wave, template, parameters, param_names, COSMOS)

