# -*- coding: utf-8 -*-
"""
Created on Mon Oct 06 17:08:14 2014

@author: xbosch
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jul 23 13:27:00 2014

@author: xbosch
"""
import os
import sys
import pylab as pl
import matplotlib as mpl
from pylab import *
import numpy as np
import time
configfile='./../Core/DataProcessorAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from DataProcessorAux import DataProcessor
#configfile='./../Core/ThermistorsAux.py'
#sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
configfile='../../GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import CVS_FILES_DATA_BASE_PATH, L0b_DATA_PROCESSED_PATH
import csv
#####################################################################
## Files to be used for calibration and data procesisng. Use Example:
cvsFileName='ln2'
FromCVSFile=True
##################################################################### 
cvsfilenamerootpath=os.path.join(CVS_FILES_DATA_BASE_PATH,  cvsFileName+'.csv')
csvfileOpen = open(cvsfilenamerootpath, 'r')
spamreader = csv.reader(csvfileOpen, delimiter=' ')
preFilenameVector=[]
for row in spamreader:
    preFilenameVector.append(row[0])
filenamerootVector=preFilenameVector
print('############################')
print('CVS file:', cvsfilenamerootpath)
print( 'Content:', filenamerootVector)
print( '############################')
pathfordata=os.path.join(L0b_DATA_PROCESSED_PATH, cvsFileName+'CVS')
if not os.path.exists(pathfordata): 
    os.makedirs(pathfordata)
    print( '-->',pathfordata, 'has been created')
    
pathfordata=os.path.join(pathfordata, cvsFileName+'Out_SND_All_v005.csv')
csvfileOpen = open(pathfordata, 'w', newline='')
#writer = csv.writer(csvfileOpen)

fieldnames=['FileName', 'GPSTime', 'Radiometer Set', 'Channel', 'Cal. Coef.', 'Trec', 'Altitude', 'Lat.', 'Lon.', 'Ext Temp.', 'Rad. Temp.', 'std Rad. Temp.', 'VAMB', 'VLN2', 'CalTarget Temp.', 'Mult. Temp.', 'Horn Temp.', 'OpticalBench Temp.', 'Back Paraboloid Bottom Temp.', 'Back Paraboloid Middle Temp.', 'Back Paraboloid Top Temp.','CalTar|Upper Left[1]','CalTar|Lower Left[3]','CalTar|Center[2]','CalTar|Bottom Left[1]','CalTar|Bottom Right[3]','CalTar|Upper Right[3]' ,'CalTar|Lower Right[1]', 'CalTar|Top[2]']
writer = csv.DictWriter(csvfileOpen, fieldnames=fieldnames, dialect=csv.excel,  delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, escapechar='\\')
writer.writeheader()


#######################
ChannelSetToAnalyze='SND'               # Radiometer data set to be used. TODO: We could use all of them with a loop.  
TotalSecondsToAnalyzeVector=[19, 14]   # Time for calibration and data processing files, respectevily. 
AngularAverageDegrees=1                 # Mimimum resolution 0.0225, one motor sample per sample.
sixtyHertzFilter = [True, True]         # The 60 Hz filter for the calibration and the data files, respectevil. Only has effect for the SND channels. -- **Recomendation: Do not change it** .
#####################################################################
##
## Setting display figure parameters
##    
mpl.rc('xtick', labelsize=18)    # xlabel tics size
mpl.rc('ytick', labelsize=18)    # ylabel tics size
font = {'family':'serif','size': 14}    # general font type and size
mpl.rc('font', **font)
## Markers for displaying 
REFdisplayArray=['b', 'b', 'b', 'b','b', 'b', 'b', 'b','b', 'b', 'b', 'b','b', 'b.', 'b.', 'b.']
ANTdisplayArray=['r+', 'r+', 'r+', 'r+','r+', 'r+', 'r+', 'r+','r+', 'r+', 'r+', 'r+','r+', 'r+', 'r+', 'r+']
markers=['.','o','*']
#######################
## Lables not used any more. 
## ---- To be eventually deleted
#sixtyHertzFilterLabel = ['Filter ON', 'Filter ON'] 
#label=['Stiffener ON', 'Stiffener OFF']

#######################
## Flags for display 
##
PlotAngularImage=True
PlotTimeImage=True
PlotTipingCurve=False
ImageInterpolation=False
DisplayAuxData=True
PlotTime=True
#######################
#######################
#######################

#####################################################################
for CalIndex in range(0,len(filenamerootVector)-1):

    print( filenamerootVector)
    filenameroot_vector=[filenamerootVector[CalIndex][:-3]]
    print( filenameroot_vector)
    mpl.pyplot.close("all")

    
    for indexVector in range(0,1):
        
        TotalSecondsToAnalyze=TotalSecondsToAnalyzeVector[indexVector]
        filenameroot=filenameroot_vector[indexVector]
        #####################################################################
        ChSetdpa=DataProcessor(filenameroot,ChannelSetToAnalyze)
        Tint=ChSetdpa.Conf.RadIntegrationTime[ChannelSetToAnalyze]
        #ChannelsToAnalyze=[0,2]# :
        ChannelsToAnalyze=ChSetdpa.ChannelstoBeExplored
        Tint_seconds=Tint/1000
        finish=int(TotalSecondsToAnalyze/Tint_seconds)
        #FromCtoK=273.15
        #start=0
        #####################################################################
        #####################################################################
        if indexVector==0:    
            # Initializing some values for each dataprocessor file. 
            NumberOfChannels=np.max(ChSetdpa.ChannelstoBeExplored)+1
            cVector=np.zeros(NumberOfChannels)
            TrecVector=np.zeros(NumberOfChannels)
            Tzenith=np.zeros(NumberOfChannels)
            MeanArray=np.zeros(NumberOfChannels)
            stdArray =np.zeros(NumberOfChannels)
            DeltaTmeasured=np.zeros(NumberOfChannels)
            DeltaTheoretical=np.zeros(NumberOfChannels)      

        if DisplayAuxData==True: 
            mpl.rc('ytick', labelsize=30)
            fig1=ChSetdpa.Thermistors.printthermistors(filenameroot)
            figfilename =os.path.join(ChSetdpa.pathfordata,filenameroot+'_AllThermistors.png')
            fig1.set_size_inches(80, 60)
            fig1.savefig(figfilename, dpi = 100)
            mpl.rc('xtick', labelsize=18) 
            mpl.rc('ytick', labelsize=18)    
        
            fig2, Time, TemperatureArray=ChSetdpa.Thermistors.PlotThermistorByName(['ABEB Bloc','OpBench MMW-MCMs','CalTar|Center[2]'], filenameroot)
            figfilename =os.path.join(ChSetdpa.pathfordata,filenameroot+'_SpecificThermistors.png')
            fig2.savefig(figfilename)  
            
            fig2=ChSetdpa.GPSIMU.printEulerAngles(filenameroot)
            figfilename =os.path.join(ChSetdpa.pathfordata,filenameroot+'_GPSAttitude.png')
            fig2.savefig(figfilename)  
        
            fig3=ChSetdpa.GPSIMU.printAltitude(filenameroot)
            figfilename =os.path.join(ChSetdpa.pathfordata,filenameroot+'_GPSAltitude.png')
            fig3.savefig(figfilename)  
            
            fig4=ChSetdpa.GPSIMU.printTrajectory(filenameroot)
            figfilename =os.path.join(ChSetdpa.pathfordata,filenameroot+'_GPSTrajectory.png')
            fig4.savefig(figfilename)  
            Position=ChSetdpa.GPSIMU.GPS_Position[0]
            GPSTime=ChSetdpa.GPSIMU.GPS_GPSTime[0]
            
        
        for x in ChannelsToAnalyze: 
        
            ##########################################################################################              
            ### Converting the acquired datastream from counts to voltages for the X channel 
            ###    
            RadiometricDataVolts=ChSetdpa.Radiometer.fromCountstoV(ChSetdpa.Radiometer.Counts[:,x])
            ##########################################################################################              
            ### Selecting the data types filtering by datatype. Not used here currently, but used in other parts of the code
            ### 
            start=0          

            AntennaIndex,IndexDirty,AntennaIndexBooolean=ChSetdpa.Radiometer.calculateIndex(0,finish,start)
    

            
            pl.figure(111110)
            timeoffset=start*Tint_seconds
            pl.plot(timeoffset+AntennaIndex*Tint_seconds, RadiometricDataVolts[AntennaIndex], 'r.', ms=10, label='Code0 - ANT '+ChSetdpa.TitleArray[x])
            pl.legend(loc = 'best',shadow = True)
            pl.grid(True)            
            pl.show(block=False) 
  
            
            
            ##########################################################################################              
            ## Calculationg the antenna normalized voltages for each motor postion for each motor scan
            ##
            StartAngle=0                    # Starting angular value, do not change unless you know what you are doing
            StopAngle=StartAngle+360        # Ending angular value, do not change unless you know what you are doing
            SixtyHertzhSNDFiler=sixtyHertzFilter[0] # Used in case we are processing the SND subset, to filter out the 60 Hz coupling. 
            ##
            ## Assigning volts to each angular resultion (AngularAverageDegrees) for each scan from StartAngle to StopAngle for TotalSecondsToAnalyze
            ## Also, if required, applying the 60 Hz filter. 
            mnANTelevationAngle, stdANTelevationAngle, ANTMotorPositionMatrix, ANTTimeMatrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.ANTValueArray[ChannelSetToAnalyze], x, finish, RadiometricDataVolts, AngularAverageDegrees,StartAngle,StopAngle,TotalSecondsToAnalyze,ChannelSetToAnalyze,SixtyHertzhSNDFiler) 
            ANTTimeAveragedMotorPossition, ANTtimevector=ChSetdpa.Radiometer.calculateTrueCourse(ANTMotorPositionMatrix,ANTTimeMatrix)
            print( 'nadirIndex:', ChSetdpa.Radiometer.nadirIndex, 'zenithIndex', ChSetdpa.Radiometer.zenithIndex, ' Distance:', ChSetdpa.Radiometer.zenithIndex-ChSetdpa.Radiometer.nadirIndex, ' index possitions')

            ###################################################################
            ## Using the calibration target angular position for selecting the volts of the ExtCalTarget 
            C=mnANTelevationAngle
            mdat = np.ma.masked_array(C,C==0)
            AntennaValues= np.mean(mdat,axis=1) 

            L=len(ChSetdpa.Radiometer.BeamNadirAngle)
            NScanns=len(ANTtimevector)
            print( "Number of Scanns to be analyzed:", NScanns)
            
            SceneMaxAngle=int(1/AngularAverageDegrees)
            CalTarMaxAngle=int(10/AngularAverageDegrees)
            SceneIndex=np.mod(np.array(range(ChSetdpa.Radiometer.nadirIndex-SceneMaxAngle, ChSetdpa.Radiometer.nadirIndex+SceneMaxAngle))+L, L)
            CalTargetIndex=np.mod(np.array(range(ChSetdpa.Radiometer.zenithIndex-CalTarMaxAngle, ChSetdpa.Radiometer.zenithIndex+CalTarMaxAngle))+L, L)
            CalTargetIndex = np.array(range(200,220))
            SceneVoltage=np.mean(AntennaValues[SceneIndex])
            CalTargetVoltage=np.mean(AntennaValues[CalTargetIndex])
           
            ###############################################################


            ##########################################################################################    
            ## Gathering information for radiometric calibration from the first file or calibrating the data iwth the second file
            ## 
            if indexVector==0:
                ## Correcting the LN2 Boiling temperature for altitude, higher than 2000m then use 77 K
                # if Position[2]> 2000: 
                #     TphysicalLN2=77
                # else: 
                #     TphysicalLN2=80
                # ADAM 10 Oct 24 -- The boiling temp of LN2 at CSU temperature and pressure is about 76 K
                # Also in my measurements there are GPS problems and it's been using 80 K
                TphysicalLN2 = 76

                c=(ChSetdpa.Radiometer.CalTargetTemperature-TphysicalLN2)/(CalTargetVoltage-SceneVoltage) ## LN2 ideal temperature is 77 K but we consider 80. 
                Trec=c*CalTargetVoltage-ChSetdpa.Radiometer.CalTargetTemperature                        ## Important note, we are using Normalized Voltage so Vhot=1, if different this needs to be changed. 
                cVector[x]=c
                TrecVector[x]=Trec


                ### 118 GHz
                if x==0 or x==1 or x==2 or x==3 or x==8 or x==9 or x==10 or x==11:
                    PhysicalReceiverTempChannels =[35]
                    multiplierTemperatureCh=[36]
                ### 183 GHz
                elif x==4 or x==5 or x==6 or x==7 or x==12 or x==13 or x==14 or x==15:
                    PhysicalReceiverTempChannels =[38]
                    multiplierTemperatureCh=[37]
             
        
                RadiometerTemperature=ChSetdpa.Thermistors.GetMeanTemperatureChannels(PhysicalReceiverTempChannels)
                MultiplierTemperature=ChSetdpa.Thermistors.GetMeanTemperatureChannels(multiplierTemperatureCh)[0]
                HornTemp=ChSetdpa.Thermistors.GetMeanTemperatureChannels([2])[0]
                OptBenchTemp=ChSetdpa.Thermistors.GetMeanTemperatureChannels([3])[0]
                PBackBottomTemp=ChSetdpa.Thermistors.GetMeanTemperatureChannels([26])[0]
                PBackMiddleTemp=ChSetdpa.Thermistors.GetMeanTemperatureChannels([27])[0]
                PBacktopTemp=ChSetdpa.Thermistors.GetMeanTemperatureChannels([28])[0]       
                
                print( "------------------------------")
                print( "Main Calibration values for: ", ChSetdpa.TitleArray[x])
                print( "ThotVAlue-TcoldValue", CalTargetVoltage, SceneVoltage, " [Volt]")
                print( "--- Calibration Coefficient:", c , " [Kelvin/Volt]")
                print( "--- Treceiver:",  Trec, " [Kelvin]")
                print( "--- Lat/Lon", Position[0], '/', Position[1])
                print( "--- Altitude:", Position[2], ' m')
                print( "--- External Temperature:", np.mean(TemperatureArray[2,:]), ' C')
                print( "--- Horn, Opt. Bench, Paraboloid-{Bottom, Middle, Top} Temperatures:", HornTemp, OptBenchTemp, '-{', PBackBottomTemp,',', PBackMiddleTemp,',',PBacktopTemp, '} C')                
                print( "--- Radiometer Temperature:", RadiometerTemperature[0], "+/-", RadiometerTemperature[1], ' C')
                print( "--- Multiplier Temperature:", MultiplierTemperature, ' C')

                 
                writer.writerow({'FileName':filenameroot, 'GPSTime':GPSTime[0], 'Radiometer Set':ChannelSetToAnalyze,'Channel':x,'Cal. Coef.':c,'Trec': Trec,'Altitude':Position[2],'Lat.':Position[0], 'Lon.':Position[1], 'Ext Temp.':np.mean(TemperatureArray[2,:]), 'Rad. Temp.':RadiometerTemperature[0], 'std Rad. Temp.':RadiometerTemperature[1], 'VAMB':CalTargetVoltage,'VLN2':SceneVoltage,'CalTarget Temp.':ChSetdpa.Radiometer.CalTargetTemperature-273.15, 'Mult. Temp.':MultiplierTemperature, 'Horn Temp.':HornTemp, 'OpticalBench Temp.':OptBenchTemp, 'Back Paraboloid Bottom Temp.':PBackBottomTemp, 'Back Paraboloid Middle Temp.':PBackMiddleTemp, 'Back Paraboloid Top Temp.':PBacktopTemp, 'CalTar|Upper Left[1]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([8])[0],'CalTar|Lower Left[3]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([9])[0],'CalTar|Center[2]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([10])[0],'CalTar|Bottom Left[1]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([11])[0],'CalTar|Bottom Right[3]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([12])[0],'CalTar|Upper Right[3]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([13])[0], 'CalTar|Lower Right[1]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([14])[0], 'CalTar|Top[2]' :ChSetdpa.Thermistors.GetMeanTemperatureChannels([15])[0]})      
                
                fig = pl.figure(300+x+indexVector*10)
                ax = fig.add_subplot(111)
                Ta=AntennaValues*cVector[x]-TrecVector[x]
                pl.plot(Ta , 'b.')
                pl.show(block=False)
                pl.grid(True)
                pl.legend(loc = 'best',shadow = True)
                fig.suptitle( filenameroot+'ElevationCorrected__Channel_'+ChSetdpa.TitleArray[x], fontsize=10)
                # figfilename =os.path.join(ChSetdpa.pathfordata,filenameroot+'_ElevationCorrected_Channel_'+ChSetdpa.TitleArray[x]+'.png')
                figfilename = "foo2"  # ADAM - filenames are too long!!
                fig.savefig(figfilename)
         
csvfileOpen.close()
time.sleep(3)
print( open(pathfordata, 'rt').read()   )
print('FINISHED!')

