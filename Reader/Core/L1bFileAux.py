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
from GeneralPaths import L0b_DATA_PROCESSED_PATH, L1a_DATA_PROCESSED_PATH, L1b_DATA_PROCESSED_PATH, CALVERSION

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


class TrajectoryDataSample(IsDescription):
    Altitude   = Float32Col(1) 
    Latitude   = Float64Col(1) 
    Longitude  = Float64Col(1) 
    GPSTime    = Float64Col(1) 

class General(IsDescription):
    info       = StringCol(8192)
    

class CreateGeoReferencedAntennaTempeartureFile():
    
    def __init__(self, filename):

        self.TrajDataTable=False
        print 'Creating a Geo-Referenced Antenna temperature file for:',  filename   
        self.rootfilename=filename
        self.pathforL1adata=L1b_DATA_PROCESSED_PATH
      
              
        if not os.path.isabs(self.rootfilename):
	      self.filenameh5 = os.path.join(self.pathforL1adata, self.rootfilename+'.h5')
        print self.filenameh5
        self.h5file = tb.open_file(self.filenameh5, mode = "w", title = "HAMMR L1b data")     
        self.ChannelsNamesMW=['MW_34_GHz_QV','NotConnected', 'MW_18_GHz_QV', 'MW_24_GHz_QV','MW_34_GHz_QH','NotConnected', 'MW_18_GHz_QH', 'MW_24_GHz_QH']
        self.ChannelsNamesMMW=['MMW_168_GHz','NotConnected','MMW_90_GHz','MMW_130_GHz']
        self.ChannelsNamesSND=['SND_183m5_GHz','SND_183m7_GHz', 'SND_183m3_GHz','SND_183m6_GHz','SND_118p0_GHz','SND_118p5_GHz','SND_118p4_GHz', 'SND_118p0.5_GHz','SND_183m2_GHz','SND_183m1_GHz', 'SND_183m8_GHz','SND_183m4_GHz','SND_118p1_GHz','SND_118p3_GHz','SND_118p0.25_GHz', 'SND_118p2_GHz']
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
        
        
    def fileclose(self):
        self.h5file.close()
        return None

    def InsertAircraftTrajectory(self,Lat, Lon, GPSTime, Altitude):
         
        self.TrajDataTable=True
        group = self.h5file.createGroup("/", "AircraftTrajectory", 'Navigation Data')
        table = self.h5file.createTable(group, 'Trajectory', TrajectoryDataSample, title="Lat-Lon Trajectory and GPStime" )
        sample = table.row

        for i in xrange(len(Lat)):
           sample['Altitude']=Altitude[i]
           sample['Latitude']=Lat[i]
           sample['Longitude']=Lon[i]
           sample['GPSTime']=GPSTime[i]
           sample.append()

        table.flush() 
        return None 

    def InsertTable(self, RadiometricDataType, x, Lat, Lon, Tant, Altitude, NadirAngle, AzimuthAngle, MajorSemiAxis, MinorSemiAxis, FootprintAngle, Time):
        
         ChannelName=x #eval('self.ChannelsNames' + RadiometricDataType+'['+str(x)+']')   
         try:
            group = self.h5file.getNode("/RadiometricData/"+RadiometricDataType)
         except:
            #raise ValueError('Creating the h5 node') # or exception of your choosing
            try:
                group = self.h5file.getNode("/RadiometricData/")
            except:    
                self.h5file.createGroup("/", 'RadiometricData', 'Antenna Temperature and Elevation Angle' )
            group =self.h5file.createGroup("/RadiometricData", RadiometricDataType, 'Antenna Temperature and Elevation Angle for ' + RadiometricDataType)
            group = self.h5file.getNode("/RadiometricData/"+RadiometricDataType)
            print 'Creating the h5 node for ', RadiometricDataType
         
         textforATTable="NO geo-referenced Antenna Temperature for the " + ChannelName + " Channel"
         table = self.h5file.createTable(group, 'Ch_'+ChannelName.replace('.','_')+'_AntTemp', AntennaTemperatureSample, title=textforATTable)
         sample = table.row
         TotalNumberofPoints=len(Tant)

         for i in xrange(TotalNumberofPoints):
           # First, assign the values to the Particle record
            #IntermidiateAntTemperature=10*Tant[i]
            sample['AntTemperature']  = Tant[i]
            sample['Lat'] = Lat[i]
            sample['Lon'] = Lon[i]
            sample['Altitude']  =Altitude[i]
            sample['ElevationAngle']  = NadirAngle[i]
            sample['AzimuthAngle']  = AzimuthAngle[i]
            sample['GPSTime']  = Time[i] 
            sample['MajorSemiAxis']= MajorSemiAxis[i]
            sample['MinorSemiAxis']=MinorSemiAxis[i]
            sample['FootprintAngle']=FootprintAngle[i]  
            sample.append()

         table.flush()
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