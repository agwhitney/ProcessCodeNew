# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 16:22:15 2014

@author: xbosch
"""
import os
import sys
# configfile='./Core/DataProcessorAux.py'
# sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from Reader.Core.DataProcessorAux import DataProcessor
# configfile='./Core/ThermistorsAux.py'
# sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
# configfile='./Core/GeneralPaths.py'
# sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import CVS_FILES_DATA_BASE_PATH, L0b_DATA_PROCESSED_PATH
import csv
from pathlib import Path

"""
This is not used in Cal Steps 1 or 2.
"""

class OpenCVSBatchFile:
    
    def __init__(self, cvsBatchFileName):
        ##################################################################### 
        cvsfilenamerootpath=os.path.join(CVS_FILES_DATA_BASE_PATH,  cvsBatchFileName+'.csv')
        csvfileOpen = open(cvsfilenamerootpath, 'r')
        spamreader = csv.reader(csvfileOpen, delimiter=',')
        preFilenameVector=[]
        for row in spamreader:
            preFilenameVector.append(row[0])
        self.filenamerootVector=preFilenameVector
        print( '############################')
        print( 'CVS file:', cvsfilenamerootpath)
        print( 'Content:', self.filenamerootVector)
        print( '############################')
        self.pathfordata=os.path.join(L0b_DATA_PROCESSED_PATH, cvsBatchFileName+'_CVS')
        if not os.path.exists(self.pathfordata): 
            os.makedirs(self.pathfordata)
            print('-->',self.pathfordata, 'has been created')
        return
    