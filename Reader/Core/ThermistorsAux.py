# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 15:13:01 2013

@author: xbosch
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

from matplotlib.figure import Figure

type Array = np.ndarray


class thermistors:
    def __init__(self, h5file, verbose=True):
        print("INFO: New instance of Thermistors data")
        data = h5file.root.Temperature_Data.Thermistor_DATA
        self.TMP_Voltages = np.array([x['Voltages'] for x in data.iterrows()])
        self.TMP_Timestamp = np.array([x['Timestamp'] for x in data.iterrows()])
        self.TMP_PackageNum = np.array([x['Packagenumber'] for x in data.iterrows()])
        self.length = len(self.TMP_Voltages)
        
        # In the future this has to be imported from the HDF5 file from information provided by the server
        # TODO: AGW - the future is now but it hasn't been implemented yet
        ## We need to calculate the OpenCircuit Voltage for the Digitizer #1        
        self.regulatedVoltage = [1.1278, 1.0804, 1.1052, 1.0966, 1.0804] # Weldon found 1.125 for ADC#3
        self.ThermistorType = ['KS502J2', 'KS502J2', '44906', 'KS502J2', 'KS502J2']
        self.ActiveADC = [3, 0, 1, 2, 4]
        self.Temp = np.empty([len(self.ActiveADC)*8, self.length])
        self.ThermistorConnected = np.empty(len(self.ActiveADC)*8,'bool_')
        index = 0
        for x in self.ActiveADC:
            for thermistor in range(8):
                self.Temp[index,:], self.ThermistorConnected[index]=self.fromVoltagetoT(self.TMP_Voltages[:,index],self.regulatedVoltage[x], self.ThermistorType[x])
                if self.ThermistorConnected[index]==False:
                    if verbose:
                        print( "Warning: Thermistor %s from ADC#%s is not connected"%(index,x))
                index += 1
        
        ## Defining Thermistor Names&Colors
        self.color = ['red', 'cyan', 'yellow', 'black', 'magenta','green','blue','#a2a7ff']
        self.thermistorName = [
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
        
        self.thermistorSTD = {}
        self.thermistorAVG = {}            

        self.thermistorResampled = []
        self.CalibratonTargetChannelsResampledSpatiallyAveraged = []
        self.resamplingTime = []
        self.ThermistorFilteredAndResampled = []


    def thermistorsFilterAndResampling(self, externalclk,WindowLength=5, Verbose=True) -> None:
        ## This function resamples the thermsitor at the motor speed rate
        ## Usually motor is at 1Hz and thermistors at 1.1 Hz, so needs to be adjusted        
        DeltaTime = 0.01  # new interpolated signal resolution in seconds
        L = len(externalclk)
        acqTime = np.squeeze(self.TMP_Timestamp-self.TMP_Timestamp[0])
        zeroOffsetExternalclk = np.squeeze(externalclk-externalclk[0])
        self.ThermistorFilteredAndResampled = np.empty([40,L])
        index = []
        NewTime = np.arange(acqTime[0], acqTime[-1], DeltaTime)
        # Calculating resampling index
        for i in range(L):
            timestampref = np.abs(NewTime-zeroOffsetExternalclk[i])
            index.append(np.where(timestampref==timestampref.min())[0][0])
            self.resamplingTime.append(externalclk[i]) 
        # Filtering and interpolating
        SemiWindowLength = int(np.floor(WindowLength/2))
        for i in range(40):
            FilteredTemp = self.runningMeanFast(self.Temp[i,:], WindowLength)
            FilteredTemp[0:SemiWindowLength] = self.Temp[i,0:SemiWindowLength]
            FilteredTemp[-SemiWindowLength:] = self.Temp[i,-SemiWindowLength-1:-1]
            f = interpolate.interp1d(acqTime,FilteredTemp)
            B = f(NewTime)
            # Resampling
            self.ThermistorFilteredAndResampled[i,:] = B[index]
            if Verbose:
                fig = plt.figure(40660)
                plt.plot(acqTime,self.Temp[i,:].T, 'ro', label= self.thermistorName[i])
                plt.plot(acqTime,FilteredTemp, 'b', label= self.thermistorName[i])
                plt.plot(NewTime[index],self.ThermistorFilteredAndResampled[i,:].T, 'k.')   
                plt.grid(True)
                plt.ylabel("Celsius")
                plt.xlabel("Seconds")
                plt.legend()
                plt.show()
    

    def runningMeanFast(self, x, N) -> Array:
        window = np.ones(int(N)) / float(N)
        return np.convolve(x, window, 'same')


    def thermistorsResamplingAverage(self,ThremistorArray, CalTargetArray, Verbose=True) -> None:
        TemperaturesToResample = np.array([self.ThermistorFilteredAndResampled[x,:] for x in ThremistorArray])
        TemperaturesCalTarget = np.array([self.ThermistorFilteredAndResampled[x,:] for x in CalTargetArray])     
        self.CalibratonTargetChannelsResampledSpatiallyAveraged = np.mean(TemperaturesCalTarget, axis=0)
        self.ThermistorResampledAndAveraged = np.mean(TemperaturesToResample, axis=0)
        if Verbose:
            print('Resampled Temps:', self.ThermistorResampledAndAveraged, len(self.ThermistorResampledAndAveraged))
            print('Resampled CalTar Temps:',self.CalibratonTargetChannelsResampledSpatiallyAveraged, len(self.CalibratonTargetChannelsResampledSpatiallyAveraged))
 

    def fromVoltagetoT(self, voltage, regulatedVoltage, thermistorType) -> tuple[float, bool]:
        if thermistorType == '44906':
            #print 'Radiometer Type Thermistor'
            A = 1.28082086269172 * 10 ** -3
            B = 2.36865057309759 * 10 ** -4
            C = 9.02634799967035 * 10 ** -8
            D = 0
        elif thermistorType == 'KS502J2':
            #print 'General Type Thermistor'configfile='..\..\GeneralPaths.py'
            A = 1.29337828808 * 10 ** -3
            B = 2.34313147501 * 10 ** -4
            C = 1.09840791237 * 10 ** -7
            D = -6.51108048031* 10 ** -11
        
        if np.mean(voltage) > 1.11: 
            ThermistorConnected = False
            tempC = np.zeros(len(voltage))
        else:
            ThermistorConnected = True
            resist = (voltage / (regulatedVoltage - voltage)) * 5000
            tempInv = (A + B * np.log(resist) + C * np.log(resist)**3 + D * np.log(resist)**5)
            temp = 1 / tempInv
            tempC = temp - 273.15
        return tempC, ThermistorConnected


    def GetTemperatureByTime(self, TimeIDInternalReference, ThremistorArray, TimeToAverage) -> Array:
        MeanTemperature = np.zeros(len(TimeIDInternalReference))
        for i in range(len(TimeIDInternalReference)):
            PositionIndexBoolean = np.logical_and(self.TMP_Timestamp>(TimeIDInternalReference[i]-TimeToAverage),self.TMP_Timestamp<(TimeIDInternalReference[i]+TimeToAverage))
            PositionIndex = np.where(PositionIndexBoolean==True)[0]
            TemperaturesToAverage = 0            
            for x in range(len(ThremistorArray)):
                TemperaturesToAverage = TemperaturesToAverage + np.sum(self.Temp[ThremistorArray[x],PositionIndex])
               
            MeanTemperature[i] = TemperaturesToAverage/(len(ThremistorArray)*len(PositionIndex))
        return MeanTemperature
    

    def GetMeanTemperatureChannels(self, ThremistorArray) -> tuple[float, float, dict, dict, float, float, float]:
        TemperaturesToAverage = [self.Temp[x,:] for x in ThremistorArray]
        AverageTemperature = np.mean(np.mean(TemperaturesToAverage,1),0)
        STDTemperature = np.mean(np.std(TemperaturesToAverage,1),0)
        TherAVG = np.mean(TemperaturesToAverage,1)        
        TherSTD = np.std(TemperaturesToAverage,1)
        iterable = zip(ThremistorArray,TherSTD)
        self.thermistorSTD = {key: value for (key,value) in iterable}   
        iterable = zip(ThremistorArray, TherAVG)        
        self.thermistorAVG = {key: value for (key,value) in iterable} 
        minTemperature = np.min(np.mean(TemperaturesToAverage,1),0)
        maxTemperature = np.max(np.mean(TemperaturesToAverage,1),0)
        return AverageTemperature, STDTemperature, self.thermistorSTD, self.thermistorAVG, minTemperature, maxTemperature, maxTemperature-minTemperature
        

    def GetMeanTemperatureDepartingChannels(self, ThremistorArray, ThermistorReference) -> tuple[float, float]:
        TemperaturesToAverage = [self.Temp[x,:] for x in ThremistorArray]
        OffsetTemperatures = TemperaturesToAverage - np.mean(self.Temp[ThermistorReference,:])
        AverageTemperature = np.mean(OffsetTemperatures, 1)
        stdTemperature = np.std(OffsetTemperatures, 1)
        return AverageTemperature, stdTemperature    
        

    def PlotThermistorByName(self, namevector, title) -> tuple[Figure, Array, Array]:
        TemperatureArray=np.empty([len(namevector),len(self.Temp[0,:])])       
        fig=plt.figure(4066)
        index=0
        for name in namevector:
            xx =[i for i, s in enumerate(self.thermistorName) if name in s]
            self.GetMeanTemperatureChannels([xx[0]])
            legend=u"%s:%.2f\u00b0\u00B1%.2f\u00b0C"%(self.thermistorName[xx[0]],self.thermistorAVG[xx[0]],self.thermistorSTD[xx[0]])
            plt.plot(self.TMP_Timestamp-self.TMP_Timestamp[0],self.Temp[xx[0],:],  color = self.color[xx[0]%8], label= legend)
            Time=self.TMP_Timestamp,
            #print xx[0], i 
            TemperatureArray[index,:]=self.Temp[xx[0],:]
            index=index+1
            
        plt.legend(loc = 'best',shadow = True)
        plt.grid(True)
        plt.ylabel("Celsius")
        plt.xlabel("Seconds")
        plt.title(title)
       # plt.show(block=False)
        return fig, Time, TemperatureArray


    def printthermistors(self, title=" ") -> Figure:
        fig=plt.figure(4001) 
        ## ADC4
        plt.subplot(5, 1, 1)
        for i in range(0, 7):
            plt.plot(self.TMP_Timestamp-self.TMP_Timestamp[0],self.Temp[i,:],  color = self.color[i%8], label= self.thermistorName[i], linewidth=4.0)
        plt.legend(loc = 'best',shadow = True)
        plt.grid(True)
        plt.ylabel("Celsius")
        ## ADC1 
        plt.subplot(5, 1, 2)
        for i in range(8, 15):
            plt.plot(self.TMP_Timestamp-self.TMP_Timestamp[0],self.Temp[i,:],  color = self.color[i%8], label= self.thermistorName[i], linewidth=4.0)
        plt.legend(loc = 'best',shadow = True)
        plt.grid(True)
        plt.ylabel("Celsius")
        ## ADC2
        plt.subplot(5, 1, 3) 
        for i in range(16, 21):
            plt.plot(self.TMP_Timestamp-self.TMP_Timestamp[0],self.Temp[i,:],  color = self.color[i%8], label= self.thermistorName[i], linewidth=4.0)
        plt.legend(loc = 'best',shadow = True)
        plt.grid(True) 
        plt.ylabel("Celsius")
        ## ADC3     
        plt.subplot(5, 1, 4)
        for i in range(24, 31):
            plt.plot(self.TMP_Timestamp-self.TMP_Timestamp[0],self.Temp[i,:], color = self.color[i%8], label= self.thermistorName[i], linewidth=4.0)
        plt.legend(loc = 'best',shadow = True)
        plt.grid(True)
        plt.ylabel("Celsius")
        ## ADC4xx[0]
        plt.subplot(5, 1, 5) 
        for i in range(32, 40):
            plt.plot(self.TMP_Timestamp-self.TMP_Timestamp[0],self.Temp[i,:],  color = self.color[i-32], label= self.thermistorName[i], linewidth=4.0)
        plt.legend(loc = 'best',shadow = True)
        plt.grid(True)
        plt.ylabel("Celsius")
        plt.suptitle("System Temperature " +title)
        #plt.show(block=False)
        return fig
        
# def main():
#     import tables as tb
#     import os
#     import sys
#     configfile='..\..\GeneralPaths.py'
#     sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
#     from GeneralPaths import H5_DATA_BASE_PATH

#     print( "\n\n###This is a Class, not to be run as a SCRIPT##")
#     filenameroot='2014_11_04__09_55_31__2of2_WCFC_Day1_LN2_Calibration'

#     filename=filenameroot+'.h5'
#     print( "WARNING: %s is provided with the repository for debuging purposes only"%filename)
#     if not os.path.isabs(filename):
#         filenameh5 = os.path.join(H5_DATA_BASE_PATH, filename)
        
#     h5file=tb.open_file(filenameh5, mode = "r")
#     print( "-----------------------------------------")
#     for group in h5file.walkGroups("/"):
#         print( "--", group)
#     print( "-----------------------------------------")
#     Thermistors=thermistors(h5file)
#     Thermistors.printthermistors(filenameroot)
#     #print Thermistors.GetMeanTemperatureChannels([8,9, 10, 11,12,13,14, 15])
#     #print Thermistors.GetMeanTemperatureDepartingChannels([8,9, 10, 11,12,13,14, 15], 10)
#     #Thermistors.PlotThermistorByName(['ABEB Bloc','SND-118 Multiplier','SND-183 Multiplier'], filenameroot)
#     figThermistorByName,time, TemperatureArray= Thermistors.PlotThermistorByName(["CalTar|Upper Left[1]","CalTar|Lower Left[3]","CalTar|Center[2]","CalTar|Bottom Left[1]","CalTar|Bottom Right[3]","CalTar|Upper Right[3]" ,"CalTar|Lower Right[1]", "CalTar|Top[2]"], filenameroot)

# if __name__ == "__main__":
#     main()