# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 16:22:15 2014

@author: xbosch
"""
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path
import time

from GeneralPaths import CVS_FILES_DATA_BASE_PATH, L0b_DATA_PROCESSED_PATH, CALVERSION
from Reader.Core.DataProcessorAux import DataProcessor
from Reader.Core.L1aFileAux import CreateAntennaTempeartureFile
from Reader.Core.OpenCVSBatchFile import OpenCVSBatchFile



class P_L1a():
    def __init__(
            self,
            CVSfilenamebatch,
            TotalSecondsToAnalyzeVector,
            AngularAverageDegrees,
            CalibrationFilesNames,
            ChannelSetToAnalyzeVector,
            sixtyHertzFilter,
            Flags
    ):
        ##############################################################################
        ##############################################################################
        self.TotalSecondsToAnalyzeVector = TotalSecondsToAnalyzeVector  # Time for calibration and data processing files, respectevily.
        self.AngularAverageDegrees = AngularAverageDegrees  # Mimimum resolution 0.0225, one motor sample per sample.
        self.sixtyHertzFilter = sixtyHertzFilter  # The 60 Hz filter for the calibration and the data files, respectevil. Only has effect for the SND channels. -- **Recomendation: Do not change it** .
        ##################################################################### 
        ## Markers for displaying 
        self.REFdisplayArray = ['b', 'b', 'b', 'b','b', 'b', 'b', 'b','b', 'b', 'b', 'b','b', 'b.', 'b.', 'b.']
        self.ANTdisplayArray = ['r+', 'r+', 'r+', 'r+','r+', 'r+', 'r+', 'r+','r+', 'r+', 'r+', 'r+','r+', 'r+', 'r+', 'r+']
        self.markers = ['.', 'o', '*']
        self.ChannelSetToAnalyzeVector = ChannelSetToAnalyzeVector
        self.CalibrationFilesNames = CalibrationFilesNames
        self.CalTarMaxAngleVector = {'mw':5, 'mmw':15, 'snd':15}
        #######################
        #######################
        ## Flags for display 
        self.PlotAngularImage = Flags["PlotAngularImage"]
        self.PlotTipingCurve = Flags["PlotTipingCurve"]  # Not used
        self.DisplayAuxData = Flags["DisplayAuxData"]
        self.ExtendedData = Flags["ExtendedData"]
        ##############################################################################
        ##############################################################################
        self.CVSBatchFiles = OpenCVSBatchFile(CVSfilenamebatch)
        self.pathfordata = self.CVSBatchFiles.pathfordata


    def run(self):
        np.seterr(invalid='ignore')
        plt.rc('xtick', labelsize=18)  # xlabel tics size
        plt.rc('ytick', labelsize=18)  # ylabel tics size
        plt.rc('font', family='serif', size=14)

        for CalIndex in range(len(self.CVSBatchFiles.filenamerootVector)-1):
            filenameroot = self.CVSBatchFiles.filenamerootVector[CalIndex]
            CATF = CreateAntennaTempeartureFile(filenameroot)
            
            StartTime = time.time()
            self.PlotAuxDataTrigger = True
            for ChannelSetToAnalyze in self.ChannelSetToAnalyzeVector:
                ##################################################################### 
                CalibrationcvsFileName = self.CalibrationFilesNames[ChannelSetToAnalyze]
                ChSetdpa = DataProcessor(Path(filenameroot), ChannelSetToAnalyze)
                Tint = ChSetdpa.Conf.RadIntegrationTime[ChannelSetToAnalyze]
                ChSetdpa.Radiometer.OpenCalCoefsFile(CalibrationcvsFileName) 
                #####################################################################           
                TotalSecondsToAnalyze = self.TotalSecondsToAnalyzeVector[0]
                ChannelsToAnalyze = ChSetdpa.ChannelstoBeExplored
                Tint_seconds = Tint/1000
                start = 0
                finish = int(TotalSecondsToAnalyze/Tint_seconds)
                #####################################################################
                if self.DisplayAuxData and self.PlotAuxDataTrigger: 
                    ## We plot it once per file. 
                    self.PlotAuxDataTrigger=False
                    plt.rc('ytick', labelsize=30)
                    fig1=ChSetdpa.Thermistors.printthermistors(filenameroot)
                    figfilename =os.path.join(ChSetdpa.pathfordata,filenameroot+'_AllThermistors.png')
                    fig1.set_size_inches(40, 30)
                    fig1.savefig(figfilename, dpi = 100)
                    plt.rc('xtick', labelsize=18) 
                    plt.rc('ytick', labelsize=18)    
                
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
                    #####################################################################         
                    plt.close("all")
                    ##########################################################################################              
                    ### Converting the acquired datastream from counts to voltages for the X channel 
                    ###    
                    RadiometricDataVolts = ChSetdpa.Radiometer.fromCountstoV(ChSetdpa.Radiometer.Counts[:,x])
                    ##########################################################################################                 
                    ##########################################################################################              
                    ## Calculationg the antenna normalized voltages for each motor postion for each motor scan
                    ##
                    StartAngle = 0  # Starting angular value, do not change unless you know what you are doing
                    StopAngle = StartAngle + 360  # Ending angular value, do not change unless you know what you are doing
                    SixtyHertzhSNDFiler = self.sixtyHertzFilter[0]  # Used when we are processing the SND subset, to filter out the 60 Hz coupling. 
                    ##########################################################################################                 
                    ##########################################################################################   
                    ### The output of this funciton is a NxM matrix, where M is the scan number and N is the angular position within the scan. 
                    ## All radiomtric data sets have antenna measuremetns
                    mnANTelevationAngle, stdANTelevationAngle, ANTMotorPositionMatrix, ANTTimeMatrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.ANTValueArray[ChannelSetToAnalyze], x, finish, RadiometricDataVolts, self.AngularAverageDegrees,StartAngle,StopAngle,TotalSecondsToAnalyze,ChannelSetToAnalyze,SixtyHertzhSNDFiler) 
                    DataTypeIndexANT,IndexDirty,DataTypeIndexBooolean = ChSetdpa.Radiometer.calculateIndex(ChSetdpa.Radiometer.ANTValueArray[ChannelSetToAnalyze], finish, start=0)
                    ## MMW and MW have noise sources and matched load
                    if ChannelSetToAnalyze =='mmw' or ChannelSetToAnalyze == 'mw':
                        mnREFelevationAngle, stdREFelevationAngle, REFMotorPositionMatrix, REFTimeMatrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.REFValueArray[ChannelSetToAnalyze], x, finish, RadiometricDataVolts, self.AngularAverageDegrees,StartAngle,StopAngle,TotalSecondsToAnalyze,ChannelSetToAnalyze,SixtyHertzhSNDFiler) 
                        mnNS1elevationAngle, stdNS1elevationAngle, NS1MotorPositionMatrix, NS1TimeMatrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.NS1ValueArray[ChannelSetToAnalyze], x, finish, RadiometricDataVolts, self.AngularAverageDegrees,StartAngle,StopAngle,TotalSecondsToAnalyze,ChannelSetToAnalyze,SixtyHertzhSNDFiler)
                        mnNS2elevationAngle, stdNS2elevationAngle, NS2MotorPositionMatrix, NS2TimeMatrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.NS2ValueArray[ChannelSetToAnalyze], x, finish, RadiometricDataVolts, self.AngularAverageDegrees,StartAngle,StopAngle,TotalSecondsToAnalyze,ChannelSetToAnalyze,SixtyHertzhSNDFiler) 
                        mnNS3elevationAngle, stdNS3elevationAngle, NS3MotorPositionMatrix, NS3TimeMatrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.NS3ValueArray[ChannelSetToAnalyze], x, finish, RadiometricDataVolts, self.AngularAverageDegrees,StartAngle,StopAngle,TotalSecondsToAnalyze,ChannelSetToAnalyze,SixtyHertzhSNDFiler)             
                        DataTypeIndexREF,IndexDirty,DataTypeIndexBooolean = ChSetdpa.Radiometer.calculateIndex(ChSetdpa.Radiometer.REFValueArray[ChannelSetToAnalyze], finish, start=0)
                        DataTypeIndexNS1,IndexDirty,DataTypeIndexBooolean = ChSetdpa.Radiometer.calculateIndex(ChSetdpa.Radiometer.NS1ValueArray[ChannelSetToAnalyze], finish, start=0)
                        DataTypeIndexNS2,IndexDirty,DataTypeIndexBooolean = ChSetdpa.Radiometer.calculateIndex(ChSetdpa.Radiometer.NS2ValueArray[ChannelSetToAnalyze], finish, start=0)
                        DataTypeIndexNS3,IndexDirty,DataTypeIndexBooolean = ChSetdpa.Radiometer.calculateIndex(ChSetdpa.Radiometer.NS3ValueArray[ChannelSetToAnalyze], finish, start=0)
                        ## Only MMW have a fourth noise source
                        if ChannelSetToAnalyze == 'mmw':
                            mnNS4elevationAngle, stdNS4elevationAngle, NS4MotorPositionMatrix, NS4TimeMatrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.NS4ValueArray[ChannelSetToAnalyze], x, finish, RadiometricDataVolts, self.AngularAverageDegrees,StartAngle,StopAngle,TotalSecondsToAnalyze,ChannelSetToAnalyze,SixtyHertzhSNDFiler)
                            DataTypeIndexNS4,IndexDirty,DataTypeIndexBooolean = ChSetdpa.Radiometer.calculateIndex(ChSetdpa.Radiometer.NS4ValueArray[ChannelSetToAnalyze], finish, start=0)
                    else:        
                        mnREFelevationAngle, stdREFelevationAngle, REFMotorPositionMatrix, REFTimeMatrix = ChSetdpa.Radiometer.AngularAveraging_Time(ChSetdpa.Radiometer.REFValueArray[ChannelSetToAnalyze], x, finish, RadiometricDataVolts, self.AngularAverageDegrees,StartAngle,StopAngle,TotalSecondsToAnalyze,ChannelSetToAnalyze,SixtyHertzhSNDFiler) 
                        mnREFelevationAngle = np.zeros_like(mnANTelevationAngle)

                    ##########################################################################################
                    ### This function calculates the true course of the vector pointing of the antenna. The output of this function consist of two signals:
                    ### 1. ANTTimeAveragedMotorPossition, a vector of N possitions, an average of the antenna value on the time domain for each angular position within the scan.
                    ### 2. ANTtimevector, a vector of M possitions, the CPU acquisition time for each scann
                    ANTTimeAveragedMotorPossition, ANTtimevector = ChSetdpa.Radiometer.calculateTrueCourse(ANTMotorPositionMatrix,ANTTimeMatrix)
                    L = len(ChSetdpa.Radiometer.BeamNadirAngle)
                    NScanns = len(ANTtimevector)          
                    ### Calculating the position of scene and calibration target.                    
                    SceneMaxAngle = int(40/self.AngularAverageDegrees)

                    CalTarMaxAngle = int(self.CalTarMaxAngleVector[ChannelSetToAnalyze]/self.AngularAverageDegrees)
                    SceneIndex = np.mod(np.array(range(ChSetdpa.Radiometer.nadirIndex-SceneMaxAngle, ChSetdpa.Radiometer.nadirIndex+SceneMaxAngle))+L, L)
                    CalTargetIndex = np.mod(np.array(range(ChSetdpa.Radiometer.zenithIndex-CalTarMaxAngle, ChSetdpa.Radiometer.zenithIndex+CalTarMaxAngle))+L, L)
                    CalTargetIndex = np.array(range(200,220))
                    ## Getting the temperature channels for the radiomtric set
                    PhysicalReceiverTempChannels = ChSetdpa.Radiometer.PhysicalReceiverTempChannels[ChannelSetToAnalyze][int(x/4)]
                    print("Number of Scanns to be analyzed:", NScanns)
                    print('Nadir-Index:', ChSetdpa.Radiometer.nadirIndex, 'Zenith-Index', ChSetdpa.Radiometer.zenithIndex, ' Distance:', ChSetdpa.Radiometer.zenithIndex-ChSetdpa.Radiometer.nadirIndex, ' index possitions')
                    print("Temperature Channel:", PhysicalReceiverTempChannels) 
                    ###############################################################
                    ### Looking for holes into the NxM matrix, where M is the scan number and N is the angular position within the scan. 
                    ### Holes are filed with NaNs
                    NA = mnANTelevationAngle
                    Coordinates = np.where(NA==0.0)
                    NA[Coordinates[0], Coordinates[1]] = np.nan
                    NATA1 = np.zeros(NA.shape)
                    NATA2 = np.zeros(NA.shape)
                    Gref = np.zeros(NA.shape)     

                    SmoothingWindowSize = 40
                    if ChannelSetToAnalyze =='mmw':
                        #E1=ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS1elevationAngle, NS1TimeMatrix, mnREFelevationAngle, WindowSize=SmoothingWindowSize, verbose=False)
                        #E2=ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS2elevationAngle, NS2TimeMatrix, mnREFelevationAngle, WindowSize=SmoothingWindowSize, verbose=False)
                        #E3=ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS3elevationAngle, NS3TimeMatrix, mnANTelevationAngle, WindowSize=SmoothingWindowSize, verbose=False)
                        
                        #E4=ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS4elevationAngle, NS4TimeMatrix, mnANTelevationAngle, WindowSize=SmoothingWindowSize, verbose=False)  
                        #E1=ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS1elevationAngle, NS1TimeMatrix, np.zeros_like(mnREFelevationAngle), WindowSize=SmoothingWindowSize, verbose=False)
                       # E2=ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS2elevationAngle, NS2TimeMatrix, mnREFelevationAngle, WindowSize=SmoothingWindowSize, verbose=False)
                        #E3=ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS3elevationAngle, NS3TimeMatrix, np.zeros_like(mnREFelevationAngle), WindowSize=SmoothingWindowSize, verbose=False)
                        #E4=ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS4elevationAngle, NS4TimeMatrix, mnANTelevationAngle, WindowSize=SmoothingWindowSize, verbose=False) 
                        ERef=ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnREFelevationAngle, REFTimeMatrix, np.zeros_like(mnREFelevationAngle), WindowSize=SmoothingWindowSize, verbose=False)               
                        N1=np.zeros(mnANTelevationAngle.T.shape)
                        N2=np.ones(mnANTelevationAngle.T.shape)
                        '''
                        ### When MMW, who is who. Only two of the noise sources are meaninful, the other two are antenna or reference measurements.
                        if x==0 or x==3: 
                            #N3=E1                       ## Reference, no NS
                            N2=np.abs(E1)      ## Antenna side NS
                            #ANT_isolated=E3
                            N1=np.abs(E3)   ##N1                   ## Reference side NS
                        elif x==2:    
                            #N3=ERef #E2                       ## Reference, no NS
                            N2=np.abs(E1)                       ## Reference side NS
                            #ANT_isolated=E4
                            N1=np.abs(E3)                       ## Antenna side NS
                            '''

                    elif  ChannelSetToAnalyze == 'mw':
                        E1 = ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS1elevationAngle, NS1TimeMatrix, mnANTelevationAngle, WindowSize=SmoothingWindowSize, verbose=False)
                        E2 = ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS2elevationAngle, NS2TimeMatrix, mnANTelevationAngle, WindowSize=SmoothingWindowSize, verbose=False)
                        E3 = ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnNS3elevationAngle, NS3TimeMatrix, mnANTelevationAngle, WindowSize=SmoothingWindowSize, verbose=False)
                        ERef = ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnREFelevationAngle, REFTimeMatrix, np.zeros_like(mnREFelevationAngle), WindowSize=SmoothingWindowSize, verbose=False)               
                        ## defining noise source priority for MW, we will use the best one
                        N1 = E1
                        N2 = E2
                        N3 = E3
                    else:
                        N1 = np.zeros(mnANTelevationAngle.T.shape)
                        N2 = np.ones(mnANTelevationAngle.T.shape)
                        ERef = ChSetdpa.Radiometer.WindowingAndInterpolatingNS(mnREFelevationAngle, REFTimeMatrix, np.zeros_like(mnREFelevationAngle), WindowSize=SmoothingWindowSize, verbose=False)  

                    NDDR1 = N1/N2
                    NDDR2 = N1/N2

                    ##################################################################################################################################
                    ### Preparing the CALIBRATION
                    ### 1. Calculate the Dicke reference ration between when looing the scene and looking the calibration target. 
                    ### 2. Filter and resample the thermistors involved in the calibration, i.e: radiomter receivers and calibration target receivers. 
                    ################################################          
                    ### Calculating the  Dicke reference values when looking the scene and when looking the calibration target 
                    AntennaValueWhenLookingCalTargetEachScan = ChSetdpa.Radiometer.CalculateScannAverageValues(mnANTelevationAngle[CalTargetIndex], NScanns)
                    if ChannelSetToAnalyze == 'snd':
                        ReferenceValueforEachScan = np.zeros_like(AntennaValueWhenLookingCalTargetEachScan) 
                        Vref_CalTarEachScan = np.zeros_like(AntennaValueWhenLookingCalTargetEachScan) 
                        Vref_SceneEachScan = np.zeros_like(AntennaValueWhenLookingCalTargetEachScan) 
                    else:
                        ReferenceValueforEachScan = ChSetdpa.Radiometer.CalculateScannAverageValues(mnREFelevationAngle, NScanns)
                        Vref_CalTarEachScan = ChSetdpa.Radiometer.CalculateScannAverageValues(mnREFelevationAngle[CalTargetIndex], NScanns)
                        Vref_SceneEachScan = ChSetdpa.Radiometer.CalculateScannAverageValues(mnREFelevationAngle[SceneIndex], NScanns)       
                    ### Filtering and resampling the thermistors involved in the calibration, i.e: the receiver and calibration target thermistors.           
                    if len(ChSetdpa.Thermistors.ThermistorFilteredAndResampled) == 0:
                        ChSetdpa.Thermistors.thermistorsFilterAndResampling(ANTtimevector, WindowLength=5, Verbose=False)
                        ChSetdpa.Thermistors.thermistorsResamplingAverage(PhysicalReceiverTempChannels, ChSetdpa.Radiometer.CalibratonTargetChannels, Verbose=False)    
                    
                    #####################################################################################################################################
                    ### CALIBRATION Version 1. 
                    ### 1. Calculate Trec and CalCoef values, Trec from a LN2 time series with temperature dependence
                    ### 2. Remove stripping form the Dikie ratio calculated before
                    #####################################################################################################################################                 
                    ### A and B coefficients are calculated from LN2 series, which are sentitive to physical temperature.
                    StrippingCorrection = False
                    CalibrationVersion = 1
                    Emissivity = 0.9798 
                    ### Trec is based on an empirical model 
                    Trec = (float(ChSetdpa.Radiometer.A[x])*np.array(ChSetdpa.Thermistors.ThermistorResampledAndAveraged)+float(ChSetdpa.Radiometer.B[x]))
                    ### Calculated each motor revolution based on hte Calibration Target voltage and temperature measurements and Trec
                    CalCoef = (np.array(Emissivity*(ChSetdpa.Thermistors.CalibratonTargetChannelsResampledSpatiallyAveraged+273.15)+Trec))/AntennaValueWhenLookingCalTargetEachScan
                    ### Removing stripping form the Dikie ratio calculated before and calibrating the ANTENNA MEASUREMENTS
                    

                    if StrippingCorrection and ChannelSetToAnalyze != 'snd':
                        print('Stripping Correction:', StrippingCorrection, ' + Calibration version inproved')
                        for itr in range(NScanns):           
                            NATA1[:,itr] = NA[:,itr]*CalCoef[itr]*Vref_CalTarEachScan[itr]/Vref_SceneEachScan[itr]-Trec[itr]
                    else:
                        print('Stripping Correction: FALSE + First Calibration version')   
                        print("Dimensions check: ", NA.shape, N1.shape)          
                        for itr in range(NScanns):
                            G1 = np.mean(N1[itr,CalTargetIndex], axis=0)/N1[itr,:]
                            G2 = np.mean(N2[itr,CalTargetIndex], axis=0)/N2[itr,:]
                            Gref[:,itr] = np.mean(ERef[itr,CalTargetIndex], axis=0)/ERef[itr,:]
                            G1T = (np.mean(N1[itr,CalTargetIndex], axis=0))/(N1[itr,:])
                            ScannElements = G1.shape

                            NATA1[:,itr] = NA[:,itr]*CalCoef[itr]-Trec[itr]

                            for itr2 in range(ScannElements[0]):
                                NATA2[itr2,itr] = NA[itr2,itr]*(Gref[itr2,itr]*CalCoef[itr])-Trec[itr]
                    
                    NATAD = NATA1-NATA2          
                    ND = np.mean(N1[:-1,CalTargetIndex], axis=1)

                    ### Calculating Measurement uncertainty for each channel acording to ISO GUM uncertainty type B
                    RVcal = AntennaValueWhenLookingCalTargetEachScan
                    RVa = NA[ChSetdpa.Radiometer.nadirIndex,:len(AntennaValueWhenLookingCalTargetEachScan)]

                    REn = N1[:len(AntennaValueWhenLookingCalTargetEachScan),ChSetdpa.Radiometer.nadirIndex]
                    REnCalTar = np.mean(N1[:len(AntennaValueWhenLookingCalTargetEachScan),CalTargetIndex], axis=1)
                    
                    WindowSize = 5
                    PolyOrder = 3
                    Va = RVa-ChSetdpa.Radiometer.savitzky_golay(RVa, WindowSize, PolyOrder, deriv=0)    
                    Vcal = RVcal-ChSetdpa.Radiometer.savitzky_golay(RVcal, WindowSize, PolyOrder, deriv=0) 
                    
                    WindowSize = 5
                    PolyOrder = 3
                    En = REn-ChSetdpa.Radiometer.runningMeanFast(REn, WindowSize) 
                    EnCalTar = REnCalTar-ChSetdpa.Radiometer.runningMeanFast(REnCalTar, WindowSize) 
                    RatioEn = REnCalTar/REn
                    
                    Tcal = np.array(Emissivity*(ChSetdpa.Thermistors.CalibratonTargetChannelsResampledSpatiallyAveraged)+273.15)
                    
                    T1_1 = np.std(Va)*np.mean((Tcal+Trec)/RVcal)
                    T2_1 = np.std(Tcal)*1*np.mean(RVa/RVcal)
                    T3_1 = -np.std(Vcal)*1*np.mean(RVa*(Tcal+Trec)/(RVcal**2))
                    T4_1 = np.std(Trec)*1*np.mean((RVa/RVcal-1))
                    NEAT_1 = np.sqrt(T1_1**2+T2_1**2+T3_1**2+T4_1**2)
                    print("Uncertatinty measurement Calibration V1:", T1_1, T2_1, T3_1, T4_1, NEAT_1, "in Kelvin")
                    
                    T1_2 = T1_1*np.mean(RatioEn)
                    T2_2 = T2_1*np.mean(RatioEn)
                    T3_2 = T2_1*np.mean(RatioEn)
                    T4_2 = np.std(Trec)*1*np.mean((RVa/RVcal*np.mean(RatioEn)-1))
                    T5_2 = np.std(EnCalTar)/np.mean((Tcal+Trec)/(RVcal*REn))
                    T6_2 = -np.std(En)/np.mean( (Tcal+Trec)*REnCalTar/(RVcal*REn**2))
                    NEAT_2 = np.sqrt(T1_2**2+T2_2**2+T3_2**2+T4_2**2+T5_2**2+T6_2**2)
                    print("Uncertatinty measurement Calibration V2:", T1_2, T2_2, T3_2, T4_2, T5_2, T6_2, NEAT_2, "in Kelvin")

                    WindowSize=5
                    a2 = NATA2[ChSetdpa.Radiometer.nadirIndex,1:-1]
                    NoiseV2 = a2-ChSetdpa.Radiometer.runningMeanFast(a2, WindowSize) 
                    a1 = NATA1[ChSetdpa.Radiometer.nadirIndex,1:-1]
                    NoiseV1 = a1-ChSetdpa.Radiometer.runningMeanFast(a1, WindowSize)
                    print("Nadir stability v001:", np.mean(a1), np.std(a1), np.std(NoiseV1[3:-3]), np.mean(NoiseV1[3:-3]))  
                    print("Nadir stability v002:", np.mean(a2), np.std(a2), np.std(NoiseV2[3:-3]), np.mean(NoiseV2[3:-3]))

                    ### Ploting images
                    mdat = np.ma.masked_array(NATA1.T[:NScanns,:],np.isnan(NATA1.T[:NScanns,:]))
                    ChSetdpa.Radiometer.zmin = np.min(np.min(mdat))-5
                    ChSetdpa.Radiometer.zmax = np.max(np.max(mdat))+5
                    if self.PlotAngularImage:
                        plt.close("all")
                        ChSetdpa.Radiometer.AntDataVsScan(3000, x, NATA1, NScanns, self.AngularAverageDegrees, TotalSecondsToAnalyze,GeneralValues=False)

                    ### Substitituting NaNs for -99999, for practical purposes                   
                    NATA1[Coordinates[0],Coordinates[1]] = -99999
                    ### Calibrating the REFERENCE LOAD MEASUREMENTS
                    if ChannelSetToAnalyze == 'snd':
                        Tref = np.zeros(mnANTelevationAngle.shape[1])
                        Vref_CalTarEachScan = Tref
                        Vref_SceneEachScan = Tref           
                    else:
                        for itr in range(NScanns):
                            Tref = ReferenceValueforEachScan*CalCoef[itr]-Trec[itr]         

                    #####################################################################################################################################
                    ## Saving results into and HDF5 file
                    #####################################################################################################################################
                    print("Saving h5 file:")
                    ## If the file does not have navigation data, then insert it.
                    if not CATF.NavDataTable:
                         CATF.InsertNavData(ANTtimevector, ChSetdpa.GPSIMU)
                         CATF.InsertTempData(ChSetdpa.Thermistors) 
                    # Save the radiometric informatioin. 
                    NDDR2 = np.zeros_like(Trec)
                    NDDR1 = np.zeros_like(Trec)

                    if ChannelSetToAnalyze == 'mmw' and CALVERSION == 1 and x != 2:
                        RecAnt = NATA1.T
                        NEAT = NEAT_1
                    elif ChannelSetToAnalyze == 'mmw' and CALVERSION == 2:
                        if self.PlotAngularImage:
                            ChSetdpa.Radiometer.AntDataVsScan(30000, x, NATA2, NScanns, self.AngularAverageDegrees, TotalSecondsToAnalyze, GeneralValues=True)
                        RecAnt = NATA2.T
                        NEAT = NEAT_2
                    else: 
                        RecAnt = NATA1.T
                        NEAT = NEAT_1

                    CATF.InsertTable(ChannelSetToAnalyze, x, RecAnt, CalCoef, Trec, NDDR1, NDDR2, Tref, Vref_CalTarEachScan, Vref_SceneEachScan,  ANTTimeAveragedMotorPossition, ChSetdpa.Radiometer.truecourse_x, ChSetdpa.Radiometer.truecourse_y, ChSetdpa.Radiometer.truecourse_z, NEAT, ChSetdpa.Radiometer.motorInfo)
         
                    if self.ExtendedData:
                        C=mnANTelevationAngle
                        mdat = np.ma.masked_array(C, (C==0)|(C==np.nan))
                        AntennaValues = np.nanmean(mdat,axis=1) 
                        C = mnREFelevationAngle
                        mdat = np.ma.masked_array(C,(C==0)|(C==np.nan))
                        ReferenceValues = np.nanmean(mdat, axis=1) 
                        CalTargetVoltage = np.nanmean(AntennaValues[CalTargetIndex])
                        if ChannelSetToAnalyze == 'snd':
                            ChSetdpa.Radiometer.plotAntData(977, x, ANTTimeAveragedMotorPossition, AntennaValues, ChSetdpa.Radiometer.nadirIndex, ChSetdpa.Radiometer.zenithIndex,CalTargetVoltage, CalTargetIndex, self.AngularAverageDegrees, mnANTelevationAngle,ANTTimeMatrix) ###, NS1Values=[], NS3Values=[], NS4Values=[])
                        else:
                            ChSetdpa.Radiometer.plotAntData(977, x, ANTTimeAveragedMotorPossition, AntennaValues, ChSetdpa.Radiometer.nadirIndex, ChSetdpa.Radiometer.zenithIndex,CalTargetVoltage, CalTargetIndex, self.AngularAverageDegrees, mnANTelevationAngle,ANTTimeMatrix, ReferenceValues) ###, NS1Values=[], NS3Values=[], NS4Values=[])
                
            ElapsedTime = StartTime-time.time()
            print("Total Time Processing: " , filenameroot, ": ", ElapsedTime, " seconds")
            CATF.fileclose()



# if __name__ == "__main__":
#     print("This is a class, do not use it as a scipt")
    #--------------------------------------
    #CVSfilenamebatch_D7_01_10_SJR='SingleFile_2014_11_06__16_09_42__1of10_WCFC_Day3_SanJoaquinRiver'
    #CVSfilenamebatch_D7_02_10_SJR='SingleFile_2014_11_06__16_14_52__2of10_WCFC_Day3_SanJoaquinRiver'
    #CVSfilenamebatch_D7_03_14_LT='SingleFileTest_2014_11_12__12_33_50__3of14_WCFC_Day7_LakeTahoe'
    #CVSfilenamebatch_D7_04_14_LT='SingleFileTest_2014_11_12__12_38_50__4of14_WCFC_Day7_LakeTahoe'
    #CVSfilenamebatch_D7_10_14_LT='SingleFileTest_2014_11_12__13_08_56__10of14_WCFC_Day7_LakeTahoe'
    #CVSfilenamebatch_D7_06_14_LT='SingleFileTest_2014_11_12__12_48_53__6of14_WCFC_Day7_LakeTahoe'
    #CVSfilenamebatch_D7_07_14_LT='SingleFileTest_2014_11_12__12_53_53__7of14_WCFC_Day7_LakeTahoe'
    #CVSfilenamebatch_D7_01_14_LT='SingleFileTest_2014_11_12__12_23_41__1of14_WCFC_Day7_LakeTahoe'
    #TotalSecondsToAnalyzeVector=[300]   # Time for calibration and data processing files, respectevily. 
    #AngularAverageDegrees=1             # Mimimum resolution 0.0225, one motor sample per sample.
  
    #CVSfilenamebatch=CVSfilenamebatch_D7_03_14_LT

   # L1a = P_L1a(CVSfilenamebatch,TotalSecondsToAnalyzeVector, AngularAverageDegrees)
   # L1a.run()