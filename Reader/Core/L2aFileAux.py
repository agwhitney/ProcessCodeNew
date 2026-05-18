# -*- coding: utf-8 -*-
"""
Created on Tue Sep 23 11:02:42 2014

@author: xbosch
"""
import sys
import os
import platform
import tables as tb
from tables import *
import numpy as np
## When running it as an script
#configfile='..\..\GeneralPaths.py'
## When running it as a class
configfile='..\GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
print sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import L0b_DATA_PROCESSED_PATH, L1a_DATA_PROCESSED_PATH, L1b_DATA_PROCESSED_PATH, L2a_DATA_PROCESSED_PATH, CALVERSION

class AntennaTemperatureSample(IsDescription):
    AntTemperature = Float32Col(1)
    Lat            = Float32Col(1)
    Lon            = Float32Col(1)
    Altitude       = Float32Col(1)
    ElevationAngle = Float32Col(1)
    MajorSemiAxis = Float32Col(1)
    MinorSemiAxis = Float32Col(1)
    FootprintAngle = Float32Col(1)
    AzimuthAngle   = Float32Col(1)
    GPSTime        = Float64Col(1)

class RetrievedSample(IsDescription):
    PD              = Float32Col(1)
    CLW            = Float32Col(1)
    WS             = Float32Col(1)
    Lat            = Float32Col(1)
    Lon            = Float32Col(1)
    Altitude       = Float32Col(1)    
    GPSTime        = Float64Col(1)


class General(IsDescription):
    info       = StringCol(8192)
    
class CreateL2File():
    
    def __init__(self, filename):

        self.TrajDataTable=False
        print 'Creating a Retrieval file for:',  filename   
        self.rootfilename=filename
        self.pathforL2adata=L2a_DATA_PROCESSED_PATH
      
              
        if not os.path.isabs(self.rootfilename):
	      self.filenameh5 = os.path.join(self.pathforL2adata, self.rootfilename+'.h5')
        print self.filenameh5
        #self.h5file = tb.open_file(self.filenameh5, mode = "w", title = "HAMMR L2a data")
        ### Append it!! 
        self.h5file = tb.open_file(self.filenameh5, mode = "w", title = "HAMMR L2a data") 

        self.ChMW=[0,2,3,4,6,7]              #Note that 1 and 5 are missing 
        self.ChMMW=[0,2,3,]                   # Note that 1 is missing
        self.ChSND=[0,1,2,3,5,6,7,8,9,10,11,12,13,14,15]   # Note that 4 is mising
        self.ChannelsNamesMW =['MW_34_GHz_QV','NotConnected', 'MW_18_GHz_QV', 'MW_24_GHz_QV','MW_34_GHz_QH','NotConnected', 'MW_18_GHz_QH', 'MW_24_GHz_QH']
        self.ChannelsNamesMMW=['MMW_168_GHz','NotConnected','MMW_90_GHz','MMW_130_GHz']
        self.ChannelsNamesSND=['SND_183m5_GHz','SND_183m7_GHz', 'SND_183m3_GHz','SND_183m6_GHz','SND_118p0_GHz','SND_118p5_GHz','SND_118p4_GHz', 'SND_118p05_GHz','SND_183m2_GHz','SND_183m1_GHz', 'SND_183m8_GHz','SND_183m4_GHz','SND_118p1_GHz','SND_118p3_GHz','SND_118p025_GHz', 'SND_118p2_GHz']
        #######################################################################################################
        self.ChannelSetToAnalyzeVector=['MW','MMW','SND'] 
        self.Ch={'MW':self.ChMW, 'MMW':self.ChMMW, 'SND':self.ChSND}
        self.ChNames={'MW':self.ChannelsNamesMW, 'MMW':self.ChannelsNamesMMW, 'SND':self.ChannelsNamesSND}
        #######################################################################################################
  


        group = self.h5file.createGroup("/", 'GeneralInformation', 'Information about the file content')
        tableInfo = self.h5file.createTable(group, 'ReadMe', General, title="Generic Information")     
        sampleInfo=tableInfo.row
        sampleInfo['info'] ='Antenna temperature in a geo-referenced grid'
        sampleInfo.append()
        sampleInfo['info'] ='Antenna pattern NOT removed'
        sampleInfo.append()
        tableInfo.flush()
        #######################################################################################################
        group = self.h5file.createGroup("/", 'RadiometricCalibrationInformation', 'Information regarding the radiometric calibration version')
        tableInfo = self.h5file.createTable(group, 'ReadMe', General, title="Radiometric Calibration Information")     
        sampleInfo=tableInfo.row
        sampleInfo['info'] ='Calibration Version:' + str(CALVERSION)
        sampleInfo.append()
        tableInfo.flush() 

        self.tableret=[] 
        self.sampleret =[] 
        #### Under Test
        self.sampleant={'MW':[], 'MMW':[], 'SND':[]} 
        self.tableant={'MW':[], 'MMW':[], 'SND':[]}    
        
        
    def fileclose(self):
        self.h5file.close()
        return None

    def InsertAntennaTemperatureTable(self, RadiometricDataType, ChannelName, m, x):
        
         try:
            group = self.h5file.getNode("/RadiometricData/"+RadiometricDataType)

         except:
            #raise ValueError('Creating the h5 node') # or exception of your choosing
            try:
                group = self.h5file.getNode("/RadiometricData/")
            except:    
                self.h5file.createGroup("/", 'RadiometricData', 'Antenna Temperature and Elevation Angle')
              #  print 'Creating the RadiometricData node' 
            try:
                group =self.h5file.createGroup("/RadiometricData/", RadiometricDataType, 'Antenna Temperature and Elevation Angle for ' + RadiometricDataType)
             #   print 'RadiometricData -> Creating the h5 node for ', RadiometricDataType 
            except:      
                print "Table already exists!"
         try: 
            group = self.h5file.getNode("/RadiometricData/"+RadiometricDataType)
            textforATTable="NO geo-referenced Antenna Temperature for the " + str(ChannelName) + " Channel"
            #print x, " inside Try", 'Ch_'+str(ChannelName)+'_AntTemp'
            self.tableant[RadiometricDataType].append(self.h5file.createTable(group, 'Ch_'+str(ChannelName)+'_AntTemp', AntennaTemperatureSample, title=textforATTable))
            self.sampleant[RadiometricDataType].append(self.tableant[RadiometricDataType][x].row)

         except:  
            print('.'),
           # print "Table already exists!"
           # print "Writting at Table ", RadiometricDataType, x
            #print self.tableant[RadiometricDataType][x]
            #print self.sampleant[RadiometricDataType][x]
         
         Tant=m['AntTemperature'][0][0][0]
         TotalNumberofPoints=len(Tant)

         for i in xrange(TotalNumberofPoints):

           # First, assign the values to the Particle record
            self.sampleant[RadiometricDataType][x]['AntTemperature']  = m['AntTemperature'][0][0][0][i] #Tant[i]
            self.sampleant[RadiometricDataType][x]['Lat'] = m['Lat'][0][0][0][i]
            self.sampleant[RadiometricDataType][x]['Lon'] = m['Lon'][0][0][0][i]
            self.sampleant[RadiometricDataType][x]['Altitude']  =m['Altitude'][0][0][0][i]
            self.sampleant[RadiometricDataType][x]['ElevationAngle']  = m['ElevationAngle'][0][0][0][i]
            self.sampleant[RadiometricDataType][x]['AzimuthAngle']  = m['AzimuthAngle'][0][0][0][i]
            self.sampleant[RadiometricDataType][x]['GPSTime']  = m['GPSTime'][0][0][0][i]
            self.sampleant[RadiometricDataType][x]['MajorSemiAxis'] = m['MajorSemiAxis'][0][0][0][i]
            self.sampleant[RadiometricDataType][x]['MinorSemiAxis'] = m['MinorSemiAxis'][0][0][0][i]
            self.sampleant[RadiometricDataType][x]['FootprintAngle'] = m['FootprintAngle'][0][0][0][i]
            self.sampleant[RadiometricDataType][x].append()

         self.tableant[RadiometricDataType][x].flush()
         #print self.tableant[x]
         #print "-------------------"
         return None

    def InsertRetrievalTable(self, RadiometricDataType, PD, CLW, WS, Lat, Lon, Altitude, Time):
        
         #ChannelName=x #eval('self.ChannelsNames' + RadiometricDataType+'['+str(x)+']')   
         try:
            group = self.h5file.getNode("/Retrieval/"+RadiometricDataType)
         except:
            #raise ValueError('Creating the h5 node') # or exception of your choosing
            try:
                group = self.h5file.getNode("/Retrieval/")
            except:    
                self.h5file.createGroup("/", 'Retrieval', 'Path Delay, Water Liquid Content and Wind Speed' )
                print 'Creating the Retrieval node'            
            try:
                group = self.h5file.createGroup("/Retrieval/", RadiometricDataType, 'Path Delay, Water Liquid Content and Wind Speed for ' + RadiometricDataType)
                group = self.h5file.getNode("/Retrieval/"+RadiometricDataType)
                print 'Retrieval -> Creating the h5 node for ', RadiometricDataType
                textforATTable="Path Delay, Water Liquid Content and Wind Speed for " + RadiometricDataType
                self.tableret = self.h5file.createTable(group, 'Retrieval', RetrievedSample, title=textforATTable)
                self.sampleret = self.tableret.row
            except:
                print "Table already exist!"

        
         TotalNumberofPoints=len(PD)
         for ii in xrange(TotalNumberofPoints):
           # First, assign the values to the Particle record
            self.sampleret['PD']  = PD[ii]
            self.sampleret['CLW']  = CLW[ii]
            self.sampleret['WS']  = WS[ii]            
            self.sampleret['Lat'] = Lat[ii]
            self.sampleret['Lon'] = Lon[ii]
            self.sampleret['Altitude']  =Altitude[ii]
            self.sampleret['GPSTime']  = Time[ii] 
            self.sampleret.append()


         self.tableret.flush()
         return None


if __name__ == "__main__":
    		#--------------------------------------

    #rootfilename='2013_11_27__13_26_43__Testing'+'.bin'
    filenameroot='2014_07_11__10_13_23__24of24_TwinOtter_EngDay3_Powell'
   
    try:
        pathforL1adata=os.path.join(L1a_DATA_PROCESSED_PATH, filenameroot)
        if not os.path.exists(pathforL1adata): 
            os.makedirs(pathforL1adata)
            print '-->',pathforL1adata, 'has been created'
    except:
         print "WARNING: I cannot create a folder for the results"
         
    CATF = CreateGeoReferencedAntennaTempeartureFile(filenameroot,pathforL1adata)