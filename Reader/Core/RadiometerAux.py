import os, sys
import math
import numpy as np
import pylab as pl
#from ThermistorsAux import thermistors
import time
from scipy.optimize import minimize
import csv
#configfile='.\..\GeneralPaths.py'
# configfile='..\..\GeneralPaths.py'
#configfile='..\GeneralPaths.py'
# sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import CALIBRATION_PATH
from pylab import *

class radiometer:
       
    FromCtoK=273.15    
    #MotorOffset=3500   # in counts

    
    def __init__(self, h5file, RadiometricDataType, verbose=True, NearRealTime=False):
        

        ## Reading radiometric data
       # try:
        datasource='h5file.root.Radiometric_Data.%s_DATA'%RadiometricDataType.upper()
        print(datasource)
        data =eval(datasource)
        print("INFO: new instance of dataprocessor for ", datasource    )   

        self.pCounts=  np.array([x['Counts'] for x in data.iterrows()],'int16')
        self.pTimestamp=  np.array([x['Timestamp'] for x in data.iterrows()]).flatten()
        self.pSystemStatus= np.array( [x['SystemStatus'] for x in data.iterrows()],'int16').flatten()
        self.pMotorPosition= np.array( [x['MotorPosition'] for x in data.iterrows()],'int16').flatten()
        self.pSystemStatus_DIFF=np.transpose(np.diff(np.transpose(self.pSystemStatus)))
        self.pdiffZero=np.append([False, False, False],(self.pSystemStatus_DIFF==0))

        self.MotorStartingPoing=0 #11202
        # Calculating the motor step for each channel, depends on the integration time
        diffMotor=np.diff(self.pMotorPosition,axis=0) 
        mdat = np.ma.masked_array(diffMotor,diffMotor<-1000)
        self.detaMotorMean= np.mean(mdat,axis=0).flatten()
        self.detaMotorstd= np.std(mdat,axis=0).flatten()
        
        self.motorInfo="Mean step: ", self.detaMotorMean[0], " (",self.detaMotorMean[0]*360/16000,") and std: ", self.detaMotorstd[0], " (",self.detaMotorstd[0]*360/16000,")"
        print("Motor information ",  self.motorInfo )
        ScannPostionCorrectIndex=np.where((self.pMotorPosition<=self.MotorStartingPoing+self.detaMotorMean) & (self.pMotorPosition>=self.MotorStartingPoing-self.detaMotorMean))[0][0]  
        print("First Sample found at:", ScannPostionCorrectIndex, " samples")     
        #ScannPostionCorrectIndex=0

        self.Counts=self.pCounts[ScannPostionCorrectIndex:]
        print( "--------------------------", self.Counts.shape, self.pCounts.shape)
        self.Timestamp=  self.pTimestamp[ScannPostionCorrectIndex:]
        self.SystemStatus= self.pSystemStatus[ScannPostionCorrectIndex:]
        self.MotorPosition= self.pMotorPosition[ScannPostionCorrectIndex:]
        self.SystemStatus_DIFF=self.pSystemStatus_DIFF[ScannPostionCorrectIndex:]
        self.diffZero=self.pdiffZero[ScannPostionCorrectIndex:]

    
        self.ScannPostionCorrect=np.zeros(len(self.MotorPosition))
        self.ScannPostionCorrect[ScannPostionCorrectIndex:]=1

        self.zmin=0
        self.zmax=0
   
        #Some extra checks on the motor's data
        if not NearRealTime: 
            # try:
            self.WrongMotorPosition=[]
            self.MotorScannNumber=np.zeros(len(self.MotorPosition))
            #self.testMotorIntegrity()
            self.MotorScanNumber()
            self.MotorOffset=0 #7212 #11212+3*4000   
            #print 'Verify that this is the motor offset:', self.MotorOffset, ' in motor counts.'
            self.MotorPosition=np.mod(self.MotorPosition-self.MotorOffset, 16000).flatten()
            print( "Motor position max:", np.max( self.MotorPosition), " First motor position:", self.MotorPosition[0])
            # except:
            #      print( "WARNING: Something went wrong with the motor analysis. Please check it. ")
            #      print( "--> most probably the motor is not connected")
        
        #except:
        #    print "No ", RadiometricDataType, " radiometer data found!"           
        
        ## Reading thermistors data
        #try:
        
        ############################################### 
        ## These values are updated from DataProcessor, do not change or update them                     
        self.Conf=[] 
        self.RadiometricDataType=[]
        self.ChannelsNames=[]
        self.Thermistors=[]
        self.AntennaAngularOffset=0
        self.filenameroot=' '
        self.pathfordata=''          
        ###############################################                      
        ##print "Each MCM has his own thermistor so it needs to be calibrated accordingly!!!!!!!!!!!!!!!!!!!!!!"
        ## Defining the thermistors each radiometer thermistors            
        self.PhysicalReceiverTempChannels={'mw': [[17,18],[17,18]],'mmw':[[35],[0],[33],[33]], 'snd':[[39],[39],[39],[39], [38], [38], [38], [38],[39],[39],[39],[39],[38], [38], [38], [38],] }   ## Internal AMR Channels + External AMR Channels ## 90 GHz, 130 GHz, NC, 168 GHz
        self.PhysicalNSTempChannels={'mw': [[[23],[24]], [[21],[22]]],'mmw':[[35],[0],[33],[33]], 'snd':[] }   ## Internal AMR Channels + External AMR Channels ## 90 GHz, 130 GHz, NC, 168 GHz
        self.CalibratonTargetChannels=range(8,16) 
        # Defining the systems' states,values based on their position on the SystemStatus Signal
        self.NS1bitvalue=2
        self.NS2bitvalue=4
        self.NS3bitvalue=8       
        self.RFOFF=16
        ## Defining the systems' states, it slightly differs for mw and for mmw, snd only has RF ON/OFF 
        self.ANTValueArray={'mw':1,'mmw':0, 'snd':0 }
        self.REFValueArray={'mw':0,'mmw':1, 'snd':0 }     
        self.NS1ValueArray={'mw':3,'mmw':3, 'snd':0 }
        self.NS2ValueArray={'mw':5,'mmw':5, 'snd':0 }
        self.NS3ValueArray={'mw':9,'mmw':4, 'snd':0 }
        self.NS4ValueArray={'mw':0,'mmw':2, 'snd':0 } 
        ######
        self.ANTValue=self.ANTValueArray[RadiometricDataType]
        self.REFValue=self.REFValueArray[RadiometricDataType]    
        self.NS1Value=self.NS1ValueArray[RadiometricDataType]  
        self.NS2Value=self.NS2ValueArray[RadiometricDataType]  
        self.NS3Value=self.NS3ValueArray[RadiometricDataType]  
        self.NS4Value=self.NS4ValueArray[RadiometricDataType]  

        ##################################
        self.A=[]
        self.B=[]
        ##################################
        self.zenithIndex=0
        self.nadirIndex=0
        self.truecourse_x=[]
        self.truecourse_y=[]
        self.truecourse_z=[]
        self.TimeMatrix = []
        self.BeamNadirAngle= []

        return None

    def UpdateConfigParameters(self):
        print( "Radiometric Type:", self.RadiometricDataType )
        self.Tint=eval("self.Conf.RadIntegrationTime['"+ self.RadiometricDataType +"']")*0.001
        self.SamplesPerSecond=int(1/self.Tint)
        print( 'Tint:', self.Tint, ' -- i.e.:',self.SamplesPerSecond ,' samples per second')
        self.CalTargetTemperature, self.CalTargetTemperatureSTD, ArrayMeanTemperature, ArrayStdTemperature, minTemp, maxTemp, diffTemp=self.Thermistors.GetMeanTemperatureChannels(self.CalibratonTargetChannels)
        self.CalTargetTemperature=self.CalTargetTemperature+self.FromCtoK         
        print( "Calibration Target Temperature:", self.CalTargetTemperature, "Standard deviation across the CalTarget:",self.CalTargetTemperatureSTD, "Min. Max and Diff. Temp:",minTemp, maxTemp, diffTemp, '- all in Kelvin. ')
        return None       

    def OpenCalCoefsFile(self, filepath):
        # cvsfilenamerootpath=os.path.join(CALIBRATION_PATH,  cvsFileName+'.csv')
        csvfileOpen = open(filepath, 'r')
        
        spamreader = csv.reader(csvfileOpen, delimiter=',')
        Channel=[];Avector=[];Bvector=[]
        for row in spamreader:
            Channel.append(row[0])
            Avector.append(row[1])
            Bvector.append(row[2])
        self.A=Avector[1:]
        self.B=Bvector[1:]
        return None
    
    def fromCountstoV(self,counts):
        MaximumInputVoltageOftheADC=4.096
        NumberofBits=14
        NumberofSteps=(2**NumberofBits)-1
        Volts=MaximumInputVoltageOftheADC*(NumberofSteps-counts)/NumberofSteps
        return Volts
        
    def MotorScanNumber(self):
        NewRotationCounts=-1000
        NewRotationDiffs=(np.diff(self.MotorPosition,axis=0)<=NewRotationCounts)
        NewRotation=np.append([0], np.where(NewRotationDiffs==True)[0])
        #print NewRotation, np.diff(NewRotation)
        for i in range(0,len(NewRotation)-1):        
            self.MotorScannNumber[NewRotation[i]:NewRotation[i+1]]=i
           #for x in range(NewRotation[i],NewRotation[i+1]):
           #     self.MotorScannNumber[x]=i 
        self.MotorScannNumber[NewRotation[i+1]+1:]=i+1
        print(  "Found " + repr(self.MotorScannNumber[-1])+ " scans on the data file.")
        #fig=pl.figure(3340)        
        #pl.plot(self.MotorScannNumber,'.')
        #pl.show()
        return None
        
    def calculateIndex(self, DataType, finish, start=0):
        preDataIndex=np.append([False, False],(self.SystemStatus==DataType))
        DataIndexBoolean=np.logical_and(preDataIndex[start:finish-1],self.diffZero[start:finish-1])
        DataIndex=np.where(DataIndexBoolean[start:finish-1])[0]
        DataIndexDirty=np.where(preDataIndex[start:finish-1])[0]
        return DataIndex, DataIndexDirty, DataIndexBoolean
    
    def calculateIndexAccordinglyToMotorPosition(self, DataType, finish, MotorPostitionStart,MotorPostitionStop):
        # Looking for the right MotorPositions
        start=0  
        if MotorPostitionStop<MotorPostitionStart:
            # print "Look at me the Start is smaller that the stop... bye!!!! --> START:",MotorPostitionStart,"STOP:",MotorPostitionStop
            preMotorPositionIndexBoolean=np.logical_and(self.MotorPosition>MotorPostitionStop,self.MotorPosition<MotorPostitionStart)
            MotorPositionIndexBoolean = (preMotorPositionIndexBoolean is False)
        else:
            MotorPositionIndexBoolean = np.logical_and(self.MotorPosition>MotorPostitionStart,self.MotorPosition<MotorPostitionStop)
  
        MotorPositionIndex = np.where(MotorPositionIndexBoolean)
        DataTypeIndex,IndexDirty,DataTypeIndexBooolean=self.calculateIndex(DataType,finish,start)
        # Interjecting DataType positions with MotorPositions
        EndofArray=len(MotorPositionIndexBoolean[:finish-1])
        DataTypeInteceptedWithMotorPositon=np.where(np.logical_and(DataTypeIndexBooolean[:EndofArray],MotorPositionIndexBoolean[:finish-1]))[0]    
        return DataTypeInteceptedWithMotorPositon, MotorPositionIndex[:finish]


    def  CalculateScannAverageValues(self, C, NScanns):

        mdat = np.ma.masked_array(C,C==0)
        pSignalAveragedperScann= np.mean(mdat,axis=0)
        A=pSignalAveragedperScann[~pSignalAveragedperScann.mask].data
        ## Dealing with non complete scans at the end of the acquisition
        lenS=A.shape
        if NScanns> lenS[0]:
            oo=NScanns-lenS[0]
            for x in range(0,oo):
                SignalAveragedperScann= np.append(A,A[-1])
        elif NScanns< lenS[0]:
            SignalAveragedperScann=A[:NScanns]           
        else: 
           SignalAveragedperScann=A
        return    SignalAveragedperScann


    def plotAntData(self,fignum, ChannelNumber, ANTTimeAveragedMotorPossition,  AntennaValues, nadirIndex ,zenithIndex, CalTargetVoltage, CalTargetIndex, AngularAverageDegrees, mnANTelevationAngle, ANTTimeMatrix, ReferenceValues=[], NS1Values=[],  NS2Values=[], NS3Values=[], NS4Values=[]):

        #fignum=200
        fig0=pl.figure(fignum)
        ax = fig0.add_subplot(111)
        #print AntennaValues
        #print  nadirIndex, AntennaValues[nadirIndex], ANTTimeAveragedMotorPossition[nadirIndex]*180/np.pi
        pl.plot(ANTTimeAveragedMotorPossition*180/np.pi, AntennaValues, label='Antenna Volts',linestyle='None', marker='.')
        pl.plot(ANTTimeAveragedMotorPossition[nadirIndex]*180/np.pi, AntennaValues[nadirIndex], label='Nadir', marker='o',  markersize=5)
        pl.plot(ANTTimeAveragedMotorPossition[zenithIndex]*180/np.pi, AntennaValues[zenithIndex], label='Zenith', marker='*',  markersize=5)
        pl.plot(ANTTimeAveragedMotorPossition[CalTargetIndex]*180/np.pi ,np.ones(len(CalTargetIndex))*CalTargetVoltage, label='CalTarget', color='red', marker='o',  linestyle='None', markersize=5)
        #pl.plot(ChSetdpa.Radiometer.BeamNadirAngle.T[:,100], label='Azimuth Correction 100', marker='o',  markersize=5)
        pl.ylabel('Measured Volt')
        pl.xlabel('Motor Pointing Angle')            
        title='Antenna Volt versus Motor Position ' + self.ChannelsNames[ChannelNumber] + ' GHz'
        pl.title(title)
        pl.grid()       
        pl.legend(loc = 'best',shadow = True)
        fig0.suptitle(self.filenameroot[:-3], fontsize=5)                 
        pl.show(block=False)
        figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig0.savefig(figfilename)
        
        fignum=fignum+1
        fig0=pl.figure(fignum)
        ax = fig0.add_subplot(111)     
        AngularRange2Plot=int(60/AngularAverageDegrees)
        L=len(self.BeamNadirAngle)
        UpIndex=np.mod(np.array(range(nadirIndex, nadirIndex+AngularRange2Plot)), L)
        DnIndex=np.mod(np.array(range(nadirIndex-AngularRange2Plot, nadirIndex)), L)
        UpX=(ANTTimeAveragedMotorPossition[UpIndex]*180/np.pi-ANTTimeAveragedMotorPossition[nadirIndex]*180/np.pi)
        DnX=-(ANTTimeAveragedMotorPossition[DnIndex]*180/np.pi-ANTTimeAveragedMotorPossition[nadirIndex]*180/np.pi)
        pl.plot(UpX, AntennaValues[UpIndex], label='Nadir-Up', marker='o',  markersize=5)
        pl.plot(DnX, AntennaValues[DnIndex], label='Nadir-Dn', marker='o',  markersize=5)
        pl.ylabel('Measured Volt')
        pl.xlabel('Motor Pointing Angle')            
        title='Antenna Volt UpDown Comparison ' + self.ChannelsNames[ChannelNumber] + ' GHz'
        pl.title(title)
        pl.grid()       
        pl.legend(loc = 'best',shadow = True)
        fig0.suptitle(self.filenameroot[:-3], fontsize=5)                 
        pl.show(block=False)
        figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig0.savefig(figfilename)     

        fignum=fignum+1
        fig0=pl.figure(fignum)  
        pl.plot(ANTTimeAveragedMotorPossition*180/np.pi, AntennaValues, 'r', label='Antenna', linestyle='None', marker='o')
        if  len(ReferenceValues)>0:
            pl.plot(ANTTimeAveragedMotorPossition*180/np.pi, ReferenceValues, 'b', label='Reference', linestyle='None', marker='o')   
        if  len(NS1Values)>0:
            pl.plot( ANTTimeAveragedMotorPossition*180/np.pi, NS1Values, 'g', label='NS1', linestyle='None', marker='o')   
        if  len(NS2Values)>0:
            pl.plot(ANTTimeAveragedMotorPossition*180/np.pi, NS2Values, 'y', label='NS2', linestyle='None', marker='o')  
        if  len(NS3Values)>0:
            pl.plot(ANTTimeAveragedMotorPossition*180/np.pi, NS3Values, 'm', label='NS3', linestyle='None', marker='o')   
        if  len(NS4Values)>0:
            pl.plot(ANTTimeAveragedMotorPossition*180/np.pi, NS4Values, 'r', label='NS4', linestyle='None', marker='o')   
        pl.ylabel('Measured Volt')
        pl.xlabel('Motor Pointing Angle')            
        title='Radiometer Averaged Voltges ' + self.ChannelsNames[ChannelNumber]+ ' GHz'
        pl.title(title)
        pl.grid()       
        pl.legend(loc = 'best',shadow = True)
        fig0.suptitle(self.filenameroot[:-3], fontsize=5)                 
        pl.show(block=False)
        figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig0.savefig(figfilename)     

        fignum=fignum+1
        fig0=pl.figure(fignum)  
        pl.plot(ANTTimeMatrix[:,0]-ANTTimeMatrix[0,0], mnANTelevationAngle[:,0], 'b', label='Voltage', linestyle='None', marker='o')
        pl.plot(ANTTimeMatrix[0,0]-ANTTimeMatrix[0,0], mnANTelevationAngle[0,0], 'g', label='First Element', linestyle='None', marker='o')
        pl.plot(ANTTimeMatrix[-1,0]-ANTTimeMatrix[0,0], mnANTelevationAngle[-1,0], 'r', label='Last Element', linestyle='None', marker='o')
        pl.plot(ANTTimeMatrix[:,1]-ANTTimeMatrix[0,0], mnANTelevationAngle[:,1], 'b', label='Voltage 2', linestyle='None', marker='o')
        pl.plot(ANTTimeMatrix[0,1]-ANTTimeMatrix[0,0], mnANTelevationAngle[0,1], 'g', label='First Element 2', linestyle='None', marker='o')
        pl.plot(ANTTimeMatrix[-1,1]-ANTTimeMatrix[0,0], mnANTelevationAngle[-1,1], 'r', label='Last Element 2', linestyle='None', marker='o')
        pl.ylabel('Antenna Volts')
        pl.xlabel('Acquisition Timee')            
        title='Antenna Volts vs Acquisition Time ' + self.ChannelsNames[ChannelNumber] + ' GHz'
        pl.title(title)
        pl.grid()       
        #pl.legend(loc = 'best',shadow = True)
        fig0.suptitle(self.filenameroot[:-3], fontsize=5)                 
        pl.show(block=False)
        figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig0.savefig(figfilename)  
        return

    def AntDataVsScan(self,fignum, ChannelNumber, NATA2, NScanns, AngularAverageDegrees, TotalSecondsToAnalyze, GeneralValues=False, PlotNameSufix=''):
        
        ##############################################################################################################################################
        L=len(self.BeamNadirAngle)
        SwathAngle=45
        ExtendedSceneIndex=np.mod(np.array(range(self.nadirIndex-int(SwathAngle/AngularAverageDegrees), self.nadirIndex+int(SwathAngle/AngularAverageDegrees)))+L, L)
        data=NATA2.T

        fignum=fignum+1
        fig = pl.figure(fignum)
        ax = fig.add_subplot(111)
        mdat = np.ma.masked_array(data[:NScanns,:],np.isnan(data[:NScanns,:]))
        zmin=np.min(np.min(mdat))-5 #
        zmax=np.max(np.max(mdat))+5 #
        if GeneralValues==True:
            zmin=self.zmin
            zmax=self.zmax        
        cax = ax.imshow(data[:NScanns,:].T, cmap=cm.jet, vmin=zmin, vmax=zmax, extent=[0,TotalSecondsToAnalyze,0,360])  #130            
        fig.colorbar(cax).set_label('Antenna Temperature [K]', fontsize=12) 
        pl.xlabel('Scan Number')
        pl.ylabel('Nadir Angle')
        pl.grid()
        pl.show(block=False) 
        fig.suptitle( self.filenameroot[:-3] +'__Channel_'+self.ChannelsNames[ChannelNumber], fontsize=10)
        figfilename =os.path.join(self.pathfordata, str(fignum) +'_'+self.filenameroot[:-3]+'__MotorVsTime_Channel_'+ self.ChannelsNames[ChannelNumber] +PlotNameSufix+'.png')
        fig.savefig(figfilename)

        fignum=fignum+1
        fig = pl.figure(fignum)
        ax = fig.add_subplot(111)
        mdat = np.ma.masked_array(data[:NScanns,ExtendedSceneIndex],np.isnan(data[:NScanns,ExtendedSceneIndex]))
        zmin=np.min(np.min(mdat))-5 #
        zmax=np.max(np.max(mdat))+5 #
        if GeneralValues==True:
            zmin=self.zmin
            zmax=self.zmax
        #cax = ax.imshow(data[:NScanns,ExtendedSceneIndex].T, cmap=cm.jet, vmin=zmin, vmax=zmax, extent=[0,TotalSecondsToAnalyze,-SwathAngle,SwathAngle])  #130
        cax = ax.imshow(data[:NScanns,ExtendedSceneIndex].T, cmap=cm.jet, vmin=0, vmax=310, extent=[0,TotalSecondsToAnalyze,-SwathAngle,SwathAngle])  #130

        fig.colorbar(cax).set_label('Antenna Temperature [K]', fontsize=12) 
        pl.xlabel('Scan Number')
        pl.ylabel('Nadir Angle')
        pl.grid()
        pl.show(block=False) 
        fig.suptitle(self.filenameroot[:-3]+'__Channel_'+self.ChannelsNames[ChannelNumber]+' min: '+ str(np.amin(data))+' Max: '+str(np.amax(data)), fontsize=10)
        figfilename =os.path.join(self.pathfordata, str(fignum) +'_'+ self.filenameroot[:-3]+'__MotorVsTime_Channel_'+ self.ChannelsNames[ChannelNumber] +PlotNameSufix+'.png')
        fig.savefig(figfilename)   
        return None

    def PlotSignalSpectrum(self, ChannelNumber, Signal, SixtyHertzFilter=[]):
        fignum=4444
        flim=self.SamplesPerSecond/2.
       # print flim, TotalSeconds, len(Signal)
        faxis=np.linspace(-flim, flim, len(Signal))
        fig0=pl.figure(fignum)  
        pl.plot(faxis, np.log10(np.abs(np.fft.fftshift(np.fft.fft(Signal**2)))), color='black')
        if len(SixtyHertzFilter)>0:
            pl.plot(faxis, np.log10(np.fft.fftshift(np.abs(np.multiply(SixtyHertzFilter,np.fft.fft(Signal**2))))), color='red') 
        pl.xlabel('Frequency [Hz]')
        pl.ylabel('Power density [dB]')            
        title='Signal Spectrum for ' + self.ChannelsNames[ChannelNumber] + ' GHz'
        pl.ylim([-3, 10])
        pl.title(title)
        pl.grid()       
        fig0.suptitle(self.filenameroot[:-3], fontsize=5)                 
        #pl.show(block=False)
        pl.show(block=False)
        figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig0.savefig(figfilename)
        return  

    ## Used for calculating the FFT efficiently in AngularAveraging_Time
    def get_next_prime_factor(self, n):
        if n % 2 == 0:
            return 2

        # Not 'good' [also] checking non-prime numbers I guess?
        # But the alternative, creating a list of prime numbers,
        # wouldn't it be more demanding? Process of creating it.
        for x in range(3, int(math.ceil(math.sqrt(n)) + 1), 2):
            if n % x == 0:
                return x
        return int(n)

    ## Used for calculating the FFT efficiently in AngularAveraging_Time        
    def prime_factorize(self, n):
        factors = []
        number = math.fabs(n)

        while number > 1:
            factor = self.get_next_prime_factor(number)
            factors.append(factor)
            number /= factor

        if n < -1: # If we'd check for < 0, -1 would give us trouble
            factors[0] = -factors[0]

        return np.array(factors) 

    def fromMotorAngleToElevationAngle(
        self,
        motorposition,
        AntennaAngularOffset,
        AngularAverageDegrees,
        Title,
        markerSty,
        indexVector,
        x,
        plotVervose=True
    ):
        ##########################################################################################    
        ## From Motor Angle to Elevation angle
        ## Here the np.mean(motorposition,axis=1)assumption is that when the motor is looking to the target is -pi/2
        ##
        Normalizedmotorposition= np.mean(motorposition,axis=1)*(2*np.pi/16000) + 18*np.pi/180# Converting motor positions to angles
        ElevationCorrectedAngle=np.arcsin(-np.cos(Normalizedmotorposition)*np.sin(Normalizedmotorposition)*np.sin(AntennaAngularOffset)+np.sin(Normalizedmotorposition)*np.cos(AntennaAngularOffset))*(180/np.pi) 
        AzimuthCorrectedAngle= np.arcsin(np.cos(Normalizedmotorposition)*np.sin(AntennaAngularOffset))
        NadirPosition= np.where(ElevationCorrectedAngle==np.max(ElevationCorrectedAngle))[0]
        ZenithPosition=np.where(ElevationCorrectedAngle==np.min(ElevationCorrectedAngle))[0]
        cooordenateNadirOriginalMotor=int(180/np.pi*Normalizedmotorposition[NadirPosition])
        cooordenateZenithOriginalMotor=int(180/np.pi*Normalizedmotorposition[ZenithPosition])              
        ##########################################################################################                
        print( "------------------------------")
        print( "Angle of the Motor and Elevation Angle Information" )                 
        print( 'First motor position:', Normalizedmotorposition[0]*180/np.pi, ' Last motor position: ', Normalizedmotorposition[-1]*180/np.pi)
        print( "------------------------------"  ) 
        print( "Corrected Elevation-> Nadir:", NadirPosition," Zenith:", ZenithPosition, " Angular distance:",(ZenithPosition-NadirPosition)/AngularAverageDegrees)
        print( "Motor Position-> Nadir: ", cooordenateNadirOriginalMotor," Zenith:", cooordenateZenithOriginalMotor, " Angular distance:" ,(cooordenateZenithOriginalMotor-cooordenateNadirOriginalMotor)/AngularAverageDegrees)
        print( "Motor Initial Angular Position:", Normalizedmotorposition[0]*180/np.pi, ElevationCorrectedAngle[0]  )           
        print( "------------------------------"   )

        return (
            Normalizedmotorposition,
            ElevationCorrectedAngle,
            NadirPosition,
            ZenithPosition,
            cooordenateNadirOriginalMotor,
            cooordenateZenithOriginalMotor,
            180/np.pi*AzimuthCorrectedAngle
        )
                           

    def AngularAveraging_Time(
        self,
        DataType,
        ChannelNumber,
        finish,
        Signal,
        AngularAverageDegrees,
        StartAngle,
        StopAngle,
        SecondsToAnalyze,
        Channel,
        SixtyHertzhSNDFiler
    ):
        
        print( "Processing:", self.RadiometricDataType, ' - Channel:',self.ChannelsNames[ChannelNumber], ' Data Type:', DataType, '-',self.filenameroot)
        aStartAngle=StartAngle  # the motor has a offset of 20 degrees  
        aStopAngle=StopAngle
        #MotorZeroDegrees=self.MotorOffset # 0 degrees is when looking at the cal target
        AngularAverage=np.floor((AngularAverageDegrees*16000/360))
        Upto=int(np.floor((aStopAngle-aStartAngle)/(AngularAverage*360/16000)))
        ElevationAngles=range(0, Upto)
        print( "----> Upto: %s, angular Average in samples: %s, in degrees: %s effective: %s, calculating %s points"%(Upto*AngularAverage*360/16000, AngularAverage, AngularAverageDegrees,AngularAverage*360/16000, len(ElevationAngles)))


        # start=0
        # DataTypeIndex, IndexDirty, DataTypeIndexBooolean=self.calculateIndex(DataType,finish,start)
        # figure(55678)
        # t=0.2e-3
        # x=range(0,DataTypeIndex[-1]) 
        # x_not_nan=DataTypeIndex
        # y_not_nan=Signal[DataTypeIndex]
        # NSInterp_COC=interp(x,x_not_nan,y_not_nan) 
        # #pl.plot(t*np.array(x), NSInterp_COC, 'r')
        # #pl.plot(t*np.array(x), NSInterp_COC, 'r.')       
        # pl.plot(t*DataTypeIndex, Signal[DataTypeIndex], '.')
        # pl.grid()
        # from scipy import signal
        # fs=1/t
        # print fs
        # f, Pxx_den = signal.periodogram(NSInterp_COC, fs, 'flattop', scaling='spectrum')
        # pl.figure(98675)
        # pl.semilogy(f, Pxx_den)
        # pl.show()

        OneSecondinSamples=self.SamplesPerSecond
        ## Filtering the 60 Hz noise
        
        if SixtyHertzhSNDFiler==True and Channel=='snd' :
            # This is correct because there is no Tref for snd or anything similar.
            t1=time.time()
            ##
            ## Making sure that the singal can be devided by 2, otherwise the FFT takes forever
            ## By doing that it changes from 20 minutes for the FFT to 0.5 seconds. 
            ## 
            if np.mod(len(Signal),2)==1:
                ODD=True
                L=len(Signal)+1 
                Signalb=np.append(Signal, np.mean(Signal))
            else: 
                ODD=False
                L=len(Signal)
                Signalb=Signal
            print( L, ODD, len(Signalb))

            ## Making sure that there is no pime number bigger than 1000 
            ## in the factorization of the lenght of the signal. Otherwise the 
            ## FFT algorithm slows down exponentially
            factorresult=self.prime_factorize(L) 
            it=0
            print( it, L, factorresult, any(factorresult>1000), factorresult>1000)
            while (any(factorresult>1000)):
                Signalb=np.append(Signalb, np.mean(Signalb))
                L=len(Signalb)
                factorresult=self.prime_factorize(L)  
                it=it+1
                print( it, L, factorresult, any(factorresult>1000), factorresult>1000)
            print( "After the prime arrangement:", it, L, ODD, len(Signalb))

            SixtyHertzFilter=np.ones(len(Signalb))
            ### This needs to be calculated according to OneSecondinSamples
            LowFrequencySixtyHamonics=[60, 120, 180, 240, 300.2, 420, 940, 880, 820, 760, 699.8, 580]
            for f in LowFrequencySixtyHamonics:
                poss_ini=int((f-0.17)*len(Signalb)/OneSecondinSamples)
                poss_end=int((f+0.17)*len(Signalb)/OneSecondinSamples)
                poss=range(poss_ini,poss_end)
                SixtyHertzFilter[poss]=0
            print( "60 Hz Filter is going to be aplied")
            TotalSeconds=len(Signalb)/OneSecondinSamples
            FFTSignal=np.fft.fft(Signalb)
            MultFilterSignal=np.multiply(SixtyHertzFilter,FFTSignal)
            Signal=np.abs(np.fft.ifft(MultFilterSignal)) 
            self.PlotSignalSpectrum(ChannelNumber, Signal, SixtyHertzFilter)            
            t3 = time.time()
            print("Elapsed time with the FFT of the 60 Hz filter is: ",  t3-t1 )

        print( "------------------------------"   )     

        TotalLength=SecondsToAnalyze           
        Offset=self.MotorStartingPoing
        
        pTimeAngleAveragedMotorposition= np.nan*np.ones((Upto,SecondsToAnalyze+1))
        pTimeMatrix=np.nan*np.ones((Upto,SecondsToAnalyze+1))
        pmnDataElevationAngle=np.nan*np.ones((Upto,SecondsToAnalyze+1))
        pstdDataElevationAngle=np.nan*np.ones((Upto,SecondsToAnalyze+1)) 

        
        t1=time.time()

        for x in ElevationAngles:
            aMotorStart=(Offset-AngularAverage)%16000  
            aMotorStop=(Offset)%16000
            if aMotorStop-aMotorStart<0:
                aMotorStop=16000-10
                pIndex=True
            else:
                pIndex=False

            IndexAccordingToMotorPosition, MotorLookingAbsorbentIndex=self.calculateIndexAccordinglyToMotorPosition(DataType, finish, aMotorStart, aMotorStop)                     
            PositionsBeingEvaluated=self.MotorScannNumber[IndexAccordingToMotorPosition]
            pScannNumbers=np.unique(self.MotorScannNumber[IndexAccordingToMotorPosition])
            ## Checking that we are not going out of boundaries
            if len(pScannNumbers)>SecondsToAnalyze:
                ScannNumbers=pScannNumbers[:-1]
            else:
                ScannNumbers=pScannNumbers

            for xx in ScannNumbers.astype(int):
                Index=IndexAccordingToMotorPosition[np.where(PositionsBeingEvaluated==xx)[0]]
                pTimeAngleAveragedMotorposition[x,xx]=np.mean(self.MotorPosition[Index])
                #if DataType==3:
                #    print xx
                #    pl.plot(Signal[Index], 'r*')
                #    print xx, len(Signal[Index])
                #    pl.show()
                pmnDataElevationAngle[x,xx]  = np.mean(Signal[Index])
                pstdDataElevationAngle[x,xx] = np.std(Signal[Index])
                pTimeMatrix[x,xx]=np.mean(self.Timestamp[Index])            
        

            Offset=Offset+1*AngularAverage
        
       # if DataType==3 or DataType==5 :    
            #pl.plot(pmnDataElevationAngle[:,2], '*')
            #pl.plot(pmnDataElevationAngle[:,5], 'r*')
            #pl.plot(pmnDataElevationAngle[:,6], 'k*')
        #    pl.plot(pmnDataElevationAngle[:,7], 'r.')
        #    pl.show()
        #    pl.imshow(pmnDataElevationAngle)
        #    pl.show()
        #    from scipy import signal
        #    fs=1e4
        #    f, Pxx_den = signal.periodogram(pmnDataElevationAngle[:,7], fs, 'flattop', scaling='spectrum')
        #    pl.plot(f, Pxx_den)
        #    pl.show()

        TimeAngleAveragedMotorposition = np.ma.array(pTimeAngleAveragedMotorposition,mask=~np.isfinite(pTimeAngleAveragedMotorposition))
        mnDataElevationAngle = np.ma.array(pmnDataElevationAngle,mask=~np.isfinite(pmnDataElevationAngle))
        stdDataElevationAngle= np.ma.array(pmnDataElevationAngle,mask=~np.isfinite(pmnDataElevationAngle))
        TimeMatrix=np.ma.array(pTimeMatrix,mask=~np.isfinite(pTimeMatrix))             

        ElapsedTime=time.time()-t1
        print( "----> Total Elapsed time:", ElapsedTime)
        print( "------------------------------" ) 
        return mnDataElevationAngle, stdDataElevationAngle, TimeAngleAveragedMotorposition, TimeMatrix

    def calculateTrueCourse(self,TimeAngleAveragedMotorposition,AngleAveragedTime):
        
        ## Calculating the True Course of the antenna beam

        TimeAveragedMotorPossition=np.mod(np.mean(TimeAngleAveragedMotorposition, axis=1)*(2*np.pi/16000)+18*np.pi/180, 2*np.pi)
       
        self.truecourse_x = np.cos(TimeAveragedMotorPossition)*np.sin(self.AntennaAngularOffset)
        self.truecourse_y = np.cos(self.AntennaAngularOffset)*np.cos(TimeAveragedMotorPossition)-np.sin(self.AntennaAngularOffset)*np.sin(TimeAveragedMotorPossition)**2
        self.truecourse_z = -(np.cos(TimeAveragedMotorPossition)*np.sin(TimeAveragedMotorPossition)*np.sin(self.AntennaAngularOffset)+np.sin(TimeAveragedMotorPossition)*np.cos(self.AntennaAngularOffset)) 
        
        self.BeamNadirAngle=np.arctan2(self.truecourse_z, self.truecourse_y)*180/np.pi
        self.BeamNadirAngle=np.mod(self.BeamNadirAngle, 360)

        b=np.abs(np.abs(self.BeamNadirAngle)-270)
        self.nadirIndex=np.where(b==np.min(b))[0][0]
        b=np.abs(np.abs(self.BeamNadirAngle)-90)
        self.zenithIndex=np.where(b==np.min(b))[0][0]

        ###################################################################################
        ### How do we calculate the time of each scan? 
        ### You could do it following different approaches, you could calculate 
        ### the mean time or the time of a singular time, in this case we provide the time 
        ### for nadir crossing. 
        #intermediateTimeAveragedTime= np.mean(AngleAveragedTime,axis=0)
        intermediateTimeAveragedTime= AngleAveragedTime[self.nadirIndex]
        TimeAveragedTime=intermediateTimeAveragedTime[intermediateTimeAveragedTime.mask==False]
        print( "Calculating True Course, signal lenght: ", len(TimeAveragedTime))

        return TimeAveragedMotorPossition, TimeAveragedTime


    def FunctionToMinimiseTC(self,x,AirMass,NormalizedVoltagesTipCurves, Teq, Tl):
        am=AirMass
        NVolts=NormalizedVoltagesTipCurves #0.813135935703615
        return sum((NVolts-(x[0]+(1-x[1]**am)*Teq+(x[1]**am)*2.7)/(x[0]+Tl))**2)    

                
    def tipingCurves(self, AirMass,NormalizedVoltagesTipCurves, Tl, Channel, position, c,b):        
       
     
       #FunctionToMinimiseTC()
       Tr=1000 #Treceiver inital guess
       gz=0.5 # zenith transmissivity, initial guess
       Teq=270 # equivalent air temperature
       
       ZenithPoss=np.where(np.array(AirMass)==np.min(np.array(AirMass)))
       
       AirMassToUse=AirMass[ZenithPoss[0]-50:ZenithPoss[0]+50]
       NormalizedVoltagesTipCurvesToUse=NormalizedVoltagesTipCurves[ZenithPoss[0]-50:ZenithPoss[0]+50]

       x0 = np.array([Tr,gz])
       res = minimize(self.FunctionToMinimiseTC, x0, args=(AirMassToUse,NormalizedVoltagesTipCurvesToUse, Teq, Tl), method='nelder-mead', options={'xtol': 1e-10, 'disp': True})
       print( "Trec:", res.x[0], 'K -Transmissivity:', res.x[1])
        
       x=[res.x[0],res.x[1]]

       IdealNormalizedTC=[]
       IdealNormalizedTC=(x[0]+(1-x[1]**AirMass)*Teq+(x[1]**AirMass)*2.7)/(x[0]+Tl)  
        
       figA = pl.figure(1775+position)
       ax = figA.add_subplot(111) 
       pl.plot(np.arccos(1/np.array(AirMass[ZenithPoss[0]:]))*180/np.pi,NormalizedVoltagesTipCurves[ZenithPoss[0]:],color='black', marker='.', label='Data '+Channel+' horizon to zenith ')
       pl.plot(np.arccos(1/np.array(AirMass[:ZenithPoss[0]]))*180/np.pi,NormalizedVoltagesTipCurves[:ZenithPoss[0]],color='blue',marker='.', label='Data '+Channel+' zenith to horizon ')
       pl.plot(np.arccos(1/np.array(AirMass))*180/np.pi,IdealNormalizedTC, color='red', marker='.', label='Ideal TC')
       pl.grid()
       pl.legend(loc = 'best',shadow = True)
       pl.show(block=False) 
       IdealTC=[]
       IdealTC=(x[0]+(1-x[1]**AirMassToUse)*Teq+(x[1]**AirMassToUse)*2.7)/(x[0]+Tl)
       rmse=np.sum((NormalizedVoltagesTipCurvesToUse-IdealTC)**2)/len(NormalizedVoltagesTipCurvesToUse)
       title='Trec=%d K - Transmissivity=%.2f - rmse:%.3e  '%(res.x[0],res.x[1],rmse)
       pl.title(title)
       pl.xlabel('Angle')
       pl.ylabel('Normalized TC')
      
       figA = pl.figure(1775000+position)
       #Tant=TcoldValue*cVector[x]-TrecVector[x]
       ax = figA.add_subplot(111) 
       pl.plot(AirMass[ZenithPoss[0]:],c*NormalizedVoltagesTipCurves[ZenithPoss[0]:]-b,color='black', marker='.', label='Data '+Channel+' horizon to zenith ')
       pl.plot(AirMass[:ZenithPoss[0]],c*NormalizedVoltagesTipCurves[:ZenithPoss[0]]-b,color='blue',marker='.', label='Data '+Channel+' zenith to horizon ')
       pl.plot(np.array(AirMass),c*IdealNormalizedTC-b, color='red', marker='.', label='Ideal TC')
       pl.grid()
       #pl.axis('equal')
       pl.legend(loc = 'best',shadow = True)
       title='Trec=%d K - Transmissivity=%.2f  '%(res.x[0],res.x[1])
       pl.title(title)
       pl.xlabel('Air Mass')
       pl.ylabel('TAnt')
       pl.show(block=False) 

       Trec=res.x[0]
       Transmissivity=res.x[1]

       return  figA, Trec, Transmissivity, rmse
     
     
    def getTskyvoltage(self, RadiometricDataVolts, finish, start, MotorCountsZenit,AngularSpanDegrees): 
        
        AngularSpan=np.round((AngularSpanDegrees*16000/360))
        AntennaLookingZenitIndex, MotorLookingZenitIndex=self.calculateIndexAccordinglyToMotorPosition(self.ANTValue,finish,MotorCountsZenit-AngularSpan,MotorCountsZenit+AngularSpan)
        VoltTsky=np.mean(RadiometricDataVolts[AntennaLookingZenitIndex])
        print( "Volts T_sky: %s",VoltTsky  )      
        return VoltTsky   
    
   

    # This function is not used in a regular basis, only to check that the is no desinchornization in the data acquistion
    def testSync(self, DataTypeValue=1):
        finish=300
        #z=np.array(np.where(self.SystemStatus_DIFF==0))[0]+3
        AntennaIndex, AntennaIndexDirty, AntennaIndexBoolean=self.calculateIndex(DataTypeValue, finish)
        Data=self.fromCountstoV(self.Counts[:,0])        
        fig=pl.figure(30)
        fig.suptitle('Checking clean-out transition samples', fontsize=14, fontweight='bold')
        ax = fig.add_subplot(111)
        pl.grid(True)
        pl.plot(1+np.abs(np.append([0, 0, 0],self.SystemStatus_DIFF[0:finish]/20.0)), 'r', label='System status Diff')
        #pl.plot(z[0:finish],1.1*np.ones(len(z[0:finish])),'k.', label='Clean out index')
        pl.plot(Data[0:finish], 'b.', label='Raw data')
        pl.plot(AntennaIndex[0:finish],1.1*np.ones(len(AntennaIndex[0:finish])),'c.', label='Clean OUT Index')
        pl.plot(AntennaIndexDirty[0:finish],1.11*np.ones(len(AntennaIndexDirty[0:finish])),'m.', label='NOT Clean OUT Index')
        pl.legend(loc = 'best',shadow = True)
        pl.ylabel("Values")
        pl.xlabel("Counts")
        #pl.title('Checking clean-out transition samples')
        ax.axis([0, 300, 0.8, 1.5])
        pl.show(block=False) 

    def testMotorIntegrity(self):
        pass
        # print "Looking for motor inconsisitencies."
        # a=self.MotorPosition
       # RadiometricDataVolts=self.fromCountstoV(self.Counts[:,0])
        # bb=(a>16000)
        # pl.plot(a)
        # if bb.any():
        # #if False:
        #     print "Warning Motor readouts higher than 16000, potential problem with the motor's Z signal"
        #     print "trying to fix the problem."
        #     b=(np.diff(a,axis=0))
        #     CompleteRotation=np.where(b<-1000)[0]
        #     b[CompleteRotation]=b[CompleteRotation]+16383 #(2^14-1)0
        #     c=np.cumsum(b)+a[0]
        #     d=[(i%16000) for i in c]
        #     self.WrongMotorPosition=self.MotorPosition
        #     self.MotorPosition= np.array([d],'int16').T           
        #    # print type(a), a.size
        #     #print type(self.MotorPosition), self.MotorPosition.size
        # else:       
        #     print "No motor incosistences found"
        
        # fig=pl.figure(222)
        # pl.subplot(2, 1, 1)        
        # pl.plot(a,RadiometricDataVolts,'.')
        # pl.subplot(2, 1, 2)
        # pl.plot(self.MotorPosition,RadiometricDataVolts[0:len(self.MotorPosition)], 'r.')
        # pl.xlabel("Motor Position", fontsize =18)
        # pl.ylabel("Radiometer readout", fontsize =18)
        # pl.title("Motor Position Vs Radiometer Readout", fontsize =18)
        # pl.grid(True)
        # pl.show()        
        return
        
    def rolling_window2(self,a, window):
        ## This rolling window is for computing Allan Variance
        # Fast version
        shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
        strides = a.strides + (a.strides[-1],)
        return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

        
    def AllanVariance(self, DataType, finish, start, RadiometricDataVolts, Atype,Tint,Bw,Verbose,DisplayPlots):
    
        print( "Warning #1: The input signal has to be continuolsy acquired with the motor not spinning if it its TANT")
        print( "Warning #2: This is Allan variance of the signal normalized by the mean ")
        Index,IndexDirty,IndexBooolean=self.calculateIndex(DataType,finish,start)
        preSignal=  RadiometricDataVolts[Index] 
        FreeNaNpreSignal=preSignal[np.isfinite(preSignal)]
        Signal=preSignal/np.mean(preSignal) 
        print( "Mean:" +repr(np.mean(preSignal)))
        nsh = Signal.shape
        alvar = np.zeros(int(nsh[0]/2), float)
        signalvar=np.zeros(int(nsh[0]/2), float)
        utime=range(1, int(nsh[0]/2))
    
        if Verbose==True:
            numpoints=len(FreeNaNpreSignal); maximum=np.max(FreeNaNpreSignal); minimum=np.min(FreeNaNpreSignal);
            mean=np.mean(FreeNaNpreSignal);  median=np.median(FreeNaNpreSignal) ; stdeviation=np.std(FreeNaNpreSignal)
            print( "#################################")
            print( "Numpoints:" + repr(numpoints))
            print( "Std:" +repr(stdeviation))
            print( "Max.:" + repr(maximum))
            print( "Min.:" +repr(minimum))
            print( "Mean:" +repr(mean))
            print( "Median:" +repr(median))
            print( "Performing " + Atype)
            print( "#################################")
    
        if(Atype=='OAVAR'):
            for lag in utime:
               # Oversampling due to sampling overlapp (OAVAR)
               Oversampling=lag 
               # Group the data into overlapping tau-length groups or bins
               # and find average in each "tau group", y (each colummn of f) 
               y=np.mean(self.rolling_window2(Signal, lag), 1)
               # First finite difference
               diffy=np.square(np.diff(y))
               # Calculate two-sample variance for this tau
               alvar[lag-1]=0.5*Oversampling*np.sum(diffy)/(len(y)-1)
               # Estimate error bars
               signalvar[lag-1]=alvar[lag-1]/np.sqrt(len(y)+1)
            display='r.'
        elif(Atype=='AVAR'):
            for lag in utime:
               # Truncate frequency set to an even multiple of this tau value
               TotalLength=int(np.floor(len(Signal)/lag))
               # Group the data into tau-length groups or bins
               e_n=np.reshape(Signal[:TotalLength*lag],(TotalLength,lag))
               # Find average in each "tau group", y (each colummn of f)                
               y=np.mean(e_n,1)
               # First finite difference
               diffy=np.square(np.diff(y))
               # Calculate two-sample variance for this tau
               alvar[lag-1]=0.5*np.sum(diffy)/(len(y)-1)
               # Estimate error bars
               signalvar[lag-1]=alvar[lag-1]/np.sqrt(len(y)+1)
            display='m.'
    
        GaussianNoiseTheoretical= -np.float32(np.array(np.log10(utime)))+np.log10(alvar[0])           
        time=np.linspace(Tint,Tint*len(alvar[:-1]), len(alvar[:-1]))
        print( Bw)
        RadiometricTheoretical= -np.float32(np.array(np.log10(Bw*1e6*time)))
    
        if DisplayPlots==True:
            ## Display the data Histogram
            fig=pl.figure(2032322)
            count, bins, ignored = pl.hist(Signal, 30, normed=True)
            mu=np.mean(Signal)
            sigma=np.std(Signal)
            pl.plot(bins, 1/(sigma*np.sqrt(2*np.pi))*np.exp(-(bins-mu)**2/(2*sigma**2)),linewidth=2, color='r')
            pl.title("Input data histogram", fontsize =18)
            pl.xlabel("Volts", fontsize =18)
            pl.ylabel("Occurrences", fontsize =18)
            pl.grid(True)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            ## Display the Allan Variance
            fig=pl.figure(102542342)
            pl.plot(np.log10(time),np.log10((alvar[:-1])), display, label=Atype)
            pl.plot(np.log10(time),GaussianNoiseTheoretical, 'k', label='Pure Gaussian Signal')
            pl.plot(np.log10(time),RadiometricTheoretical, 'b', label='Theoretical Rad')
            pl.xlabel("Time [log10(s)]", fontsize =18)
            pl.ylabel("Log10(AVAR)", fontsize =18)
            pl.title(Atype, fontsize =18)
            pl.grid(True)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
    
        return alvar, time, signalvar, GaussianNoiseTheoretical, RadiometricTheoretical              
  

    def WindowingAndInterpolatingNS(self, mnTypeSignal, mnTypeTime,mnANTTypeSignal, WindowSize=31, verbose=True, windowingType="Running Mean"):
        
        PolyOrder=3
        Dims=mnTypeSignal.shape
        #######################################################################################################
        ## Vectrizing the NxM matrixes, where M is the scan number and N is the angular position within the scan. 
        ## These vectors now are time series.
        NSVectorSignal=np.reshape(mnTypeSignal.T,(Dims[0]*Dims[1],1))
        #NSVectorTime=np.reshape(mnTypeTime.T,(Dims[0]*Dims[1],1))
        ANTVectorSignal=np.reshape(mnANTTypeSignal.T,(Dims[0]*Dims[1],1))

        #######################################################################################################
        ## Substracting the antenna temperature to the diode + antenna measurement
        x=range(0,Dims[0]*Dims[1])
        ##
        NonNanIndex=~np.isnan(NSVectorSignal.data)
        x_not_nan=np.where(NonNanIndex==True)[0]
        y_not_nan=NSVectorSignal.data[NonNanIndex]
        NSInterp=interp(x,x_not_nan,y_not_nan) 
        ##
        NonNanIndex2=~np.isnan(ANTVectorSignal.data)
        x_not_nan2=np.where(NonNanIndex2==True)[0]
        y_not_nan2=ANTVectorSignal.data[NonNanIndex2]
        ANTInterp=interp(x,x_not_nan2,y_not_nan2)         
        ###################################################################

        TwentyHertzFilter=np.ones(len(NSInterp))
        ### This needs to be calculated according to OneSecondinSamples
        OneSecondinSamples=self.SamplesPerSecond
        LowFrequencySixtyHamonics=[255, 270, -255, -270]
        for f in LowFrequencySixtyHamonics:
            poss_ini=int((f-15)*len(NSInterp)/OneSecondinSamples)
            poss_end=int((f+15)*len(NSInterp)/OneSecondinSamples)
            #print poss_end
            poss=range(poss_ini,poss_end)
            TwentyHertzFilter[poss]=0
        poss=range(int(255*len(NSInterp)/(OneSecondinSamples)), int(len(NSInterp)/2)-1)
        TwentyHertzFilter[poss]=0  
        poss=range(int(len(NSInterp)/2)-1, int(len(NSInterp)-255*len(NSInterp)/(OneSecondinSamples)) )
        TwentyHertzFilter[poss]=0       

        #print "--------------------------------------------------------------------------------------------"              
        #print "20 Hz Filter is going to be applied"
        #print "--------------------------------------------------------------------------------------------"
        TotalSeconds=len(NSInterp)/OneSecondinSamples           
        NSInterpFilered=np.abs(np.fft.ifft(np.multiply(TwentyHertzFilter,np.fft.fft(NSInterp))))
        ANTInterpFilered=np.abs(np.fft.ifft(np.multiply(TwentyHertzFilter,np.fft.fft(ANTInterp))))    



        ###################################################################
        ###################################################################
        ###################################################################          
        Ehat2=np.abs(self.runningMeanFast(NSInterpFilered, WindowSize)-self.runningMeanFast(ANTInterpFilered, WindowSize))#  runningMeanFast(NSInterp, 130)-self.runningMeanFast(ANTInterp, 130)
        ## Correcting for the edges and/or outliers
        mEhat2=np.mean(Ehat2) 
        OutlierThreshold=0.02
        OutliersIndex=(Ehat2>mEhat2*(1+OutlierThreshold))|(Ehat2<mEhat2*(1-OutlierThreshold))
        notOutlierIndex=~OutliersIndex
        Outliers= np.where(OutliersIndex)[0]
        NotOutliers= np.where(notOutlierIndex)[0]
        #print Outliers, mEhat2

        Ehat2[Outliers]=np.mean(Ehat2[NotOutliers])
        ## Returning to the NxM matrix form    
        mnE=np.reshape(Ehat2,(Dims[1], Dims[0]))
        

        if verbose==True:
            ###################################
            self.PlotSignalSpectrum(0, NSInterp, TwentyHertzFilter) 
            self.PlotSignalSpectrum(0, NSInterpFilered, TwentyHertzFilter)
            ###################################
            fig=pl.figure(12123)
            pl.plot(indices_not_nan, E,  'k')
            #pl.plot(indices_not_nan, Ehat,  'g*')
            pl.plot(indices,Ehat, 'r.')
            pl.show(block=False)
            ###################################
            fignum=98989
            fignum=fignum+1
            fig = pl.figure(fignum)
            ax = fig.add_subplot(111)
            mdat = np.ma.masked_array(mnE,np.isnan(mnE))
            mnEmean_TenPercent=0.1*np.mean(np.mean(mdat))
            zmin=np.min(np.min(mdat))-mnEmean_TenPercent #
            zmax=np.max(np.max(mdat))+mnEmean_TenPercent #
            cax = ax.imshow(mnE.T, cmap=cm.jet, vmin=zmin, vmax=zmax)  #130            
            fig.colorbar(cax).set_label('Antenna Temperature [K]', fontsize=12) 
            pl.xlabel('Scan Number')
            pl.ylabel('Nadir Angle')
            pl.grid()
            pl.show() 

        return mnE
    
    def runningMeanFast(self,  values, window):
        #print values.shape
        W=np.ones(window)/window
        #print W.shape
        B=np.convolve(values, W,'same') 
        #pl.plot(values)
        #print B.shape
        return B

    def movingaverage(self, values,window):
        weigths = np.repeat(1.0, window)/window
        #including valid will REQUIRE there to be enough datapoints.
        #for example, if you take out valid, it will start @ point one,
        #not having any prior points, so itll be 1+0+0 = 1 /3 = .3333
        smas = np.convolve(values, weigths, 'valid')
        return smas # as a numpy array    

    def savitzky_golay(self, y, window_size, order, deriv=0):
        import numpy as np
        import matplotlib.pyplot as plt
        """Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
        The Savitzky-Golay filter removes high frequency noise from data.
        It has the advantage of preserving the original shape and
        features of the signal better than other types of filtering
        approaches, such as moving averages techhniques.
        
        This code has been taken from http://www.scipy.org/Cookbook/SavitzkyGolay
        Parameters
        ----------
        y : array_like, shape (N,)
            the values of the time history of the signal.
        window_size : int
            the length of the window. Must be an odd integer number.
        order : int
            the order of the polynomial used in the filtering.
            Must be less then `window_size` - 1.
        deriv: int
            the order of the derivative to compute (default = 0 means only smoothing)
        Returns
        -------
        ys : ndarray, shape (N)
            the smoothed signal (or it's n-th derivative).
        Notes
        -----
        The Savitzky-Golay is a type of low-pass filter, particularly
        suited for smoothing noisy data. The main idea behind this
        approach is to make for each point a least-square fit with a
        polynomial of high order over a odd-sized window centered at
        the point.
        Examples
        --------
        t = np.linspace(-4, 4, 500)
        y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
        ysg = savitzky_golay(y, window_size=31, order=4)
        import matplotlib.pyplot as plt
        plt.plot(t, y, label='Noisy signal')
        plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
        plt.plot(t, ysg, 'r', label='Filtered signal')
        plt.legend()
        plt.savefig('images/golay.png')
        #plt.show()
        References
        ----------
        .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
           Data by Simplified Least Squares Procedures. Analytical
           Chemistry, 1964, 36 (8), pp 1627-1639.
        .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
           W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
           Cambridge University Press ISBN-13: 9780521880688
        """
        try:
            window_size = np.abs(int(window_size))
            order = np.abs(int(order))
        except( ValueError, msg):
            raise ValueError("window_size and order have to be of type int")
        if window_size % 2 != 1 or window_size < 1:
            raise TypeError("window_size size must be a positive odd number")
        if window_size < order + 2:
            raise TypeError("window_size is too small for the polynomials order")
        order_range = range(order+1)
        half_window = (window_size -1) // 2
        # precompute coefficients
        b = np.asmatrix([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
        m = np.linalg.pinv(b).A[deriv]
        # pad the signal at the extremes with
        # values taken from the signal itself
        firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
        lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
        y = np.concatenate((firstvals, y, lastvals))
        return np.convolve( m, y, mode='valid')


def main():
    
    import tables as tb
    import os
    import sys
    configfile='..\..\GeneralPaths.py'
    sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
    from GeneralPaths import H5_DATA_BASE_PATH
    from RadiometerAux import radiometer        

    print( "\n\n-+++------------------------------------+++-" )
    print( "## -- This is a Class, not to be run as a SCRIPT -- ##")
    #filenameroot='PLIVtest'
    filenameroot='2014_04_11__06_36_02__1of1_PLTVIII'
    print( "-->WARNING: %s is provided with the repository for debugin purposes only"%filenameroot)
    print( "-+++------------------------------------+++-"     )
    filename=filenameroot+'.h5'
    if not os.path.isabs(filename):
        filenameh5 = os.path.join(H5_DATA_BASE_PATH, filename)
        
    h5file0=tb.open_file(filenameh5, mode="r")
    print( "-----------------------------------------")
    for group in h5file.walkGroups("/"):
        print( "--", group)
    print( "-----------------------------------------")
    
    TotalSecondsToAnalyze=5
    ChannelSetToAnalyze='mw'
    ChSetdpa=radiometer(h5file,ChannelSetToAnalyze )
    Tint=0.2
    Tint_seconds=Tint/1000

    start=0
    finish=TotalSecondsToAnalyze/Tint_seconds
    x=7 #6
    RadiometricDataVolts=ChSetdpa.fromCountstoV(ChSetdpa.Counts[:,x])
    if x<4 and ChannelSetToAnalyze=='mw':
        PhysicalDickeTempChannels =ChSetdpa.PhysicalDickeTempChannels[ChannelSetToAnalyze][0]
    elif ChannelSetToAnalyze=='mw' :
        PhysicalDickeTempChannels =ChSetdpa.PhysicalDickeTempChannels[ChannelSetToAnalyze][1]
    elif ChannelSetToAnalyze=='mmw':
        PhysicalDickeTempChannels =ChSetdpa.PhysicalDickeTempChannels[ChannelSetToAnalyze][x]

    pattern=[1, 1, 1, 47]
    lag=64*4 
    lagTemp=10
    NS=['NS2','NS1','NS3','NS1']
    TantNS, GainNS, TrecNS= ChSetdpa.NSCalibration(RadiometricDataVolts, finish, start, PhysicalDickeTempChannels, pattern, lag, lagTemp,NS,x)
    fig=pl.figure(1)
    pl.plot(TantNS)
    pl.show(block=False) 
    fig=pl.figure(2)
    pl.plot(GainNS)
    pl.plot(TrecNS)
    pl.show(block=False) 
   

if __name__ == "__main__":
    main()