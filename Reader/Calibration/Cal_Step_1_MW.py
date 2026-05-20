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
ln2_filename = 'ln2'  # AGW
import csv
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import time

from GeneralPaths import CVS_FILES_DATA_BASE_PATH, L0b_DATA_PROCESSED_PATH
from Reader.Core.DataProcessorAux import DataProcessor


def calstep1(filepaths: list[Path]):
    #####################################################################
    ## Files to be used for calibration and data procesisng. Use Example:
    cvsFileName = ln2_filename
    NewDataFlag = True  # Set True if data is newer than 2020
    FromCVSFile = True
    ##################################################################### 
    cvsfilenamerootpath = os.path.join(CVS_FILES_DATA_BASE_PATH,  cvsFileName+'.csv')
    csvfileOpen = open(cvsfilenamerootpath, 'r')
    spamreader = csv.reader(csvfileOpen, delimiter=' ')
    preFilenameVector = []
    for row in spamreader:
        preFilenameVector.append(row[0])
    filenamerootVector = preFilenameVector
    print('############################')
    print('CVS file:', cvsfilenamerootpath)
    print('Content:', filenamerootVector)
    print('############################')
    pathfordata = os.path.join(L0b_DATA_PROCESSED_PATH, cvsFileName+'CVS')
    if not os.path.exists(pathfordata): 
        os.makedirs(pathfordata)
        print( '-->',pathfordata, 'has been created')
        
    pathfordata = os.path.join(pathfordata, cvsFileName+'Out_MW_test.csv')
    csvfileOpen = open(pathfordata, 'w', newline='')
    #writer = csv.writer(csvfileOpen)
    fieldnames=[
        'FileName',
        'GPSTime',
        'Radiometer Set',
        'Channel',
        'Cal. Coef.',
        'Trec',
        'Altitude',
        'Lat.',
        'Lon.',
        'Ext Temp.',
        'Rad. Temp.',
        'std Rad. Temp.',
        'TNS1',
        'TNS2',
        'TNS3',
        'VNS1',
        'VNS2',
        'VNS3',
        'Temp. MW-NS-18/24',
        'Temp. MW-NS-34',
        'VAMB',
        'VLN2',
        'Vref',
        'stdVref',
        'CalTarget Temp.',
        'Horn Temp.',
        'OpticalBench Temp.',
        'Back Paraboloid Bottom Temp.',
        'Back Paraboloid Middle Temp.',
        'Back Paraboloid Top Temp.',
        'CalTar|Upper Left[1]',
        'CalTar|Lower Left[3]',
        'CalTar|Center[2]',
        'CalTar|Bottom Left[1]',
        'CalTar|Bottom Right[3]',
        'CalTar|Upper Right[3]',
        'CalTar|Lower Right[1]',
        'CalTar|Top[2]'
    ]
    writer = csv.DictWriter(csvfileOpen, fieldnames=fieldnames, dialect=csv.excel,  delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, escapechar='\\')
    writer.writeheader()

    #######################
    ChannelSetToAnalyze = 'mw'  # Radiometer data set to be used. TODO: We could use all of them with a loop.  
    TotalSecondsToAnalyzeVector = [19, 14]  # Time for calibration and data processing files, respectevily. 
    AngularAverageDegrees = 1  # Mimimum resolution 0.0225, one motor sample per sample.
    sixtyHertzFilter = [True, True]  # The 60 Hz filter for the calibration and the data files, respectevil. Only has effect for the SND channels. -- **Recomendation: Do not change it** .
    #####################################################################
    ##
    ## Setting display figure parameters
    ##    
    plt.rc('xtick', labelsize=18)  # xlabel tics size
    plt.rc('ytick', labelsize=18)  # ylabel tics size
    font = {'family': 'serif', 'size': 14}  # general font type and size
    plt.rc('font', **font)
    ## Markers for displaying 
    REFdisplayArray = ['b', 'b', 'b', 'b','b', 'b', 'b', 'b','b', 'b', 'b', 'b','b', 'b.', 'b.', 'b.']
    ANTdisplayArray = ['r+', 'r+', 'r+', 'r+','r+', 'r+', 'r+', 'r+','r+', 'r+', 'r+', 'r+','r+', 'r+', 'r+', 'r+']
    markers = ['.','o','*']
    #######################
    ## Lables not used any more. 
    ## ---- To be eventually deleted
    #sixtyHertzFilterLabel = ['Filter ON', 'Filter ON'] 
    #label=['Stiffener ON', 'Stiffener OFF']

    #######################
    ## Flags for display 
    ##
    PlotAngularImage = True
    PlotTimeImage = True
    PlotTipingCurve = False
    ImageInterpolation = False
    DisplayAuxData = True
    PlotTime = True
    #######################
    #######################
    #######################
    ## Currently these sets of variables are not used. 
    ##
    ## ---- To be integrated to the RadiometerAux file. 
    ##
    #ChannelSetToAnalyzeVector=['SND']
    #ScansArray={'ALL', 'EVEN', 'ODD'}
    #SamplesArray={'ALL', 'EVEN', 'ODD'}
    Scans = 'ALL'
    Samples = 'ALL'
    #####################################################################


    for CalIndex in range(len(filepaths)):
        print(filenamerootVector)
        filenameroot_vector = [filepaths[CalIndex].stem]
        print(filenameroot_vector)
        plt.close("all")

        
        indexVector = 0  # AGW This was a for loop that only did one loop at this value.
        # I think the idea was to have 0 and 1 do different things (like debugging), and then 1 was removed.
        TotalSecondsToAnalyze = TotalSecondsToAnalyzeVector[indexVector]
        filenameroot = filenameroot_vector[indexVector]
        #####################################################################
        ChSetdpa = DataProcessor(filepaths[CalIndex],ChannelSetToAnalyze)
        Tint = ChSetdpa.Conf.RadIntegrationTime[ChannelSetToAnalyze]
        ChannelsToAnalyze = ChSetdpa.ChannelstoBeExplored
        Tint_seconds = Tint/1000
        finish = int(TotalSecondsToAnalyze/Tint_seconds)
        #####################################################################
        #####################################################################
        # Initializing some values for each dataprocessor file. 
        NumberOfChannels = np.max(ChSetdpa.ChannelstoBeExplored) + 1
        cVector = np.zeros(NumberOfChannels)
        TrecVector = np.zeros(NumberOfChannels)
        Tzenith = np.zeros(NumberOfChannels)
        MeanArray = np.zeros(NumberOfChannels)
        stdArray = np.zeros(NumberOfChannels)
        DeltaTmeasured = np.zeros(NumberOfChannels)
        DeltaTheoretical = np.zeros(NumberOfChannels)      

        # AGW Below was held behind 'DisplayAuxData' condition, but contains necessary assignments.
        plt.rc('ytick', labelsize=30)
        fig1 = ChSetdpa.Thermistors.printthermistors(filenameroot)
        figfilename = os.path.join(ChSetdpa.pathfordata,filenameroot+'_AllThermistors.png')
        fig1.set_size_inches(80, 60)
        fig1.savefig(figfilename, dpi = 100)
        plt.rc('xtick', labelsize=18) 
        plt.rc('ytick', labelsize=18)    
    
        fig2, Time, TemperatureArray = ChSetdpa.Thermistors.PlotThermistorByName(['ABEB Bloc','OpBench MMW-MCMs','CalTar|Center[2]'], filenameroot)
        figfilename = os.path.join(ChSetdpa.pathfordata,filenameroot+'_SpecificThermistors.png')
        fig2.savefig(figfilename)  
        
        fig2=ChSetdpa.GPSIMU.printEulerAngles(filenameroot)
        figfilename = os.path.join(ChSetdpa.pathfordata,filenameroot+'_GPSAttitude.png')
        fig2.savefig(figfilename)  
    
        fig3=ChSetdpa.GPSIMU.printAltitude(filenameroot)
        figfilename = os.path.join(ChSetdpa.pathfordata,filenameroot+'_GPSAltitude.png')
        fig3.savefig(figfilename)  
        
        fig4=ChSetdpa.GPSIMU.printTrajectory(filenameroot)
        figfilename = os.path.join(ChSetdpa.pathfordata,filenameroot+'_GPSTrajectory.png')
        fig4.savefig(figfilename)

        Position = ChSetdpa.GPSIMU.GPS_Position[0]
        GPSTime = ChSetdpa.GPSIMU.GPS_GPSTime[0]
            
        
        for x in ChannelsToAnalyze: 
            ##########################################################################################              
            ### Converting the acquired datastream from counts to voltages for the X channel 
            ###    
            RadiometricDataVolts = ChSetdpa.Radiometer.fromCountstoV(ChSetdpa.Radiometer.Counts[:,x])
            ##########################################################################################              
            ### Selecting the data types filtering by datatype. Not used here currently, but used in other parts of the code
            ### 
            start = 0
            ReferenceIndex, IndexDirty, RNumberOfChannelseferenceIndexBooolean = ChSetdpa.Radiometer.calculateIndex(0, finish, start)
            AntennaIndex, IndexDirty, AntennaIndexBooolean = ChSetdpa.Radiometer.calculateIndex(1, finish, start)
            NS1Index, IndexDirty, AntennaIndexBoooleanX = ChSetdpa.Radiometer.calculateIndex(3, finish, start)
            NS1NS2Index, IndexDirty, AntennaIndexBoooleanX = ChSetdpa.Radiometer.calculateIndex(5, finish, start)
            NS1NS2NS3Index, IndexDirty, AntennaIndexBoooleanX = ChSetdpa.Radiometer.calculateIndex(9, finish, start)        
            
            plt.figure(111110)
            timeoffset=start*Tint_seconds
            plt.plot(timeoffset+AntennaIndex*Tint_seconds, RadiometricDataVolts[AntennaIndex], 'r.', ms=10, label='Code0 - ANT '+ChSetdpa.TitleArray[x])
            plt.plot(timeoffset+ReferenceIndex*Tint_seconds, RadiometricDataVolts[ReferenceIndex], 'b.',ms=10, label='Code1 - REF '+ChSetdpa.TitleArray[x])
            plt.plot(timeoffset+NS1Index*Tint_seconds, RadiometricDataVolts[NS1Index], 'k.', ms=10, label='Code3 - NS1 + REF ' +ChSetdpa.TitleArray[x])
            plt.plot(timeoffset+NS1NS2Index*Tint_seconds, RadiometricDataVolts[NS1NS2Index], 'g.',ms=10, label='Code5 - NS2 + REF ' +ChSetdpa.TitleArray[x])  
            plt.plot(timeoffset+NS1NS2NS3Index*Tint_seconds, RadiometricDataVolts[NS1NS2NS3Index], 'c.',ms=10, label='Code4 - NS2 + ANT' +ChSetdpa.TitleArray[x])
            plt.plot(timeoffset+NS1NS2NS3Index*Tint_seconds, RadiometricDataVolts[NS1NS2NS3Index], 'y.',ms=10, label='Code2 - NS1 + ANT' +ChSetdpa.TitleArray[x])     
            plt.grid(True)            
            plt.show(block=False) 

            
            ##########################################################################################              
            ## Calculationg the antenna normalized voltages for each motor postion for each motor scan
            ##
            StartAngle = 0  # Starting angular value, do not change unless you know what you are doing
            StopAngle = StartAngle + 360  # Ending angular value, do not change unless you know what you are doing
            SixtyHertzhSNDFiler = sixtyHertzFilter[0]  # Used in case we are processing the SND subset, to filter out the 60 Hz coupling. 
            ##
            ## Assigning volts to each angular resultion (AngularAverageDegrees) for each scan from StartAngle to StopAngle for TotalSecondsToAnalyze
            ## Also, if required, applying the 60 Hz filter. 
            mnANTelevationAngle, stdANTelevationAngle, motorposition, ANTtimematrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.ANTValue, x, finish, RadiometricDataVolts, AngularAverageDegrees, StartAngle, StopAngle, TotalSecondsToAnalyze, ChannelSetToAnalyze, SixtyHertzhSNDFiler) 
            mnREFelevationAngle, stdREFelevationAngle, REFmotorposition, REFtimematrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.REFValue, x, finish, RadiometricDataVolts, AngularAverageDegrees, StartAngle, StopAngle, TotalSecondsToAnalyze, ChannelSetToAnalyze, SixtyHertzhSNDFiler) 
            mnNS1elevationAngle, stdNS1elevationAngle, NS1motorposition, NS1timematrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.NS1Value, x, finish, RadiometricDataVolts, AngularAverageDegrees, StartAngle, StopAngle, TotalSecondsToAnalyze, ChannelSetToAnalyze, SixtyHertzhSNDFiler) 
            mnNS2elevationAngle, stdNS2elevationAngle, NS2motorposition, NS2timematrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.NS2Value, x, finish, RadiometricDataVolts, AngularAverageDegrees, StartAngle, StopAngle, TotalSecondsToAnalyze, ChannelSetToAnalyze, SixtyHertzhSNDFiler) 
            mnNS3elevationAngle, stdNS3elevationAngle, NS3motorposition, NS3timematrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.NS3Value, x, finish, RadiometricDataVolts, AngularAverageDegrees, StartAngle, StopAngle, TotalSecondsToAnalyze, ChannelSetToAnalyze, SixtyHertzhSNDFiler) 
        
            ##
            ## Using the calibration target angular position for selecting the volts to normalize the signal. 
            ##
            MotorAngletoStart = int(0/AngularAverageDegrees)
            MotorAngletoEnd = int(10/AngularAverageDegrees)
            print("Normalizing Data with CalTarget Values, Angles:", MotorAngletoStart, '-', MotorAngletoEnd)
            C = mnANTelevationAngle[MotorAngletoStart:MotorAngletoEnd]
            mdat = np.ma.masked_array(C, C == 0)
            AntennaValueWhenLookingCalTarget = np.mean(mdat, axis=0)  
            NormalizedDataElevationAngle = mnANTelevationAngle / AntennaValueWhenLookingCalTarget   
            NormalizedRefElevationAngle = mnREFelevationAngle / AntennaValueWhenLookingCalTarget
            NormalizedNS1ElevationAngle = mnNS1elevationAngle / AntennaValueWhenLookingCalTarget
            NormalizedNS2ElevationAngle = mnNS2elevationAngle / AntennaValueWhenLookingCalTarget
            NormalizedNS3ElevationAngle = mnNS3elevationAngle / AntennaValueWhenLookingCalTarget               

            ##########################################################################################    
            ## From Motor Angle to Elevation angle
            ## Here the np.mean(motorposition,axis=1)assumption is that when the motor is looking to the target is -pi/2
            ## Calculationg the antenna mean normalized voltages for each motor postion for all the motor scans
            ##
            Normalizedmotorposition, ElevationCorrectedAngle, NadirPosition, ZenithPosition, cooordenateNadirOriginalMotor, cooordenateZenithOriginalMotor, AzimuthCorrectedAngle = ChSetdpa.Radiometer.fromMotorAngleToElevationAngle(motorposition, ChSetdpa.AntennaAngularOffset, AngularAverageDegrees, ChSetdpa.TitleArray[x], markers[indexVector], indexVector, x, False) 
            NadirPosition[0] = 53
            
            mdat = np.ma.masked_array(mnANTelevationAngle,mnANTelevationAngle==0)
            AntDataMotorPosition = np.mean(mdat, axis=1)
            CalTargetValues = np.mean(AntDataMotorPosition[MotorAngletoStart:MotorAngletoEnd])
            NormalizedAntDataMotorPosition = AntDataMotorPosition / CalTargetValues
            TcoldValue = AntDataMotorPosition[NadirPosition]
            ThotValue = AntDataMotorPosition[ZenithPosition]
            ## Calculationg the reference mean normalized voltages for each motor postion for all the motor scans
            ##             
            REFNormalizedmotorposition, REFElevationCorrectedAngle, REFNadirPosition, REFZenithPosition, REFcooordenateNadirOriginalMotor, REFcooordenateZenithOriginalMotor, AzimuthCorrectedAngle = ChSetdpa.Radiometer.fromMotorAngleToElevationAngle(REFmotorposition, ChSetdpa.AntennaAngularOffset, AngularAverageDegrees, ChSetdpa.TitleArray[x], markers[indexVector], indexVector, x, False) 
            mdat = np.ma.masked_array(mnREFelevationAngle, mnREFelevationAngle==0)
            RefDataMotorPosition = np.mean(mdat, axis=1)
            NormalizedRefDataMotorPosition = RefDataMotorPosition / CalTargetValues
            ## Calculationg the reference mean normalized voltages for each motor postion for all the motor scans
            ##
            NS1Normalizedmotorposition, NS1ElevationCorrectedAngle, NS1NadirPosition, NS1ZenithPosition, NS1cooordenateNadirOriginalMotor, NS1cooordenateZenithOriginalMoto, NS1AzimuthCorrectedAngler=ChSetdpa.Radiometer.fromMotorAngleToElevationAngle(NS1motorposition, ChSetdpa.AntennaAngularOffset, AngularAverageDegrees, ChSetdpa.TitleArray[x], markers[indexVector], indexVector, x, False) 
            mdat = np.ma.masked_array(mnNS1elevationAngle, mnNS1elevationAngle==0)
            NS1DataMotorPosition = np.mean(mdat, axis=1)
            NormalizedNS1DataMotorPosition = NS1DataMotorPosition / CalTargetValues                     
            ## Calculationg the reference mean normalized voltages for each motor postion for all the motor scans
            ##
            NS2Normalizedmotorposition, NS2ElevationCorrectedAngle, NS2NadirPosition, NS2ZenithPosition, NS2cooordenateNadirOriginalMotor, NS2cooordenateZenithOriginalMotor, NS2AzimuthCorrectedAngler=ChSetdpa.Radiometer.fromMotorAngleToElevationAngle(NS2motorposition, ChSetdpa.AntennaAngularOffset, AngularAverageDegrees, ChSetdpa.TitleArray[x], markers[indexVector], indexVector, x, False) 
            mdat = np.ma.masked_array(mnNS2elevationAngle,mnNS2elevationAngle==0)
            NS2DataMotorPosition = np.mean(mdat, axis=1)
            NormalizedNS2DataMotorPosition = NS2DataMotorPosition / CalTargetValues
            ## Calculationg the reference mean normalized voltages for each motor postion for all the motor scans
            ##
            NS3Normalizedmotorposition, NS3ElevationCorrectedAngle, NS3NadirPosition, NS3ZenithPosition, NS3cooordenateNadirOriginalMotor, NS3cooordenateZenithOriginalMotor, NS3AzimuthCorrectedAngler=ChSetdpa.Radiometer.fromMotorAngleToElevationAngle(NS3motorposition, ChSetdpa.AntennaAngularOffset, AngularAverageDegrees, ChSetdpa.TitleArray[x], markers[indexVector], indexVector, x, False) 
            mdat = np.ma.masked_array(mnNS3elevationAngle, mnNS3elevationAngle==0)
            NS3DataMotorPosition = np.mean(mdat, axis=1)
            NormalizedNS3DataMotorPosition = NS3DataMotorPosition / CalTargetValues              
            
            ER1 = NS1DataMotorPosition - AntDataMotorPosition
            ER2 = NS2DataMotorPosition - AntDataMotorPosition
            ER3 = NS3DataMotorPosition - AntDataMotorPosition 
            
            
            print("------------------------------")  
            print("Tnadir-Tzenith: ", TcoldValue, ThotValue, " Normalized Volts")
            ##########################################################################################
            ## Gathering information for radiometric calibration from the first file or calibrating the data iwth the second file
            ##
            ## Correcting the LN2 Boiling temperature for altitude, higher than 2000m then use 77 K
            if Position[2] > 2000:
                TphysicalLN2 = 77
            else:
                TphysicalLN2 = 80
                    
                c = (ChSetdpa.Radiometer.CalTargetTemperature - TphysicalLN2) / (ThotValue - TcoldValue)  # LN2 ideal temperature is 77 K but we consider 80.
                Trec = c * ThotValue - ChSetdpa.Radiometer.CalTargetTemperature  # Important note, we are using Normalized Voltage so Vhot=1, if different this needs to be changed.
                cVector[x] = c
                TrecVector[x] = Trec
                ENR_NS1 = np.mean(ER1*cVector[x])
                ENR_NS2 = np.mean(ER2*cVector[x])  
                ENR_NS3 = np.mean(ER3*cVector[x]) 
                VNS1 = np.mean(ER1)
                VNS2 = np.mean(ER2)
                VNS3 = np.mean(ER3)

                # AGW Removed 'channelsettoanalyze == 'mw'' for all, since that's the defined case for this file.
                if x < 4:
                    PhysicalReceiverTempChannels = ChSetdpa.Radiometer.PhysicalReceiverTempChannels[ChannelSetToAnalyze][0]
                    PhysicalNS1824TempChannels = ChSetdpa.Radiometer.PhysicalNSTempChannels[ChannelSetToAnalyze][0][0]
                    PhysicalNS1834TempChannels = ChSetdpa.Radiometer.PhysicalNSTempChannels[ChannelSetToAnalyze][0][1]
                elif NewDataFlag:
                    PhysicalReceiverTempChannels = ChSetdpa.Radiometer.PhysicalReceiverTempChannels[ChannelSetToAnalyze][0]
                    PhysicalNS1824TempChannels = ChSetdpa.Radiometer.PhysicalNSTempChannels[ChannelSetToAnalyze][1][0]
                    PhysicalNS1834TempChannels = ChSetdpa.Radiometer.PhysicalNSTempChannels[ChannelSetToAnalyze][1][1]  
                else:
                    PhysicalReceiverTempChannels = ChSetdpa.Radiometer.PhysicalReceiverTempChannels[ChannelSetToAnalyze][1]
                    PhysicalNS1824TempChannels = ChSetdpa.Radiometer.PhysicalNSTempChannels[ChannelSetToAnalyze][1][0]
                    PhysicalNS1834TempChannels = ChSetdpa.Radiometer.PhysicalNSTempChannels[ChannelSetToAnalyze][1][1]                              
        
                MW_NS_1824Temperature = ChSetdpa.Thermistors.GetMeanTemperatureChannels(PhysicalNS1824TempChannels) 
                MW_NS_34Temperature = ChSetdpa.Thermistors.GetMeanTemperatureChannels(PhysicalNS1834TempChannels)
                
                RadiometerTemperature = ChSetdpa.Thermistors.GetMeanTemperatureChannels(PhysicalReceiverTempChannels)
                HornTemp = ChSetdpa.Thermistors.GetMeanTemperatureChannels([2])[0]
                OptBenchTemp = ChSetdpa.Thermistors.GetMeanTemperatureChannels([2])[0]
                PBackBottomTemp = ChSetdpa.Thermistors.GetMeanTemperatureChannels([26])[0]
                PBackMiddleTemp = ChSetdpa.Thermistors.GetMeanTemperatureChannels([27])[0]
                PBacktopTemp = ChSetdpa.Thermistors.GetMeanTemperatureChannels([28])[0]       
                
                print("------------------------------")
                print("Main Calibration values for: ", ChSetdpa.TitleArray[x])
                print("ThotVAlue-TcoldValue", ThotValue, TcoldValue, " [Volt]")
                print("--- Calibration Coefficient:", c[0] , " [Kelvin/Volt]")
                print("--- Treceiver:",  Trec[0], " [Kelvin]")
                print("--- Lat/Lon", Position[0], '/', Position[1])
                print("--- Altitude:", Position[2], ' m')
                print("--- External Temperature:", np.mean(TemperatureArray[2,:]), ' C')
                print("--- Horn, Opt. Bench, Paraboloid-{Bottom, Middle, Top} Temperatures:", HornTemp, OptBenchTemp, '-{', PBackBottomTemp, ',', PBackMiddleTemp, ',', PBacktopTemp, '} C')
                print("--- Radiometer Temperature:", RadiometerTemperature[0], "+/-", RadiometerTemperature[1], ' C')
                print("--- mean TNS1, TNS2, TNS3:", ENR_NS1, ' | ', ENR_NS2, ' | ', ENR_NS3, " K")
                print("--- std  TNS1, TNS2, TNS3:", np.std(ER1*cVector[x]), ' | ', np.std(ER2*cVector[x]), ' | ', np.std(ER3*cVector[x]), " K")
                print("--- mean VNS1, VNS2, VNS3:", VNS1, ' | ', VNS2, ' | ', VNS3, " volts")
                print("---  NS Temperature: 18/24|34:", MW_NS_1824Temperature[0], ' | ', MW_NS_34Temperature[0])
                                
                writer.writerow({
                    'FileName':filenameroot,
                    'GPSTime':GPSTime[0],
                    'Radiometer Set':ChannelSetToAnalyze,
                    'Channel':x,
                    'Cal. Coef.':c[0],
                    'Trec': Trec[0],
                    'Altitude':Position[2],
                    'Lat.':Position[0],
                    'Lon.':Position[1],
                    'Ext Temp.':np.mean(TemperatureArray[2,:]),
                    'Rad. Temp.':RadiometerTemperature[0],
                    'std Rad. Temp.':RadiometerTemperature[1],
                    'TNS1':ENR_NS1,
                    'TNS2':ENR_NS2,
                    'TNS3':ENR_NS3,
                    'VNS1':VNS1,
                    'VNS2':VNS2,
                    'VNS3':VNS3,
                    'Temp. MW-NS-18/24': MW_NS_1824Temperature[0],
                    'Temp. MW-NS-34':MW_NS_34Temperature[0],
                    'VAMB':ThotValue[0],
                    'VLN2':TcoldValue[0],
                    'Vref': np.mean(RefDataMotorPosition),  
                    'stdVref': np.std(RefDataMotorPosition),
                    'CalTarget Temp.':ChSetdpa.Radiometer.CalTargetTemperature-272.15,
                    'Horn Temp.':HornTemp,
                    'OpticalBench Temp.':OptBenchTemp,
                    'Back Paraboloid Bottom Temp.':PBackBottomTemp, 
                    'Back Paraboloid Middle Temp.':PBackMiddleTemp,
                    'Back Paraboloid Top Temp.':PBacktopTemp,
                    'CalTar|Upper Left[1]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([8])[0],
                    'CalTar|Lower Left[3]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([9])[0],
                    'CalTar|Center[2]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([10])[0],
                    'CalTar|Bottom Left[1]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([11])[0],
                    'CalTar|Bottom Right[3]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([12])[0],
                    'CalTar|Upper Right[3]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([13])[0], 
                    'CalTar|Lower Right[1]':ChSetdpa.Thermistors.GetMeanTemperatureChannels([14])[0], 
                    'CalTar|Top[2]' :ChSetdpa.Thermistors.GetMeanTemperatureChannels([15])[0]
                })      


                
                fig = plt.figure(300+x+indexVector*10)
                ax = fig.add_subplot(111)
                Ta = AntDataMotorPosition * cVector[x] - TrecVector[x]
                plt.plot(ElevationCorrectedAngle,Ta , 'b.')
                plt.plot(NS1ElevationCorrectedAngle, ER1*cVector[x], label='ENR NS1 '+ ChSetdpa.TitleArray[x], color='Black', marker=markers[indexVector])    
                plt.plot(NS2ElevationCorrectedAngle, ER2*cVector[x], label='ENR NS2 '+ ChSetdpa.TitleArray[x], color='Green', marker=markers[indexVector])    
                plt.plot(NS3ElevationCorrectedAngle, ER3*cVector[x], label='ENR NS3 '+ ChSetdpa.TitleArray[x], color='Yellow', marker=markers[indexVector])    
                plt.show(block=False)
                plt.grid(True)
                plt.legend(loc='best', shadow=True)
                fig.suptitle(filenameroot+'ElevationCorrected__Channel_'+ChSetdpa.TitleArray[x], fontsize=10)
                figfilename = os.path.join(ChSetdpa.pathfordata,filenameroot+'_ElevationCorrected_Channel_'+ChSetdpa.TitleArray[x]+'.png')
                fig.savefig(figfilename)
            
    csvfileOpen.close()
    time.sleep(3)
    print( open(pathfordata, 'rt').read())
    print('FINISHED CAL STEP 1!')   

