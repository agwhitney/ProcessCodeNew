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
# configfile='..\GeneralPaths.py'
# sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
# print( sys.path.append(os.path.dirname(os.path.expanduser(configfile))))
from GeneralPaths import L0b_DATA_PROCESSED_PATH, L1a_DATA_PROCESSED_PATH, CALVERSION
from pathlib import Path

import warnings
warnings.filterwarnings('ignore', category=tb.NaturalNameWarning)

class AntennaTemperatureSample(IsDescription):
    AntTempAngular     = UInt16Col(363)
    CalCoef            = UInt16Col()
    Trec               = UInt16Col()
    NDDR1              = UInt16Col()
    NDDR2              = UInt16Col()
    Tref               = UInt16Col()    
    Vref_CalTarg       = UInt16Col()
    Vref_Scene        = UInt16Col()

class NavigationDataSample(IsDescription):
    Roll      = Float32Col()
    Pitch      = Float32Col()
    Yaw      = Float32Col()
    Altitude      = Float32Col() 
    Latitude   = Float64Col() 
    Longitude   = Float64Col() 
    GPSTime    = Float64Col()
    CPUTime     = Float64Col()      
    
class Thermistorsample(IsDescription):
    Temperature      = Float16Col(40)    

class General(IsDescription):
    info       = StringCol(1000)

class TrueCoursesample(IsDescription):
    x = Float64Col() 
    y = Float64Col() 
    z = Float64Col()         
    

class CreateAntennaTempeartureFile():
    
    def __init__(self, filename):

        self.NavDataTable=False
        self.TemDataTable=False        
        print( 'Creating an Antenna temperature file for:',  filename )  
        self.rootfilename=filename
        self.pathforL1adata=L1a_DATA_PROCESSED_PATH #os.path.join(L1a_DATA_PROCESSED_PATH, self.rootfilename)
        self.thermistorName=[
            "OpBench MW-Horn",
            "OpBench MMW-MCMs",
            "OpBench Sounder-Horn",
            "OpBench Ambient Box",
            "not connected 1",
            "not connected 2",
            "not connected 3",
            "not connected 4",
            "CalTar|Upper Left[1]",
            "CalTar|Lower Left[3]",
            "CalTar|Center[2]",
            "CalTar|Bottom Left[1]",
            "CalTar|Bottom Right[3]",
            "CalTar|Upper Right[3]",
            "CalTar|Lower Right[1]",
            "CalTar|Top[2]",
            "MW QV-18/24-Int",
            "MW QV-34-Int",
            "MW QH-18/24-Ext",
            "MW QH-34-Ext",
            "MW-NS QH-18/24",
            "MW-NS QH-34",
            "MW-NS QV-18/24",
            "MW-NS QV-34",
            "+/-11.5V PS-Front",
            "+/-11.5V PS-Back",
            "Paraboloid Backside Bottom",
            "Paraboloid Backside Middle",
            "Paraboloid Backside Top",
            "Motor Controller",
            "Motor",
            "Motor PSU",
            "MMW-MCM90",
            "MMW-MCM130",
            "MMW-MCM168",
            "SND-118 External",
            "SND-118 Multiplier",
            "SND-183 Multiplier",
            "SND-183 External",
            "ABEB Bloc"
        ]
      
        if not os.path.isabs(self.rootfilename):
            self.filenameh5 = os.path.join(self.pathforL1adata, 'HAMMR_L1a_v00'+str(CALVERSION)+'_'+self.rootfilename)
        else:
            self.filenameh5 = os.path.join(self.pathforL1adata, 'HAMMR_L1a_v00'+str(CALVERSION)+'_'+Path(self.rootfilename).name)
        print(self.filenameh5)
        self.h5file = tb.open_file(self.filenameh5, mode = "w", title = "HAMMR L1a data")     
        self.ChannelsNamesMW=['34_GHz_QV','NotConnected', '18_GHz_QV', '24_GHz_QV','34_GHz_QH','NotConnected', '18_GHz_QH', '24_GHz_QH']
        self.ChannelsNamesMMW=['168_GHz','NotConnected','90_GHz','130_GHz']
        self.ChannelsNamesSND=['183m5_GHz','183m7_GHz', '183m3_GHz','183m6_GHz','118p0_GHz','118p5_GHz','118p4_GHz', '118p0.5_GHz','183m2_GHz','183m1_GHz', '183m8_GHz','183m4_GHz','118p1_GHz','118p3_GHz','118p0.25_GHz', '118p2_GHz']
        #######################################################################################################
        group = self.h5file.create_group("/", 'Information', 'Information regarding the file content')
        tableInfo = self.h5file.create_table(group, 'Read Me', General, title="Generic Information")     
        sampleInfo=tableInfo.row
        sampleInfo['info'] ='Antenna temperature with respect elevation angle (L1a), not in a geo-referenced grid'
        sampleInfo.append()
        sampleInfo['info'] ='The elevation angle has been corrected for the fact that the horn antenna is not at the focal point of the paraboloid'
        sampleInfo.append()
        sampleInfo['info'] ='Antenna pattern NOT removed (L1a)'
        sampleInfo.append()
        tableInfo.flush()
        #######################################################################################################
        tableInfo = self.h5file.create_table(group, 'Calibration_Version', General, title="Radiometric Calibration Information")     
        sampleInfo=tableInfo.row
        sampleInfo['info'] = str(CALVERSION)
        sampleInfo.append()
        tableInfo.flush()        
        #######################################################################################################
        tableInfo = self.h5file.create_table(group, 'Antenna_Temperature', General, title="Antenna Temperature")     
        sampleInfo=tableInfo.row
        sampleInfo['info'] = "Antenna temperature has to be divided by 10 in order to have Kelvin units."
        sampleInfo.append()
        tableInfo.flush()            
        #######################################################################################################
        tableInfo = self.h5file.create_table(group, 'Receiver_Temperature', General, title="Receiver Temperature")     
        sampleInfo=tableInfo.row
        sampleInfo['info'] = "Receiver temperature has to be divided by 10 in order to have Kelvin units."
        sampleInfo.append()
        tableInfo.flush()           
        #######################################################################################################
        tableInfo = self.h5file.create_table(group, 'Reference_Temperature', General, title="Reference Temperature")     
        sampleInfo=tableInfo.row
        sampleInfo['info'] = "Reference temperature has to be divided by 10 in order to have Kelvin units."
        sampleInfo.append()
        tableInfo.flush() 
        #######################################################################################################
        tableInfo = self.h5file.create_table(group, 'Vref_cal', General, title="Volts of the Reference Load while Looking at the Calibration Target")     
        sampleInfo=tableInfo.row
        sampleInfo['info'] = "Vref cal has to be divided by 10 in order to have milivolts units."
        sampleInfo.append()
        tableInfo.flush()
        #######################################################################################################
        tableInfo = self.h5file.create_table(group, 'Vref_Scene', General, title="Volts of the Reference Load while Looking at the Scene Target")     
        sampleInfo=tableInfo.row
        sampleInfo['info'] = "Vref Scene has to be divided by 10 in order to have milivolts units."
        sampleInfo.append()
        tableInfo.flush()                       
        #######################################################################################################
        tableInfo = self.h5file.create_table(group, 'Cal_Coef', General, title="Calibration Coefficient")     
        sampleInfo=tableInfo.row
        sampleInfo['info'] = "Calibration Coefficient has to be divided by 10 in order to have Kelvin/Volt units."
        sampleInfo.append()
        tableInfo.flush()          
    

    def fileclose(self):
        self.h5file.close()
        return None

    
    def InsertNavData(self,FirstSampleTime, GPSIMU):
         
         self.NavDataTable=True
         group = self.h5file.create_group("/", "NavigationData", 'Navigation Data')
         table = self.h5file.create_table(group, 'Navigation', NavigationDataSample, title="Time, GPStime, Navigation Data and Euler Angles" )
         sample = table.row

         for i in range(len(FirstSampleTime)):
         
            ## Finding the closest Auxiliar information to the measurement
            timestampref=np.abs(GPSIMU.GPS_Timestamp-FirstSampleTime[i])
            index=np.where(timestampref==np.min(timestampref))[0][0]
            ## 16 samples per second
            if i==0:
                IndexVector=range(index,index+7)
            elif i==len(FirstSampleTime)-1:
                IndexVector=range(index-7,index)
            else:
                IndexVector=range(index-7,index+7)

            ## Transition going South        
            PreYaw=GPSIMU.GPS_EulerAngles[IndexVector,2]*180/np.pi
            if np.max(PreYaw)-np.min(PreYaw)>180:
                ## Transition sample
                cleanIndex=np.where(PreYaw>0)[0]
                Yaw=PreYaw[cleanIndex]
            else:
                Yaw=PreYaw


            sample['Roll']=np.mean(GPSIMU.GPS_EulerAngles[IndexVector,0]*180/np.pi)
            sample['Pitch']=np.mean(GPSIMU.GPS_EulerAngles[IndexVector,1]*180/np.pi)
            sample['Yaw']=np.mean(Yaw)
            sample['Altitude']=np.mean(GPSIMU.GPS_Position[IndexVector,2])
            sample['Latitude']=np.mean(GPSIMU.GPS_Position[IndexVector,0])
            sample['Longitude']=np.mean(GPSIMU.GPS_Position[IndexVector,1])
            sample['GPSTime']=GPSIMU.GPS_GPSTime[index]
            sample['CPUTime'] = FirstSampleTime[i]
            sample.append()

         table.flush() 
         return None 

    
    def InsertTempData(self,Thermistor):

         self.TemDataTable=True         
         group = self.h5file.create_group("/", "TemperatureData", 'System Temperatures')
         table = self.h5file.create_table(group, 'Temperature', Thermistorsample, title="System Temperature" )
         sample = table.row
         L=Thermistor.ThermistorFilteredAndResampled.shape
         for i in range(L[1]):
            sample['Temperature']=Thermistor.ThermistorFilteredAndResampled[:,i]
            sample.append()
         ThermistorNames = self.h5file.create_array(group, "ThermistorNames", Thermistor.thermistorName, title="Names and Id of the thermistors")
         table.flush() 
         return None 

    def InsertTable(self, RadiometricDataType, x, Data, CalCoef, Trec, NDDR1, NDDR2, Tref, Vref_CalTar, Vref_Sceene, MotorPosition, truecourse_x, truecourse_y,truecourse_z, NEAT, motorInfo):

         ChannelName=eval('self.ChannelsNames' + RadiometricDataType.upper()+'['+str(x)+']')   
         try:
            group = self.h5file.get_node("/RadiometricData/"+RadiometricDataType)
         except:
            #raise ValueError('Creating the h5 node') # or exception of your choosing
            try:
                group = self.h5file.get_node("/RadiometricData/")
            except:    
                self.h5file.create_group("/", 'RadiometricData', 'Antenna Temperature and Elevation Angle' )
            group =self.h5file.create_group("/RadiometricData/", RadiometricDataType, 'Antenna Temperature and Elevation Angle for ' + RadiometricDataType)
            group = self.h5file.get_node("/RadiometricData/"+RadiometricDataType)
            print('Creating the h5 node for ', RadiometricDataType)
            Mposit = self.h5file.create_array(group, "MotorPosition", MotorPosition, title="Motor Position in Counts for the " + ChannelName + " Channel")
            table = self.h5file.create_table(group, 'TrueCourse', TrueCoursesample, title="Beam Pointing Vector" )
            sample = table.row
            TotalNumberofAngles=len(truecourse_x)
            for i in range(TotalNumberofAngles):
               sample['x'] = truecourse_x[i]
               sample['y'] = truecourse_y[i]
               sample['z'] = truecourse_z[i]
               sample.append()
            MotorInformation = self.h5file.create_array(group, "MotorInformation", motorInfo, title="Mean and standard deviation of the raw motor step when spinning")
 
            table.flush() 

         RadiometricResolutionInformation = self.h5file.create_array(group, 'Ch_'+ChannelName.replace('.','_')+'_NEAT', NEAT, title="Radiometric resolution in Kelvin")   
         
         textforATTable="NO geo-referenced Antenna Temperature for the " + ChannelName + " Channel"
         table = self.h5file.create_table(group, 'Ch_'+ChannelName.replace('.','_')+'_AntTemp', AntennaTemperatureSample, title=textforATTable)
         sample = table.row
         TotalNumberofScans=len(Trec)
         for i in range(TotalNumberofScans):
           # First, assign the values to the Particle record
           # print i
            IntermidiateVariableAntTempAngular=10*Data[i,:]
            IntermidiateVariableCalCoef=10*CalCoef[i]
            IntermidiateVariableTrec=10*Trec[i]
            IntermidiateVariableTref=10*Tref[i]
            IntermidiateVariableVref_CalTar= 10000*Vref_CalTar[i] 
            IntermidiateVariableVref_Sceene= 10000*Vref_Sceene[i] 

            sample['AntTempAngular']  = IntermidiateVariableAntTempAngular.astype(np.uint16)
            sample['CalCoef'] =IntermidiateVariableCalCoef.astype(np.uint16)
            sample['Trec'] = IntermidiateVariableTrec.astype(np.uint16)
            sample['NDDR1']  = NDDR1[i]
            sample['NDDR2']  = NDDR2[i]
            sample['Tref']  = IntermidiateVariableTref.astype(np.uint16)
            sample['Vref_CalTarg']  = IntermidiateVariableVref_CalTar.astype(np.uint16)
            sample['Vref_Scene']  = IntermidiateVariableVref_Sceene.astype(np.uint16)          
            sample.append()
         table.flush() 

         
         return None

if __name__ == "__main__":
    		#--------------------------------------

    #rootfilename='2013_11_27__13_26_43__Testing'+'.bin'
    filenameroot='2014_07_11__10_13_23__24of24_TwinOtter_EngDay3_Powell'
   
    try:
        pathforL1adata=os.path.join(L0b_DATA_PROCESSED_PATH, filenameroot)
        if not os.path.exists(pathforL1adata): 
            os.makedirs(pathforL1adata)
            print( '-->',pathforL1adata, 'has been created')
    except:
         print( "WARNING: I cannot create a folder for the results")
         
    CATF = CreateAntennaTempeartureFile(filenameroot,pathforL1adata)