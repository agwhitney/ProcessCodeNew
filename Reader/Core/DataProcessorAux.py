import numpy as np
import pylab as pl
from pylab import *
import os
import sys
import tables as tb

from Reader.Core.GPSIMUAux import GPSIMU
from Reader.Core.ThermistorsAux import thermistors
from Reader.Core.ConfigurationAux import configread
from Reader.Core.RadiometerAux import radiometer
#configfile='..\..\GeneralPaths.py'
# configfile='..\GeneralPaths.py'
# sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import H5_DATA_BASE_PATH, L0b_DATA_PROCESSED_PATH, L1a_DATA_PROCESSED_PATH

class dataprocess:

       
    FromCtoK=273.15    
    #MotorOffset=3800   # in counts

    def __init__(self,filepath, RadiometricDataType, verbose=False, NearRealTime=False):
        
        ## Opening the h5 file
        # try:        
        filenameh5=filepath.name
        h5file=tb.open_file(filepath, mode = "r")
        if verbose==True:
            print( "-----------------------------------------")
            for group in h5file.walkGroups('/'):
                print( "--", group)
            print( "-----------------------------------------"   )     
        # except:
        #    print("File not found:", filenameroot   )                  
   
        ## Reading radiometric data
        #try:
        self.Radiometer=radiometer(h5file, RadiometricDataType, verbose, NearRealTime)
        #except:
        #   print "No ", RadiometricDataType, " radiomter data found!"           
        
        ## Reading thermistors data
        # try:
        self.Thermistors=thermistors(h5file, verbose)
        # except:
        #     print( "WARNING: The processor cannot find thermistor information on the h5 file")
        ## Reading GPS/IMU  data
        # try:
        self.GPSIMU=GPSIMU(h5file, verbose)
        # except:
        #     print( "WARNING: The processor cannot find thermistor information on the h5 file")
        ## Reading configuration files    tighten
        # try:            
        self.Conf=configread(h5file,verbose)
        # except:
        #     print( "WARNING: The processor cannot find a configuration file information on the h5 file")
        # try:
        self.pathfordata=os.path.join(L0b_DATA_PROCESSED_PATH, filepath.stem)
        if not os.path.exists(self.pathfordata): 
            os.makedirs(self.pathfordata)
            print( '-->',self.pathfordata, 'has been created')

                
        # except:
        #     print( "WARNING: I cannot create a folder for the results")
            
        ##################################################        
        h5file.close()      
        ##################################################
        TitleArrayMW=['34-QV','NC2','18-QV','24-QV','34-QH','NC1','18-QH','24-QH']
        TitleArrayMMW=['168','NC3', '90','130']
        TitleArraySND=['183-5','183-7', '183-3','183-6','118+0','118+5','118+4', '118+0.5','183-2','183-1', '183-8','183-4','118+1','118+3','118+0.225', '118+2']
        ## Defining frequency center for each channel
        FrequencyVectorMW=[34, 0, 18, 24,34, 0, 18, 24]
        FrequencyVectorMMW=[168, 0, 90, 130]
        # FrequencyVectorSND=[183-5,183-7, 183-3,183-6,118+0,118+5,118+4,118+0.5,183-2,183-1, 183-8,183-4,118+1,118+3,118+0.225, 118+2] ## +1 and +5 got switch for 118 GHZ
        # ADAM 2 Oct 24 -- L0b labels 118+0.25 as 118.0.225 (correct above) and 118+0.5 as 118+0.4 (incorrect above)
        FrequencyVectorSND=[183-5,183-7, 183-3,183-6,118+0,118+5,118+4,118+0.4,183-2,183-1, 183-8,183-4,118+1,118+3,118+0.225, 118+2]
        ##         
        ChannelstoBeExploredMW =[0,2,3,4,6,7]
        ChannelstoBeExploredMMW =[0,2,3]
        ChannelstoBeExploredSND =[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]  #June 2014,Ch4 has been removed, XB
        ## 
        AntennaAngularOffsetMW=-15.75*np.pi/180 # Calculated using the horn distance from the focal point 8.0 cm and the focal length to the paraboloid 28.575 cm (11.25"), Angle=atan(8/28.575)
        AntennaAngularOffsetMMW=0              # Centered right at the paraboloid focal point
        AntennaAngularOffsetSND=+3.4*np.pi/180 # Calculated using the horn distance from the focal point -2.7 cm and the focal length to the paraboloid 28.575 cm (11.25"), Angle=atan(-2.7/28.575)
        ##
        self.TitleArray=eval('TitleArray' + RadiometricDataType.upper())
        self.ChannelstoBeExplored=eval('ChannelstoBeExplored' + RadiometricDataType.upper())
        self.FrequencyVector=eval('FrequencyVector' + RadiometricDataType.upper())
        self.AntennaAngularOffset=eval('AntennaAngularOffset' + RadiometricDataType.upper())
        ################################################## 
        self.Radiometer.pathfordata = self.pathfordata  
        self.Radiometer.filenameroot= filepath.stem   
        self.Radiometer.AntennaAngularOffset=self.AntennaAngularOffset
        self.Radiometer.Conf=self.Conf
        self.Radiometer.RadiometricDataType=RadiometricDataType
        self.Radiometer.ChannelsNames=self.TitleArray
        self.Radiometer.Thermistors=self.Thermistors
        self.Radiometer.UpdateConfigParameters()
        ##################################################            
        return None
           
        
def main():
    
    print( "\n\n-+++------------------------------------+++-" )
    print( "## -- This is a Class, not to be run as a SCRIPT -- ##")
    filenameroot='2014_07_10__09_31_36__2of24_TwinOtter_EngDay2_Powell'
    print( "-->WARNING: %s is provided with the repository for debugin purposes only"%filenameroot)
    print( "-+++------------------------------------+++-" )
    ## Changing figure parameters    
    matplotlib.rc('xtick', labelsize=18) 
    matplotlib.rc('ytick', labelsize=18)
    font = {'weight' : 'bold','size': 14}
    matplotlib.rc('font', **font)
    ChannelSetToAnalyze='SND'  # {'MW', 'MMW', 'SND'}
    TotalSecondsToAnalyze=5
    ChSetdpa=dataprocess(filenameroot,ChannelSetToAnalyze)
    print( ChSetdpa.Conf.RadIntegrationTime)
    Tint=ChSetdpa.Conf.RadIntegrationTime[ChannelSetToAnalyze] 
    REFdisplayArray=['b+', 'm+', 'r+', 'k+','b+', 'm+', 'r+', 'k+','b+', 'm+', 'r+', 'k+','b+', 'm+', 'r+', 'k+']
    ANTdisplayArray=['b.', 'm.', 'r.', 'k.','b.', 'm.', 'r.', 'k.','b.', 'm.', 'r.', 'k.','b.', 'm.', 'r.', 'k.']
   
    Tint_seconds=Tint/1000
    start=0
    finish=TotalSecondsToAnalyze/Tint_seconds
    
    for x in ChSetdpa.ChannelstoBeExplored:     
        print( x, ChSetdpa.Radiometer.ANTValue, ChSetdpa.Radiometer.REFValue)
        RadiometricDataVolts=ChSetdpa.Radiometer.fromCountstoV(ChSetdpa.Radiometer.Counts[:,x])
        ReferenceIndex,IndexDirty,ReferenceIndexBooolean=ChSetdpa.Radiometer.calculateIndex(0,finish,start)
        AntennaIndex,IndexDirty,AntennaIndexBooolean=ChSetdpa.Radiometer.calculateIndex(5,finish,start)
        print( "REF "+ str(ChSetdpa.TitleArray[x])+"-"+str(x)+" = mean "+ str(np.mean(RadiometricDataVolts[ReferenceIndex]))+ ' -- std'+ " = "+ str(np.std(RadiometricDataVolts[ReferenceIndex])))  
        print( "ANT "+ str(ChSetdpa.TitleArray[x])+" = mean "+ str(np.mean(RadiometricDataVolts[AntennaIndex])) +'  -- std' + " = "+ str(np.std(RadiometricDataVolts[AntennaIndex])))
        pl.figure(x+10)
        pl.grid(True)
        timeoffset=start*Tint_seconds
        #pl.plot(timeoffset+ReferenceIndex*Tint_seconds, RadiometricDataVolts[ReferenceIndex], REFdisplayArray[x], label='Ref' +ChSetdpa.TitleArray[x])
        #pl.plot(timeoffset+AntennaIndex*Tint_seconds, RadiometricDataVolts[AntennaIndex], ANTdisplayArray[x], label='Ant'+ChSetdpa.TitleArray[x])
        pl.plot(RadiometricDataVolts[0:-1], ANTdisplayArray[x], label='Ant'+ChSetdpa.TitleArray[x])
        
        pl.legend(loc = 'best',shadow = True)
        pl.ylabel("Volts")
        pl.xlabel("Seconds")
        pl.title(ChannelSetToAnalyze)
        pl.show()    

if __name__ == "__main__":
    main()