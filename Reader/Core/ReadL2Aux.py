
import numpy as np
import os
import sys
from pylab import *
import tables as tb
import utm as utm
from scipy import linalg
#from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as pl
configfile='..\..\GeneralPaths.py'    
#configfile='..\GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import L2a_DATA_PROCESSED_PATH



class readL2file:

    def __init__(self, filenameroot, RadDataSet, verbose=True):
       # try:        
        filename=filenameroot+'.h5'
        if not os.path.isabs(filename):
            filenameh5 = os.path.join(L2a_DATA_PROCESSED_PATH, filename)
        self.h5file=tb.openFile(filenameh5, mode = "r")
        if verbose==True:
            print "-----------------------------------------"
            for group in self.h5file.walkGroups('/'):
                print "--", group
            print "-----------------------------------------"        

        self.RadiometricSubset=RadDataSet
        datasource='self.h5file.root.Retrieval.%s.Retrieval'%(self.RadiometricSubset)
        #print datasource
        data =eval(datasource)
        print data
        #print "INFO: new instance of dataprocessor for ", data   
        self.PD=  np.array([x['PD'] for x in data.iterrows()], np.double)
        self.CLW= np.array([x['CLW'] for x in data.iterrows()],np.double)
        self.WS= np.array([x['WS'] for x in data.iterrows()], np.double)
        self.Altitude= np.array( [x['Altitude'] for x in data.iterrows()],np.double)
        self.GPSTime= np.array( [x['GPSTime'] for x in data.iterrows()],np.double)
        self.Latitude= np.array( [x['Lat'] for x in data.iterrows()],np.double)
        self.Longitude= np.array( [x['Lon'] for x in data.iterrows()],np.double)
          
        print "WARNING The file contains more information than we are reading!!! "

        return None

    def fileclose(self):
        self.h5file.close()
        return None


if __name__ == "__main__":
    #---------------------
    configfile='..\GeneralPaths.py'
    sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
    from GeneralPaths import L2a_DATA_PROCESSED_PATH

    #rootfilename='2013_11_27__13_26_43__Testing'+'.bin'
    filenameroot='HAMMR_L2a_v002_20150520_ShannonBrown2_Day4_25minutes'
   
    L2File=readL2file(filenameroot, 'MW')

    plt.figure()
    plt.plot(L2File.Altitude)
    plt.show()
