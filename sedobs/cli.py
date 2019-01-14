'''

The SEDSIM Project 
-------------------
File: cli.py

This file configures the Command line interface 

@author: R. THOMAS
@year: 2018
@place:  ESO
@License: GPL v3.0 - see LICENCE.txt
'''

#### Python Libraries
import argparse

class CLI:
    """
    This Class defines the arguments to be calle to use SPARTAN
    For the help, you can use 'SPARTAN -h' or 'SPARTAN --help'
    """
    def __init__(self,):
        """
        Class constructor, defines the attributes of the class
        and run the argument section
        """
        self.args()

    def args(self,):
        """
        This function creates defines the 7 main arguments of SPARTAN using the argparse module
        """
        parser = argparse.ArgumentParser(description="SEDobs, R. Thomas, 2018-2019, \
                This program comes with ABSOLUTELY NO WARRANTY; and is distributed under \
                the GPLv3.0 Licence terms.See the version of this Licence distributed along \
                this code for details.\n website: \n \
                https://astrom-tom.github.io/SEDSIM/build/html/index.html")

        parser.add_argument("-p", "--project", help="Input configuration file")
        parser.add_argument("--test", action="store_true", \
                help="If you wanna try the test run of SEDobs")
        parser.add_argument("--docs", action="store_true", help="open the doc in web browser")
        parser.add_argument("--version", action="store_true", help="display current version of SEDSIM")

        ##### GET the Arguments for SPARTAN startup
        self.arguments = parser.parse_args()


