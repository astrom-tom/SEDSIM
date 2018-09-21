'''
The SEDSIM Project
-------------------
Modul dealing with the filters 

@Author R. THOMAS
@year   2017
@place  UV/LAM/UCBJ
@License: GNU public licence v3.0 - see LICENCE.txt
'''
##standard lib
import os

####Python Libraries
import h5py
import numpy
import scipy


class Retrieve_Filter_inf:
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
        self.Filterfile = filterfile

    def filter_list(self):
        """
        Function that extract the filter name list from the filter file

        Parameter
        --------
        NONE    We use self.Filterfile from the constructor


        Return
        ------
        Fillist list of filter names. A name as the following format
                ==> filter-system

        """""
        ###First we load the filter
        filters = h5py.File(self.Filterfile, 'r')
        Filterlist = []
        for i in filters:
            ## 'i' is the group
            for j in filters[i]:
                ## 'j' is an object in the group
                Filterlist.append(j)
        ##then we close the file
        filters.close()
        
        return Filterlist

    def retrieve_one_filter(self, band_name):
        '''
        Method that retrieves the filter information for
        a given filter name
        Parameter
        ---------
        band_name   str, name of the band

        Return
        ------
        to_take     list, of 2 1D-array, wavelenght then throughput
        '''
        to_take = []
        with h5py.File(self.Filterfile, 'r') as allfilt:
            for i in allfilt:
                for j in allfilt[i]:
                    if j == band_name:
                        Filter = allfilt['%s/%s'%(i, band_name)]
                        to_take.append(Filter[0])
                        to_take.append(Filter[1])
                        Leff = self.compute_Lambda_eff_Filt(Filter[0], Filter[1])
                        to_take.append(Leff)
                        FWHM = self.compute_FWHM(Filter[0], Filter[1], Leff)
                        to_take.append(FWHM)

        return to_take



    def rectangular(self, l0, lf):
        '''
        This method creates a rectangular filter between l0 and lf
        IN THE OBSERVER FRAME
        Parameter
        ---------
        l0  float, first wavelength of the filter
        lf  float, last  wavelength of the filter
        '''
        ##create the filter 
        wavelength = numpy.arange(l0-20, lf+21)                
        throughput = []
        for i in range(len(wavelength)):
            if l0 < wavelength[i] < lf:
                throughput.append(1.)
            else:
                throughput.append(0.)

        ##compute effective wavelength
        Leff = self.compute_Lambda_eff_Filt(wavelength, throughput)

        band = {}
        band['Tran'] = [wavelength, throughput, Leff]
       
        return band


    def compute_Lambda_eff_Filt(self, Lambda, throughput):
        '''
        This modules compute the effective wavelength of the filter
        Parameter
        ---------
        Lambda      1Darray, wavelengths of the filter
        thoughput   1Darray, thoughtput of the filter
       
        Return
        ------
        Leff        float, effective wavelength of the filter
        '''
        ### we follow http://www.bdnyc.org/2013/07/filter-effective-wavelengths/

        A = numpy.trapz(Lambda * throughput, Lambda)   
        B = numpy.trapz(throughput, Lambda)

        Leff = A / B
        return Leff


    def compute_FWHM(self, Lambda, throughput, Leff):
        '''
        This method find the full width at high maximum of the filter
        ---> Taken as the X error on the magnitude measurments.
        Parameter
        ---------
        Lambda      1Darray, wavelengths of the filter
        thoughput   1Darray, thoughtput of the filter
       
        Return
        ------
        FWHM        float, full width at high maximum
        '''

        ##normalise filter at max(Filter) = 1
        throughput = throughput * 1/max(throughput) 

        ##interp a 1A
        interp_L = numpy.arange(Lambda[0], Lambda[-1]+1, 1)
        interp_T = numpy.interp(interp_L, Lambda, throughput)

        ##find max and half max
        maxT = max(interp_T)
        HM = maxT / 2.

        ##find index where interp_T = max
        idx = (numpy.abs(interp_T-maxT)).argmin()

        ##define right and left part of the filter
        right = interp_T[idx+1:]
        rightL = interp_L[idx+1:]
        left = interp_T[:idx]
        leftL = interp_L[:idx]

        ###and fine the closest value in each part of the filter 
        ###to half a filter
        
        idxL = numpy.where(left > HM)
        idxR = numpy.where(right > HM) 
        FWHM = rightL[idxR][-1]-leftL[idxL][0]

        #plot().filter_FWHM(interp_L[idx], interp_L, interp_T, FWHM, HM)

        return FWHM

