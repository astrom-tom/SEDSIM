#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
############################
#####
#####       SEDSIM
#####      R. THOMAS
#####        2018
#####
###########################
@License: GPL - see LICENCE.txt
'''

###import libraries
import sys
import os
from subprocess import call

##third parties
import socket

###Local modules
import cli
import __info__ as info
import config
import messages as MTU

def main():
    '''
    This is the main function of the code.
    if loads the command line interface and depending
    on the options specified by the user, start the 
    main window.
    '''
    ###load the command line interface
    args = cli.CLI().arguments

    ###if the user wants to display the version
    if args.version == True:
        MTU.Info('SEDSIM version %s'%info.__version__, 'No')
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
            dir_path = os.path.dirname(os.path.realpath(__file__))
            url = os.path.join(dir_path, '../docs/build/html/index.html')

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
        print('\nLOAD: %s\n'%args.project)
        full_conf = config.read_config(args.project)
        final = config.check_prepare(full_conf)

if __name__ == "__main__":
    main()
