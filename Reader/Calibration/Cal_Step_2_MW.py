# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 16:12:27 2014

@author: xbosch
"""
ln2_filename = 'ln2'  # AGW

import os
import sys
import pylab as pl
import matplotlib as mpl
from pylab import *
import numpy as np
import time, datetime
from pathlib import Path

# configfile='./../Core/DataProcessorAux.py'
# sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
# from DataProcessorAux import dataprocess
# configfile='./Core/ThermistorsAux.py'
# sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
# from DataProcessorAux import thermistors
# from scipy.interpolate import griddata
# configfile='./Core/AntennaTemperatureFileAux.py'
# sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
# #from AntennaTemperatureFileAux import CreateAntennaTempeartureFile
# configfile='./../../GeneralPaths.py'
# sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import H5_DATA_BASE_PATH, CVS_FILES_DATA_BASE_PATH,L0b_DATA_PROCESSED_PATH
pathfordata = Path(L0b_DATA_PROCESSED_PATH) / f'{ln2_filename}CVS'
import csv
from scipy.optimize import curve_fit
def f(x, A, B): # this is your 'straight line' y=f(x)
    return A*x + B    


def calstep2():
    RadiometricDataType='mw'
    ChannelsNamesMW=['MW_34_GHz_QV','NotConnected', 'MW_18_GHz_QV', 'MW_24_GHz_QV','MW_34_GHz_QH','NotConnected', 'MW_18_GHz_QH', 'MW_24_GHz_QH']
    ChannelsNamesMMW=['MMW_168_GHz','NotConnected','MMW_90_GHz','MMW_130_GHz']
    ChannelsNamesSND=['SND_183-5_GHz','SND_183-7_GHz', 'SND_183-3_GHz','SND_183-6_GHz','SND_118+0_GHz','SND_118+5_GHz','SND_118+4_GHz', 'SND_118+0.5_GHz','SND_183-2_GHz','SND_183-1_GHz', 'SND_183-8_GHz','SND_183-4_GHz','SND_118+1_GHz','SND_118+3_GHz','SND_118+0.25_GHz', 'SND_118+2_GHz']
    ChannelstoBeExploredMW =[0,1,2,3,4,5,6,7]
    ChannelstoBeExploredMMW =[0,2,3]
    ChannelstoBeExploredSND =[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] 


    ChannelsNames=eval('ChannelsNames' + RadiometricDataType.upper())
    ChannelsToAnalyze=eval('ChannelstoBeExplored' + RadiometricDataType.upper())


    filenameroot='CalibrationFilesAnalysis_ALL_'
    ChannelNameNumber=2


    ################ Preparing the output file
    cvsFileName = ln2_filename
    t=datetime.datetime.now().strftime("%Y_%m_%d_%H%M_%S")
    pathfordata=os.path.join(L0b_DATA_PROCESSED_PATH, cvsFileName+'CVS')
    if not os.path.exists(pathfordata): 
        os.makedirs(pathfordata)
        print('-->',pathfordata, 'has been created')
        
    pathfordata=os.path.join(pathfordata, t+'_'+cvsFileName+'_test_LN2_Trec_model_'+RadiometricDataType+'.csv')
    csvfileOpenWrite = open(pathfordata, 'w', newline='')
    fieldnames=['Channel Name', 'A', 'B', 'RMS']
    writer = csv.DictWriter(csvfileOpenWrite, fieldnames=fieldnames, dialect=csv.excel,  delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, escapechar='\\')
    writer.writeheader()

    ##################################################################### 
    cvsFileName = ln2_filename + 'Out_MW_test'
    FromCVSFile=True
    ##################################################################### 
    pathfordata=os.path.join(L0b_DATA_PROCESSED_PATH, ln2_filename + 'CVS',  cvsFileName+'.csv')
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
    preTN1Vector=[]
    preTN2Vector=[]
    preTN3Vector=[]
    preNDD1Vector=[]
    preNDD2Vector=[]
    preNDD3Vector=[]
    preNS1824TemperatureVector=[]
    preNS34TemperatureVector=[]



    Again=[]; Bgain=[]; Rgain=[]
    ATrec=[];BTrec=[];RTrec=[]
    ANDD2=[];BNDD2=[];RNDD2=[]
    ANDD3=[];BNDD3=[];RNDD3=[]

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
        preTN1Vector.append(row[12])  
        preTN2Vector.append(row[13])  
        preTN3Vector.append(row[14])
        preNDD1Vector.append(row[15])
        preNDD2Vector.append(row[16])
        preNDD3Vector.append(row[17])    
        
        preNS1824TemperatureVector.append(row[18])
        preNS34TemperatureVector.append(row[19])       
        
    for ChannelNameNumber in ChannelsToAnalyze:   
        if np.mod(ChannelNameNumber,4)==1:
            writer.writerow({'Channel Name':ChannelsNames[ChannelNameNumber], 'A':0, 'B':0, 'RMS':0})      

        else:
            matplotlib.pyplot.close("all")
            
            ChannelName=ChannelsNames[ChannelNameNumber]
            print(ChannelName)
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
            TN3Vector=[]
            TN3Vector=[]
            TN3Vector=[]
            NDD1Vector=[]
            NDD2Vector=[]
            NDD3Vector=[]    
            NS1824TemperatureVector=[]
            NS34TemperatureVector=[]    
            
            ## Selecting the channel of interest
            FilenameVector=list( preFilenameVector[i] for i in indexes )
            GPSTimeVector=list( float(preGPSTimeVector[i]) for i in indexes )
            GainVector=list( float(preGainVector[i]) for i in indexes )
            TrecVector=list( float(preTrecVector[i]) for i in indexes )
            AltitudeVector=list( float(preAltitudeVector[i]) for i in indexes )
            LatVector=list( float(preLatVector[i]) for i in indexes )
            LonVector=list( float(preLonVector[i]) for i in indexes )
            ExternalTemperatureVector=list( float(preExternalTemperatureVector[i]) for i in indexes )
            meanRadTemperatureVector=list( float(premeanRadTemperatureVector[i]) for i in indexes )
            stdRadTemperatureVector=list( float(prestdRadTemperatureVector[i]) for i in indexes )
            TN1Vector=list( float(preTN1Vector[i]) for i in indexes )
            TN2Vector=list( float(preTN2Vector[i]) for i in indexes )
            TN3Vector=list( float(preTN3Vector[i]) for i in indexes )    
            NDD1Vector=list( float(preNDD1Vector[i]) for i in indexes ) 
            NDD2Vector=list( float(preNDD2Vector[i]) for i in indexes ) 
            NDD3Vector=list( float(preNDD3Vector[i]) for i in indexes ) 
            
            NS1824TemperatureVector=list(float(preNS1824TemperatureVector[i]) for i in indexes )
            NS34TemperatureVector=list(float(preNS34TemperatureVector[i]) for i in indexes )        
            
            
            if np.mod(ChannelNameNumber,4)==0:
                NSTemperature=NS34TemperatureVector
            else: 
                NSTemperature=NS1824TemperatureVector
            
        
            Time=np.array(GPSTimeVector,dtype=np.float64)
            XvariablemeanRadTemperatureVector=np.array(meanRadTemperatureVector,dtype=np.float64)
            XcoordmeanRadTemperatureVector = np.vstack([XvariablemeanRadTemperatureVector, np.ones(len(XvariablemeanRadTemperatureVector))]).T       
            L=len(XcoordmeanRadTemperatureVector)    
            TemperatureSwept=np.linspace(-5,40,100)

            pathfordata = L0b_DATA_PROCESSED_PATH + f'\\{ln2_filename}CVS'
            
            fignum=2302
            fig = pl.figure(fignum)
            GainVector=np.array(GainVector,dtype=np.float64)
            ax = fig.add_subplot(111)
            pl.plot(meanRadTemperatureVector,GainVector, marker='o', linestyle = 'None', label='Trec',color='blue')
            [Ag2,Bg2], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, GainVector) # your data x, y to fit   
            R=np.sqrt(residuals/L)
            pl.plot(TemperatureSwept, Ag2*TemperatureSwept+Bg2,label='%.4f*T+%.2f, R:%.3f K'%(Ag2,Bg2,R[0]), linewidth = 2.0,color='black')                
            pl.grid(True)
            pl.xlabel('Tph receiver [C]')
            pl.ylabel('Gain [K/v]')
            title='Gain Vs Temperature for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)     
            
            
            fignum=2300
            fig = pl.figure(fignum)
            ax = fig.add_subplot(111)
            b=np.array(GainVector,dtype=np.float64)
            normalizedGain=b /np.mean( b)            
            pl.plot(meanRadTemperatureVector,normalizedGain, marker='o', label='Calibration Gain', linestyle = 'None',color='red')                     
            [Ag,Bg], residualsGain, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedGain) # your data x, y to fit 
            R=np.sqrt(residualsGain/L)*100    
            Again.append(Ag), Bgain.append(Bg), Rgain.append(R[0])    
            pl.plot(TemperatureSwept, Ag*TemperatureSwept+Bg,label='%.4f*T+%.2f, R:%.3f%%'%(Ag,Bg,R[0]), linewidth = 2.0,color='black')    
            pl.grid(True)
            pl.ylim([0.6, 1.3])
            pl.xlabel('Tph receiver [C]')
            pl.ylabel('Gain [normalized]')
            title='Gain Vs Temperature for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)
            
            #error=normalizedGain-(Ag*XvariablemeanRadTemperatureVector+Bg)
            #print 'Residuals Gain:', 100*np.sqrt(np.sum(np.square(error)))/L,100*np.sqrt(np.sum(np.square(error))/L), 100*np.sqrt(residualsGain)/L, 100*np.sum(np.sqrt(np.square(error)))/L
        
            
            fignum=2400
            fig = pl.figure(fignum)
            ax = fig.add_subplot(111)
            b=np.array(TrecVector,dtype=np.float64)
            normalizedTrecVector=b /np.mean( b)                       
            pl.plot(meanRadTemperatureVector,normalizedTrecVector, marker='o', linestyle = 'None', label='Trec',color='blue')
            [At,Bt], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedTrecVector) # your data x, y to fit    
            R=np.sqrt(residuals/L)*100   
            ATrec.append(At), BTrec.append(Bt), RTrec.append(R[0])      
            pl.plot(TemperatureSwept, At*TemperatureSwept+Bt,label='%.4f*T+%.2f, R:%.3f%%'%(At,Bt,R[0]), linewidth = 2.0,color='black')                
            #print 'Residuals Trec:', np.sqrt(np.sum(np.square(normalizedTrecVector-(At*XvariablemeanRadTemperatureVector+Bt)))/len(meanRadTemperatureVector))*100, residuals*100
            pl.grid(True)
            pl.ylim([0.85, 1.15])
            pl.ylim([0.6, 1.3])    
            pl.xlabel('Tph receiver [C]')
            pl.ylabel('Trec [normalized]')
            title='Trec Vs Temperature for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)   
            
            fignum=2401
            fig = pl.figure(fignum)
            TrecVector=np.array(TrecVector,dtype=np.float64)
            ax = fig.add_subplot(111)
            pl.plot(meanRadTemperatureVector,TrecVector, marker='o', linestyle = 'None', label='Trec',color='blue')
            [At2,Bt2], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, TrecVector) # your data x, y to fit    
            R=np.sqrt(residuals/L)    
            ATrec.append(At), BTrec.append(Bt), RTrec.append(R[0]) 
            writer.writerow({'Channel Name':ChannelsNames[ChannelNameNumber], 'A':At2, 'B':Bt2, 'RMS':R[0]})      
                
            pl.plot(TemperatureSwept, At2*TemperatureSwept+Bt2,label='%.4f*T+%.2f, R:%.3f K'%(At2,Bt2,R[0]), linewidth = 2.0,color='black')                
            error=TrecVector-(At2*XvariablemeanRadTemperatureVector+Bt2)
            print(np.sqrt(np.mean(np.square(error))))      
            print('--Residuals Trec:', np.sqrt(np.sum(np.square(error)))/L, np.sqrt(residuals/L))
            pl.grid(True)
            pl.xlabel('Tph receiver [C]')
            pl.ylabel('Trec [K]')
            title='Trec Vs Temperature for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)     
            
            
            fignum=2301
            fig = pl.figure(fignum)
            ax = fig.add_subplot(111)       
            pl.plot(Time-Time[0],100*(normalizedGain-(Ag*XvariablemeanRadTemperatureVector+Bg)), marker='o', label='Gain Residual', linestyle = 'None',color='red')
            pl.plot(Time-Time[0],100*(normalizedTrecVector-(At*XvariablemeanRadTemperatureVector+Bt)), marker='o', label='$T_{REC}$ Residual', linestyle = 'None',color='blue')                      
            pl.grid(True)
            pl.ylim([-2.6, 2.6])
            pl.xlabel('Time [s]')
            pl.ylabel('Residual [%]')
            title='Normalized Gain Error after Compensating for Radiometer Temperature Time Series  '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)    
            
            
            fignum=1300
            fig = pl.figure(fignum)
            ax = fig.add_subplot(111)
            b=np.array(NDD1Vector,dtype=np.float64)
            normalizedNDD1Vector=b /np.mean( b)
            b=np.array(NDD2Vector,dtype=np.float64)
            normalizedNDD2Vector=b /np.mean( b) 
            b=np.array(NDD3Vector,dtype=np.float64)
            normalizedNDD3Vector=b /np.mean( b)                  
            pl.plot(meanRadTemperatureVector,normalizedNDD1Vector, marker='o', label='$NDD_{NS1}$', linestyle = 'None',color='red')                
            pl.plot(meanRadTemperatureVector,normalizedNDD2Vector, marker='o', label='$NDD_{NS2}$', linestyle = 'None',color='blue')
            pl.plot(meanRadTemperatureVector,normalizedNDD3Vector, marker='o', label='$NDD_{NS3}$', linestyle = 'None',color='green')     
            [A,B], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedNDD1Vector) # your data x, y to fit 
            pl.plot(TemperatureSwept, A*TemperatureSwept+B,label='%.4f*T+%.2f, R:%.3f %%'%(A,B,(np.sqrt(residuals/L)*100)[0]), linewidth = 2.0,color='red')
            [A,B], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedNDD2Vector) # your data x, y to fit     
            pl.plot(TemperatureSwept, A*TemperatureSwept+B,label='%.4f*T+%.2f, R:%.3f %%'%(A,B,(np.sqrt(residuals/L)*100)[0]), linewidth = 2.0,color='blue')
            [A,B], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedNDD3Vector) # your data x, y to fit       
            pl.plot(TemperatureSwept, A*TemperatureSwept+B,label='%.4f*T+%.2f, R:%.3f %%'%(A,B,(np.sqrt(residuals/L)*100)[0]), linewidth = 2.0,color='green')  
            pl.grid(True)
            pl.ylim([0.65, 1.5])    
            pl.xlabel('Tph receiver [C]')
            pl.ylabel('Normalized $NDD_{NSx}$ ')
            title='Normalized NDDx Vs Temperature for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)
        
        
            fignum=1301
            fig = pl.figure(fignum)
            ax = fig.add_subplot(111)
            XcoordNSTemperature = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                   
            pl.plot(NSTemperature,TN1Vector, marker='o', label='$T_{NS1}$', linestyle = 'None',color='red')                
            pl.plot(NSTemperature,TN2Vector, marker='o', label='$T_{NS2}$', linestyle = 'None',color='blue')
            pl.plot(NSTemperature,TN3Vector, marker='o', label='$T_{NS3}$', linestyle = 'None',color='green')    
            [A1,B1], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, TN1Vector) # your data x, y to fit
            res = np.sqrt(residuals/L)[0] if len(residuals) == 1 else 0
            pl.plot(TemperatureSwept, A1*TemperatureSwept+B1,label='%.4f*T+%.2f, R:%.2f K'%(A1,B1,res), linewidth = 2.0,color='red')
            [A2,B2], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, TN2Vector) # your data x, y to fit
            res = np.sqrt(residuals/L)[0] if len(residuals) == 1 else 0        
            pl.plot(TemperatureSwept, A2*TemperatureSwept+B2,label='%.4f*T+%.2f, R:%.2f K'%(A2,B2,res), linewidth = 2.0,color='blue')
            [A3,B3], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature,  TN3Vector) # your data x, y to fit 
            res = np.sqrt(residuals/L)[0] if len(residuals) == 1 else 0     
            pl.plot(TemperatureSwept, A3*TemperatureSwept+B3,label='%.4f*T+%.2f, R:%.2f K'%(A3,B3,res), linewidth = 2.0,color='green')  
            pl.grid(True)
            pl.xlabel('Tph NS [C]')
            pl.ylabel('$T_{NS}$ [K]')
            title='TNSx Vs NS Temperature for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)
            
            fignum=1302
            fig = pl.figure(fignum)
            ax = fig.add_subplot(111)
            XcoordNSTemperature = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                   
            pl.plot(NSTemperature,normalizedNDD1Vector, marker='o', label='$NDD_{NS1}$', linestyle = 'None',color='red')                
            pl.plot(NSTemperature,normalizedNDD2Vector, marker='o', label='$NDD_{NS2}$', linestyle = 'None',color='blue')
            pl.plot(NSTemperature,normalizedNDD3Vector, marker='o', label='$NDD_{NS3}$', linestyle = 'None',color='green')    
            [A1,B1], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, normalizedNDD1Vector) # your data x, y to fit
            res = np.sqrt(residuals/L)[0] if len(residuals) == 1 else 0
            pl.plot(TemperatureSwept, A1*TemperatureSwept+B1,label='%.4f*T+%.2f, R:%.3f %%'%(A1,B1,res), linewidth = 2.0,color='red')
            [A2,B2], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, normalizedNDD2Vector) # your data x, y to fit          
            res = np.sqrt(residuals/L)[0] if len(residuals) == 1 else 0
            pl.plot(TemperatureSwept, A2*TemperatureSwept+B2,label='%.4f*T+%.2f, R:%.3f %%'%(A2,B2,res), linewidth = 2.0,color='blue')
            res = np.sqrt(residuals/L)[0] if len(residuals) == 1 else 0
            [A3,B3], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature,  normalizedNDD3Vector) # your data x, y to fit      
            pl.plot(TemperatureSwept, A3*TemperatureSwept+B3,label='%.4f*T+%.2f, R:%.3f %%'%(A3,B3,res), linewidth = 2.0,color='green')  
            pl.grid(True)
            pl.xlabel('Tph NS [C]')
            pl.ylabel('normalized $NDD_{NS}$')
            title='Normalized NDDx Vs NS Temperature for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)
            
        
            fignum=1303
            fig = pl.figure(fignum)
            TrecVector2Swept=np.linspace(np.min(normalizedNDD1Vector),np.max(normalizedNDD1Vector),100)  
            XcoordnormalizedTrecVector2Swept = np.vstack([normalizedNDD1Vector, np.ones(len(normalizedNDD1Vector))]).T                           
            pl.plot(normalizedNDD1Vector, normalizedNDD2Vector , marker='o', label='$NDD_{NS2}$', linestyle = 'None',color='blue')
            pl.plot(normalizedNDD1Vector,  normalizedNDD3Vector , marker='o', label='$(NDD_{NS3})$', linestyle = 'None',color='green')
            [A2,B2], residuals2, rank, s= np.linalg.lstsq(XcoordnormalizedTrecVector2Swept,  normalizedNDD2Vector) # your data x, y to fit    
            R=np.sqrt(residuals2/L)*100    
            ANDD2.append(A2), BNDD2.append(B2), RNDD2.append(R[0])
            pl.plot(TrecVector2Swept, A2*TrecVector2Swept+B2,label='%.4f*$NDD_{NS1}$+%.2f, R:%.3f %%'%(A2,B2,R[0]), linewidth = 2.0,color='blue')      
            [A3,B3], residuals3, rank, s= np.linalg.lstsq(XcoordnormalizedTrecVector2Swept,  normalizedNDD3Vector) # your data x, y to fit    
            R=np.sqrt(residuals3/L)*100
            ANDD3.append(A3), BNDD3.append(B3), RNDD3.append(R[0])
            pl.plot(TrecVector2Swept, A3*TrecVector2Swept+B3,label='%.4f*$NDD_{NS1}$+%.2f, R:%.3f %%'%(A2,B2,R[0]), linewidth = 2.0,color='green')      
            pl.grid(True)
            pl.xlabel('$NDD_{NS1}$')
            pl.ylabel('$NDD_{NSx}$')
            
            
            
            title='Normalized NDDx Vs NS NDD1 for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)
        
        
        
            
            ENR2=normalizedNDD2Vector/normalizedNDD1Vector
            ENR3=normalizedNDD3Vector/normalizedNDD1Vector 
        
        
            fignum=8304
            fig = pl.figure(fignum)
            ax = fig.add_subplot(111)
            NSTemperature2=np.array(NSTemperature,dtype=np.float64)
            NSTemperatureVectorSwept=np.linspace(np.min(NSTemperature2),np.max(NSTemperature2),100)  
            XcoordnormalizedTrecVector2Swept = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                           
            pl.plot(NSTemperature, ENR2 , marker='o', label='$NDDR_{21}$', linestyle = 'None',color='blue')
            [A2,B2], residualsNDDR2, rank, s= np.linalg.lstsq(XcoordnormalizedTrecVector2Swept,  ENR2) # your data x, y to fit
            res = np.sqrt(residuals/L)[0] if len(residuals) == 1 else 0
            pl.plot(NSTemperatureVectorSwept, A2*NSTemperatureVectorSwept+B2,label='%.4f*$T_{ph} NS$+%.2f, R:%.3f %%'%(A2,B2,res), linewidth = 2.0,color='blue')      
            pl.plot(NSTemperature, ENR3 , marker='o', label='$NDDR_{31}$', linestyle = 'None',color='green')
            [A3,B3], residualsNDDR3, rank, s= np.linalg.lstsq(XcoordnormalizedTrecVector2Swept,  ENR3) # your data x, y to fit
            res = np.sqrt(residuals/L)[0] if len(residuals) == 1 else 0
            pl.plot(NSTemperatureVectorSwept, A3*NSTemperatureVectorSwept+B3,label='%.4f*$T_{ph} NS$+%.2f, R:%.3f %%'%(A3,B3,res), linewidth = 2.0,color='green')      
            pl.grid(True)
            pl.xlabel('Tph NS [C]')
            pl.ylabel('$NDDR_{X1}$ ')
            title='NDDRx Vs Tph NS for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)
        
            fignum=8303
            fig = pl.figure(fignum)
            ax = fig.add_subplot(111)
            meanRadTemperatureVector2=np.array(meanRadTemperatureVector,dtype=np.float64)
            meanRadTemperatureVectorSwept=np.linspace(np.min(meanRadTemperatureVector2),np.max(meanRadTemperatureVector2),100)  
            XcoordnormalizedTrecVector2Swept = np.vstack([meanRadTemperatureVector, np.ones(len(meanRadTemperatureVector))]).T                           
            pl.plot(meanRadTemperatureVector, ENR2-(A2*NSTemperature2+B2) , marker='o', label='Residuals $NDDR_{21}$', linestyle = 'None',color='blue')
            pl.plot(meanRadTemperatureVector, ENR3-(A3*NSTemperature2+B3) , marker='o', label='Residuals $NDDR_{31}$', linestyle = 'None',color='green')
            pl.grid(True)
            pl.xlabel('Tph receiver [C]')
            pl.ylabel('Residual $NDDR_{x1}$ ')
            title='Residual NDDRx Vs Tph receiver for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)
        
            fignum=8302
            fig = pl.figure(fignum)
            TrecVector2=np.array(TrecVector,dtype=np.float64)
            TrecVector2Swept=np.linspace(np.min(TrecVector2),np.max(TrecVector2),100)  
            XcoordnormalizedTrecVector2Swept = np.vstack([TrecVector2, np.ones(len(TrecVector2))]).T                           
            pl.plot(TrecVector, ENR2-(A2*NSTemperature2+B2) , marker='o', label='Residuals $NDDR_{21}$', linestyle = 'None',color='blue')
            pl.plot(TrecVector,ENR3-(A3*NSTemperature2+B3) , marker='o', label='Residuals $NDDR_{31}$', linestyle = 'None',color='green')
            pl.grid(True)
            pl.xlabel('Trec [k]')
            pl.ylabel('Residual $NDDR_{NSx1}$ ')
            title='Residual NDDRx Vs Trec for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)
        
        
            fignum=8305
            fig = pl.figure(fignum)
            ax = fig.add_subplot(111)                  
            pl.plot(Time,ENR2-(A2*NSTemperature2+B2), marker='o', label='Residuals $NDDR_{21}$', linestyle = 'None',color='blue')
            pl.plot(Time,ENR3-(A3*NSTemperature2+B3), marker='o', label='Residuals $NDDR_{31}$', linestyle = 'None',color='green')
            pl.grid(True)
            pl.xlabel('Time')
            pl.ylabel('Reiduals $NDDR_{x1}$')
            title='Residuals NDDRx time series for '+ ChannelName
            fig.suptitle(title, fontsize=10)
            pl.legend(loc = 'best',shadow = True)
            pl.show(block=False) 
            figfilename =os.path.join(pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
            fig.savefig(figfilename)
        
    csvfileOpenWrite.close()    
    print( Again, Bgain, Rgain)     
    print( ATrec, BTrec, RTrec)
    print( ANDD2, BNDD2, RNDD2)
    print( ANDD3, BNDD3, RNDD3)       
    print('FINISHED CAL STEP 2!')
