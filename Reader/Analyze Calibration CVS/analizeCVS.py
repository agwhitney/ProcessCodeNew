# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 16:12:27 2014

@author: xbosch
"""
import os
import sys
import pylab as pl
import matplotlib as mpl
from pylab import *
import numpy as np
import time
configfile='./Core/DataProcessorAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from DataProcessorAux import dataprocess
configfile='./Core/ThermistorsAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from DataProcessorAux import thermistors
from scipy.interpolate import griddata
configfile='./Core/AntennaTemperatureFileAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from AntennaTemperatureFileAux import CreateAntennaTempeartureFile
configfile='./Core/GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import H5_DATA_BASE_PATH, CVS_FILES_DATA_BASE_PATH,DATA_PROCESSED_PATH
import csv
from scipy.optimize import curve_fit
def f(x, A, B): # this is your 'straight line' y=f(x)
    return A*x + B    


RadiometricDataType='MW'
ChannelsNamesMW=['MW_34_GHz_QV','NotConnected', 'MW_18_GHz_QV', 'MW_24_GHz_QV','MW_34_GHz_QH','NotConnected', 'MW_18_GHz_QH', 'MW_24_GHz_QH']
ChannelsNamesMMW=['MMW_168_GHz','NotConnected','MMW_90_GHz','MMW_130_GHz']
ChannelsNamesSND=['SND_183-5_GHz','SND_183-7_GHz', 'SND_183-3_GHz','SND_183-6_GHz','SND_118+0_GHz','SND_118+5_GHz','SND_118+4_GHz', 'SND_118+0.5_GHz','SND_183-2_GHz','SND_183-1_GHz', 'SND_183-8_GHz','SND_183-4_GHz','SND_118+1_GHz','SND_118+3_GHz','SND_118+0.25_GHz', 'SND_118+2_GHz']
ChannelstoBeExploredMW =[0,2,3,4,6,7]
ChannelstoBeExploredMMW =[0,2,3]
ChannelstoBeExploredSND =[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] 


ChannelsNames=eval('ChannelsNames' + RadiometricDataType)
ChannelsToAnalyze=eval('ChannelstoBeExplored' + RadiometricDataType)


filenameroot='CalibrationFilesAnalysis_ALL_'
ChannelNameNumber=2



##################################################################### 
cvsFileName='WCFC LN2 Calibration Points 2Out_MW_All_v002g'
FromCVSFile=True
##################################################################### 
pathfordata=os.path.join(DATA_PROCESSED_PATH, 'WCFC LN2 Calibration Points 2CVS',  cvsFileName+'.csv')
csvfileOpen = open(pathfordata, 'rt')
spamreader = csv.reader(csvfileOpen, delimiter=',')
preFilenameVector=[]
preGPSTimeVector=[]
preGainVector=[]
preTrecVector=[]
preAltitudeVector=[]
preLatVector=[]
preLonVector=[]
preExternalTemperatureVector=[]
preRadSetTypeVector=[]
preChannelVector=[]
premeanRadTemperatureVector=[]
prestdRadTemperatureVector=[]
preENR_NS1Vector=[]
preENR_NS2Vector=[]
preENR_NS3Vector=[]
preNS1824TemperatureVector=[]
preNS34TemperatureVector=[]

for row in spamreader:
    preFilenameVector.append(row[0])
    preGPSTimeVector.append(row[1])
    preRadSetTypeVector.append(row[2])
    preChannelVector.append(row[3])    
    preGainVector.append(row[4])
    preTrecVector.append(row[5])
    preAltitudeVector.append(row[6])
    preLatVector.append(row[7])
    preLonVector.append(row[8])
    preExternalTemperatureVector.append(row[9])    
    premeanRadTemperatureVector.append(row[10])  
    prestdRadTemperatureVector.append(row[11])
    preENR_NS1Vector.append(row[12])  
    preENR_NS2Vector.append(row[13])  
    preENR_NS3Vector.append(row[14])
    preNS1824TemperatureVector.append(row[15])
    preNS34TemperatureVector.append(row[16])       
    
for ChannelNameNumber in [6]: #ChannelsToAnalyze:   
    matplotlib.pyplot.close("all")
    
    ChannelName=ChannelsNames[ChannelNameNumber]
    print ChannelName
    indexes = [i for i,x in enumerate(preChannelVector) if x == str(ChannelNameNumber)]
    FilenameVector=[]
    GPSTimeVector=[]
    GainVector=[]
    TrecVector=[]
    AltitudeVector=[]
    LatVector=[]
    LonVector=[]
    ExternalTemperatureVector=[]
    meanRadTemperatureVector=[]
    stdRadTemperatureVector=[]
    ENR_NS3Vector=[]
    ENR_NS3Vector=[]
    ENR_NS3Vector=[]
    NS1824TemperatureVector=[]
    NS34TemperatureVector=[]    
    
    ## Selecting the channel of interest
    FilenameVector=list( preFilenameVector[i] for i in indexes )
    GPSTimeVector=list( preGPSTimeVector[i] for i in indexes )
    GainVector=list( preGainVector[i] for i in indexes )
    TrecVector=list( preTrecVector[i] for i in indexes )
    AltitudeVector=list( preAltitudeVector[i] for i in indexes )
    LatVector=list( preLatVector[i] for i in indexes )
    LonVector=list( preLonVector[i] for i in indexes )
    ExternalTemperatureVector=list( preExternalTemperatureVector[i] for i in indexes )
    meanRadTemperatureVector=list( premeanRadTemperatureVector[i] for i in indexes )
    stdRadTemperatureVector=list( prestdRadTemperatureVector[i] for i in indexes )
    ENR_NS1Vector=list( preENR_NS1Vector[i] for i in indexes )
    ENR_NS2Vector=list( preENR_NS2Vector[i] for i in indexes )
    ENR_NS3Vector=list( preENR_NS3Vector[i] for i in indexes )    
    NS1824TemperatureVector=list(preNS1824TemperatureVector[i] for i in indexes )
    NS34TemperatureVector=list(preNS34TemperatureVector[i] for i in indexes )        
    #RadSetTypeVector=preRadSetTypeVector[indexes]
    
    
    if np.mod(ChannelNameNumber,4)==0:
        NSTemperature=NS34TemperatureVector
    else: 
        NSTemperature=NS1824TemperatureVector
        
        
    print '############################'
    print 'CVS file:', pathfordata
    print 'GPSTimeVector:', GPSTimeVector
    print '############################'    
    #print DataVector[1]

    Time=np.array(GPSTimeVector,dtype=np.float64)
    XvariablemeanRadTemperatureVector=np.array(meanRadTemperatureVector,dtype=np.float64)
    XcoordmeanRadTemperatureVector = np.vstack([XvariablemeanRadTemperatureVector, np.ones(len(XvariablemeanRadTemperatureVector))]).T       
    TemperatureSwept=np.linspace(-5,40,100)
    pathfordata='C:\IIP Software Project\AcqSystem\Reader\Results\WCFC LN2 Calibration Points 2CVS'
    fignum=2300
    fig = pl.figure(fignum)
    ax = fig.add_subplot(111)
    b=np.array(GainVector,dtype=np.float64)
    normalizedGain=b /np.mean( b)               
    pl.plot(meanRadTemperatureVector,normalizedGain, marker='o', label='Calibration Gain', linestyle = 'None',color='red')                     
    [Ag,Bg], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedGain) # your data x, y to fit 
    pl.plot(TemperatureSwept, Ag*TemperatureSwept+Bg,label='%.4f*T+%.2f, R:%.3f%%'%(Ag,Bg,100*residuals), linewidth = 2.0,color='black')    
    pl.grid(True)
    pl.ylim([0.85, 1.15])
    pl.xlabel('Tph receiver [C]')
    pl.ylabel('Gain [normalized]')
    title='Gain Vs Temperature for '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)
    
    fignum=2400
    fig = pl.figure(fignum)
    ax = fig.add_subplot(111)
    b=np.array(TrecVector,dtype=np.float64)
    normalizedTrecVector=b /np.mean( b)                       
    pl.plot(meanRadTemperatureVector,normalizedTrecVector, marker='o', linestyle = 'None', label='Trec',color='blue')
    [At,Bt], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedTrecVector) # your data x, y to fit    
    pl.plot(TemperatureSwept, At*TemperatureSwept+Bt,label='%.4f*T+%.2f, R:%.3f%%'%(At,Bt,100*residuals), linewidth = 2.0,color='black')                
    pl.grid(True)
    pl.ylim([0.85, 1.15])    
    pl.xlabel('Tph receiver [C]')
    pl.ylabel('Trec [normalized]')
    title='Trec Vs Temperature for '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)    
    
    fignum=2301
    fig = pl.figure(fignum)
    ax = fig.add_subplot(111)       
    pl.plot(Time-Time[0],100*(normalizedGain-(Ag*XvariablemeanRadTemperatureVector+Bg)), marker='o', label='Gain Residual', linestyle = 'None',color='red')
    pl.plot(Time-Time[0],100*(normalizedTrecVector-(At*XvariablemeanRadTemperatureVector+Bt)), marker='o', label='$T_{REC}$ Residual', linestyle = 'None',color='blue')                      
    pl.grid(True)
    pl.ylim([-1.6, 1.6])
    pl.xlabel('Time [s]')
    pl.ylabel('Normalized Gain Error [%]')
    title='Normalized Gain Error after Compensating for Radiometer Temperature Time Series  '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)    
    
    


    fignum=1300
    fig = pl.figure(fignum)
    ax = fig.add_subplot(111)
    b=np.array(ENR_NS1Vector,dtype=np.float64)
    normalizedENR_NS1Vector=b /np.mean( b)
    b=np.array(ENR_NS2Vector,dtype=np.float64)
    normalizedENR_NS2Vector=b /np.mean( b) 
    b=np.array(ENR_NS3Vector,dtype=np.float64)
    normalizedENR_NS3Vector=b /np.mean( b)                  
    pl.plot(meanRadTemperatureVector,normalizedENR_NS1Vector, marker='o', label='$T_{NS1 ON} -T_{NS1 OFF}$', linestyle = 'None',color='red')                
    pl.plot(meanRadTemperatureVector,normalizedENR_NS2Vector, marker='o', label='$T_{NS2 ON} -T_{NS2 OFF}$', linestyle = 'None',color='blue')
    pl.plot(meanRadTemperatureVector,normalizedENR_NS3Vector, marker='o', label='$T_{NS3 ON} -T_{NS3 OFF}$', linestyle = 'None',color='green')     
    [A,B], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedENR_NS1Vector) # your data x, y to fit 
    pl.plot(TemperatureSwept, A*TemperatureSwept+B,label='%.4f*T+%.2f, R:%.3f %%'%(A,B,100*residuals), linewidth = 2.0,color='red')
    [A,B], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedENR_NS2Vector) # your data x, y to fit     
    pl.plot(TemperatureSwept, A*TemperatureSwept+B,label='%.4f*T+%.2f, R:%.3f %%'%(A,B,100*residuals), linewidth = 2.0,color='blue')
    [A,B], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedENR_NS3Vector) # your data x, y to fit       
    pl.plot(TemperatureSwept, A*TemperatureSwept+B,label='%.4f*T+%.2f, R:%.3f %%'%(A,B,100*residuals), linewidth = 2.0,color='green')  
    pl.grid(True)
    pl.ylim([0.85, 1.15])    
    pl.xlabel('Tph receiver [C]')
    pl.ylabel('Normalized $T_{NSx ON} -T_{NSx OFF}$ ')
    title='Normalized TNS_ONx-TNS_OFFx Vs Temperature for '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)



    fignum=1301
    fig = pl.figure(fignum)
    ax = fig.add_subplot(111)
    XcoordNSTemperature = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                   
    pl.plot(NSTemperature,ENR_NS1Vector, marker='o', label='$T_{NS1 ON} -T_{NS1 OFF}$', linestyle = 'None',color='red')                
    pl.plot(NSTemperature,ENR_NS2Vector, marker='o', label='$T_{NS2 ON} -T_{NS2 OFF}$', linestyle = 'None',color='blue')
    pl.plot(NSTemperature,ENR_NS3Vector, marker='o', label='$T_{NS3 ON} -T_{NS3 OFF}$', linestyle = 'None',color='green')    
    [A1,B1], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, ENR_NS1Vector) # your data x, y to fit           
    pl.plot(TemperatureSwept, A1*TemperatureSwept+B1,label='%.4f*T+%.2f, R:%.2f K'%(A1,B1,residuals), linewidth = 2.0,color='red')
    [A2,B2], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, ENR_NS2Vector) # your data x, y to fit          
    pl.plot(TemperatureSwept, A2*TemperatureSwept+B2,label='%.4f*T+%.2f, R:%.2f K'%(A2,B2,residuals), linewidth = 2.0,color='blue')
    [A3,B3], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature,  ENR_NS3Vector) # your data x, y to fit      
    pl.plot(TemperatureSwept, A3*TemperatureSwept+B3,label='%.4f*T+%.2f, R:%.2f K'%(A3,B3,residuals), linewidth = 2.0,color='green')  
    pl.grid(True)
    pl.xlabel('Tph NS [C]')
    pl.ylabel('$T_{NSx ON} -T_{NSx OFF}$ [K]')
    title='TNS_ONx-TNS_OFFx Vs NS Temperature for '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)
    
 

    fignum=1302
    fig = pl.figure(fignum)
    ax = fig.add_subplot(111)
    b=np.array(ENR_NS1Vector,dtype=np.float64)
    normalizedENR_NS1Vector=b /np.mean( b)
    b=np.array(ENR_NS2Vector,dtype=np.float64)
    normalizedENR_NS2Vector=b /np.mean( b)
    b=np.array(ENR_NS3Vector,dtype=np.float64)
    normalizedENR_NS3Vector=b /np.mean( b)

    XcoordNSTemperature = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                   
    pl.plot(NSTemperature,normalizedENR_NS1Vector, marker='o', label='$(T_{NS1 ON} -T_{NS1 OFF})$', linestyle = 'None',color='red')                
    pl.plot(NSTemperature,normalizedENR_NS2Vector, marker='o', label='$(T_{NS2 ON} -T_{NS2 OFF})$', linestyle = 'None',color='blue')
    pl.plot(NSTemperature,normalizedENR_NS3Vector, marker='o', label='$(T_{NS3 ON} -T_{NS3 OFF})$', linestyle = 'None',color='green')    
    [A1,B1], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, normalizedENR_NS1Vector) # your data x, y to fit           
    pl.plot(TemperatureSwept, A1*TemperatureSwept+B1,label='%.4f*T+%.2f, R:%.3f %%'%(A1,B1,100*residuals), linewidth = 2.0,color='red')
    [A2,B2], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, normalizedENR_NS2Vector) # your data x, y to fit          
    pl.plot(TemperatureSwept, A2*TemperatureSwept+B2,label='%.4f*T+%.2f, R:%.3f %%'%(A2,B2,100*residuals), linewidth = 2.0,color='blue')
    [A3,B3], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature,  normalizedENR_NS3Vector) # your data x, y to fit      
    pl.plot(TemperatureSwept, A3*TemperatureSwept+B3,label='%.4f*T+%.2f, R:%.3f %%'%(A3,B3,100*residuals), linewidth = 2.0,color='green')  
    pl.grid(True)
    pl.xlabel('Tph NS [C]')
    pl.ylabel('normalized $T_{NS1 ON} -T_{NS1 OFF}$')
    title='Normalized TNS_ONx-TNS_OFFx Vs NS Temperature for '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)
    
 
    fignum=1303
    fig = pl.figure(fignum)
    TrecVector2Swept=np.linspace(np.min(normalizedENR_NS1Vector),np.max(normalizedENR_NS1Vector),100)  
    XcoordnormalizedTrecVector2Swept = np.vstack([normalizedENR_NS1Vector, np.ones(len(normalizedENR_NS1Vector))]).T                           
    pl.plot(normalizedENR_NS1Vector, normalizedENR_NS2Vector , marker='o', label='$(T_{NS2 ON} -T_{NS2 OFF})$', linestyle = 'None',color='blue')
    [A2,B2], residuals, rank, s= np.linalg.lstsq(XcoordnormalizedTrecVector2Swept,  normalizedENR_NS2Vector) # your data x, y to fit    
    pl.plot(TrecVector2Swept, A2*TrecVector2Swept+B2,label='%.4f*$(T_{NS1 ON} -T_{NS1 OFF})$+%.2f, R:%.3f K'%(A2,B2,100*residuals), linewidth = 2.0,color='blue')      
    pl.plot(normalizedENR_NS1Vector,  normalizedENR_NS3Vector , marker='o', label='$(T_{NS3 ON} -T_{NS3 OFF})$', linestyle = 'None',color='green')
    [A3,B3], residuals, rank, s= np.linalg.lstsq(XcoordnormalizedTrecVector2Swept,  normalizedENR_NS3Vector) # your data x, y to fit    
    pl.plot(TrecVector2Swept, A3*TrecVector2Swept+B3,label='%.4f*$(T_{NS1 ON} -T_{NS1 OFF})$+%.2f, R:%.3f K'%(A2,B2,100*residuals), linewidth = 2.0,color='green')      
    pl.grid(True)
    pl.xlabel('$(T_{NS1 ON} -T_{NS1 OFF})$ [K]')
    pl.ylabel(' $(T_{NSx ON} -T_{NSx OFF})$ [K]')
    title='Normalized TNS_ONx-TNS_OFFx Vs NS TNS_ON1-TNS_OFF1 for '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)


 
    
    ENR2=normalizedENR_NS2Vector/normalizedENR_NS1Vector
    ENR3=normalizedENR_NS3Vector/normalizedENR_NS1Vector 


    fignum=8304
    fig = pl.figure(fignum)
    ax = fig.add_subplot(111)
    NSTemperature2=np.array(NSTemperature,dtype=np.float64)
    NSTemperatureVectorSwept=np.linspace(np.min(NSTemperature2),np.max(NSTemperature2),100)  
    XcoordnormalizedTrecVector2Swept = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                           
    pl.plot(NSTemperature, ENR2 , marker='o', label='$(T_{NS2 ON} -T_{NS2 OFF})/(T_{NS1 ON} -T_{NS1 OFF})$', linestyle = 'None',color='blue')
    [A2,B2], residuals, rank, s= np.linalg.lstsq(XcoordnormalizedTrecVector2Swept,  ENR2) # your data x, y to fit    
    pl.plot(NSTemperatureVectorSwept, A2*NSTemperatureVectorSwept+B2,label='%.4f*$T_{ph} Receiver$+%.2f, R:%.3f K'%(A2,B2,100*residuals), linewidth = 2.0,color='blue')      
    pl.plot(NSTemperature, ENR3 , marker='o', label='$(T_{NS3 ON} -T_{NS3 OFF})/(T_{NS1 ON} -T_{NS1 OFF})$', linestyle = 'None',color='green')
    [A3,B3], residuals, rank, s= np.linalg.lstsq(XcoordnormalizedTrecVector2Swept,  ENR3) # your data x, y to fit    
    pl.plot(NSTemperatureVectorSwept, A3*NSTemperatureVectorSwept+B3,label='%.4f*$T_{ph} Receiver$+%.2f, R:%.3f K'%(A3,B3,100*residuals), linewidth = 2.0,color='green')      
    pl.grid(True)
    pl.xlabel('Tph NS [C]')
    pl.ylabel('$(T_{NSx ON} -T_{NSx OFF})/(T_{NS1 ON} -T_{NS1 OFF})$ ')
    title='ENRx Vs Tph NS for '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)

    fignum=8303
    fig = pl.figure(fignum)
    ax = fig.add_subplot(111)
    meanRadTemperatureVector2=np.array(meanRadTemperatureVector,dtype=np.float64)
    meanRadTemperatureVectorSwept=np.linspace(np.min(meanRadTemperatureVector2),np.max(meanRadTemperatureVector2),100)  
    XcoordnormalizedTrecVector2Swept = np.vstack([meanRadTemperatureVector, np.ones(len(meanRadTemperatureVector))]).T                           
    pl.plot(meanRadTemperatureVector, ENR2-(A2*NSTemperature2+B2) , marker='o', label='Residuals $(T_{NS2 ON} -T_{NS2 OFF})/(T_{NS1 ON} -T_{NS1 OFF})$', linestyle = 'None',color='blue')
    pl.plot(meanRadTemperatureVector, ENR3-(A3*NSTemperature2+B3) , marker='o', label='Residuals $(T_{NS3 ON} -T_{NS3 OFF})/(T_{NS1 ON} -T_{NS1 OFF})$', linestyle = 'None',color='green')
    pl.grid(True)
    pl.xlabel('Tph receiver [C]')
    pl.ylabel('Residual $(T_{NSx ON} -T_{NSx OFF})/(T_{NS1 ON} -T_{NS1 OFF})$ ')
    title='Residual ENRx Vs Tph receiver for '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)

    fignum=8302
    fig = pl.figure(fignum)
    TrecVector2=np.array(TrecVector,dtype=np.float64)
    TrecVector2Swept=np.linspace(np.min(TrecVector2),np.max(TrecVector2),100)  
    XcoordnormalizedTrecVector2Swept = np.vstack([TrecVector2, np.ones(len(TrecVector2))]).T                           
    pl.plot(TrecVector, ENR2-(A2*NSTemperature2+B2) , marker='o', label='Residuals $(T_{NS2 ON} -T_{NS2 OFF})/(T_{NS1 ON} -T_{NS1 OFF})$', linestyle = 'None',color='blue')
    pl.plot(TrecVector,  ENR3-(A3*NSTemperature2+B3) , marker='o', label='Residuals $(T_{NS3 ON} -T_{NS3 OFF})/(T_{NS1 ON} -T_{NS1 OFF})$', linestyle = 'None',color='green')
    pl.grid(True)
    pl.xlabel('Trec [k]')
    pl.ylabel('Residual $(T_{NSx ON} -T_{NSx OFF})/(T_{NS1 ON} -T_{NS1 OFF})$ ')
    title='Residual ENRx Vs Trec for '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)




    fignum=8305
    fig = pl.figure(fignum)
    ax = fig.add_subplot(111) 
    XcoordnormalizedENR_NS1Vector = np.vstack([normalizedENR_NS1Vector, np.ones(len(normalizedENR_NS1Vector))]).T                           
    pl.plot(Time,normalizedENR_NS2Vector, marker='o', label='$(T_{NS2 ON} -T_{NS2 OFF})/(T_{NS1 ON} -T_{NS1 OFF})$', linestyle = 'None',color='blue')
    #[A,B], residuals, rank, s= np.linalg.lstsq(XcoordnormalizedENR_NS1Vector,  normalizedENR_NS2Vector) # your data x, y to fit    
    #pl.plot(normalizedENR_NS1Swept, A*normalizedENR_NS1Swept+B,label='%.4f*$(T_{NS1 ON} -T_{NS1 OFF})$+%.2f, R:%.3f K'%(A,B,100*residuals), linewidth = 2.0,color='blue')
    pl.plot(Time,normalizedENR_NS3Vector, marker='o', label='$(T_{NS3 ON} -T_{NS3 OFF})/(T_{NS1 ON} -T_{NS1 OFF})$', linestyle = 'None',color='green')
    #[A,B], residuals, rank, s= np.linalg.lstsq(XcoordnormalizedENR_NS1Vector,  normalizedENR_NS3Vector) # your data x, y to fit    
    #pl.plot(normalizedENR_NS1Swept, A*normalizedENR_NS1Swept+B,label='%.4f*$(T_{NS1 ON} -T_{NS1 OFF})$+%.2f, R:%.3f K'%(A,B,100*residuals), linewidth = 2.0,color='green')
    pl.grid(True)
    pl.xlabel('Time')
    pl.ylabel('$(T_{NSx ON} -T_{NSx OFF})/(T_{NS1 ON} -T_{NS1 OFF})$')
    title='ENRx time series for '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)