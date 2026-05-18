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
import time, datetime
configfile='./../Core/DataProcessorAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from DataProcessorAux import dataprocess
configfile='./Core/ThermistorsAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from DataProcessorAux import thermistors
from scipy.interpolate import griddata
configfile='./Core/AntennaTemperatureFileAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
#from AntennaTemperatureFileAux import CreateAntennaTempeartureFile
configfile='./../../GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import H5_DATA_BASE_PATH, CVS_FILES_DATA_BASE_PATH,L0b_DATA_PROCESSED_PATH
import csv
from scipy.optimize import curve_fit
def f(x, A, B): # this is your 'straight line' y=f(x)
    return A*x + B      

RadiometricDataType='MMW'
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

################ Preparing the output file
cvsFileName='MM_Vald_test_LN2'
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
cvsFileName='MM_Vald_test_LN2Out_MMW_test'
FromCVSFile=True
##################################################################### 
pathfordata=os.path.join(L0b_DATA_PROCESSED_PATH, 'MM_Vald_test_LN2CVS',  cvsFileName+'.csv')
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
preTREF_iVector=[] 
preTREF_NS1Vector=[]
preTANT_iVector=[] 
preTANT_NS1Vector=[]
preNDDREF_iVector=[]
preNDDREF_NS1Vector=[]
preNDDANT_iVector=[]
preNDDANT_NS1Vector=[]      



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
    preTREF_iVector.append(row[12])  
    preTREF_NS1Vector.append(row[13])  
    preTANT_iVector.append(row[14])  
    preTANT_NS1Vector.append(row[15])      
    preNDDREF_iVector.append(row[16])
    preNDDREF_NS1Vector.append(row[17])
    preNDDANT_iVector.append(row[18])
    preNDDANT_NS1Vector.append(row[19])     
        
    
for ChannelNameNumber in [0,1,2,3]:  
    
    print(np.mod(ChannelNameNumber,4))
    if np.mod(ChannelNameNumber,4)==1:
        print( "sssssssssssss")
        writer.writerow({'Channel Name':ChannelsNames[ChannelNameNumber], 'A':0, 'B':0, 'RMS':0})      

    else:
       
        matplotlib.pyplot.close("all")
        
        ChannelName=ChannelsNames[ChannelNameNumber]
        print( ChannelName)
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
        TREF_iVector=[]
        TREF_NS1Vector=[] 
        TANT_iVector=[]
        TANT_NS1Vector=[]     
        NDDREF_iVector=[]
        NDDREF_NS1Vector=[]
        NDDANT_iVector=[]
        NDDANT_NS1Vector=[]   
    
        
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
        TREF_iVector=list( preTREF_iVector[i] for i in indexes ) 
        TREF_NS1Vector=list( preTREF_NS1Vector[i] for i in indexes )  
        TANT_iVector=list( preTANT_iVector[i] for i in indexes ) 
        TANT_NS1Vector=list( preTANT_NS1Vector[i] for i in indexes )     
        NDDREF_iVector=list( preNDDREF_iVector[i] for i in indexes )
        NDDREF_NS1Vector=list( preNDDREF_NS1Vector[i] for i in indexes )
        NDDANT_iVector=list( preNDDANT_iVector[i] for i in indexes )
        NDDANT_NS1Vector=list( preNDDANT_NS1Vector[i] for i in indexes )     
        
        NSTemperature=meanRadTemperatureVector
        
     
        
    
        Time=np.array(GPSTimeVector,dtype=np.float64)
        XvariablemeanRadTemperatureVector=np.array(meanRadTemperatureVector,dtype=np.float64)
        XcoordmeanRadTemperatureVector = np.vstack([XvariablemeanRadTemperatureVector, np.ones(len(XvariablemeanRadTemperatureVector))]).T       
        L=len(XcoordmeanRadTemperatureVector)    
        TemperatureSwept=np.linspace(-5,40,100)
        pathfordata='E:\\HAMMR\\Control and Processing Software\\acqsystem\\Reader\\Results\\L0bdata\\WCFC LN2 Calibration Points 2CVS'
        
        
        
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
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
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
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
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
        print( np.sqrt(np.mean(np.square(error))) )     
        print( '--Residuals Trec:', np.sqrt(np.sum(np.square(error)))/L, np.sqrt(residuals/L))
        pl.grid(True)
        pl.xlabel('Tph receiver [C]')
        pl.ylabel('Trec [K]')
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
        pl.ylim([-2.6, 2.6])
        pl.xlabel('Time [s]')
        pl.ylabel('Residual [%]')
        title='Normalized Gain Error after Compensating for Radiometer Temperature Time Series  '+ ChannelName
        fig.suptitle(title, fontsize=10)
        pl.legend(loc = 'best',shadow = True)
        pl.show(block=False) 
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig.savefig(figfilename)    
        
        
        fignum=1300
        fig = pl.figure(fignum)
        ax = fig.add_subplot(111)
        
        
            
    
            
        b=np.array(NDDREF_NS1Vector,dtype=np.float64)
        normalizedNDDREF_NS1Vector=b /np.mean( b)
        b=np.array(NDDANT_NS1Vector,dtype=np.float64)
        normalizedNDDANT_NS1Vector=b /np.mean( b)
        b=np.array(NDDREF_iVector,dtype=np.float64)
        normalizedNDDREF_iVector=b /np.mean( b)
        b=np.array(NDDANT_iVector,dtype=np.float64)
        normalizedNDDANT_iVector=b /np.mean( b) 
                    
        pl.plot(meanRadTemperatureVector,normalizedNDDREF_NS1Vector, marker='o', label='$NDD_{REF}$', linestyle = 'None',color='red')                
        pl.plot(meanRadTemperatureVector,normalizedNDDANT_NS1Vector, marker='o', label='$NDD_{ANT}$', linestyle = 'None',color='blue')
        #[A,B], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedNDDREF_NS1Vector) # your data x, y to fit 
        #pl.plot(TemperatureSwept, A*TemperatureSwept+B,label='%.4f*T+%.2f, R:%.3f %%'%(A,B,np.sqrt(residuals)*100/len(XcoordmeanRadTemperatureVector )), linewidth = 2.0,color='red')
        #[A,B], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedNDDANT_NS1Vector) # your data x, y to fit     
        #pl.plot(TemperatureSwept, A*TemperatureSwept+B,label='%.4f*T+%.2f, R:%.3f %%'%(A,B,np.sqrt(residuals)*100/len(XcoordmeanRadTemperatureVector )), linewidth = 2.0,color='blue')
        pl.grid(True)
        pl.ylim([0.65, 1.5])    
        pl.xlabel('Tph receiver [C]')
        pl.ylabel('Normalized $NDD_{NS}$ ')
        title='Normalized NDDx Vs Temperature for '+ ChannelName
        fig.suptitle(title, fontsize=10)
        pl.legend(loc = 'best',shadow = True)
        pl.show(block=False) 
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig.savefig(figfilename)
    
    
        fignum=1301
        fig = pl.figure(fignum)
        ax = fig.add_subplot(111)
        XcoordNSTemperature = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                   
        pl.plot(NSTemperature,TREF_NS1Vector, marker='o', label='$T_{REF}$', linestyle = 'None',color='red')                
        pl.plot(NSTemperature,TANT_NS1Vector, marker='o', label='$T_{ANT}$', linestyle = 'None',color='blue') 
        #[A1,B1], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, TREF_NS1Vector) # your data x, y to fit           
        #pl.plot(TemperatureSwept, A1*TemperatureSwept+B1,label='%.4f*T+%.2f, R:%.2f K'%(A1,B1,np.sqrt(residuals)/len(XcoordmeanRadTemperatureVector )), linewidth = 2.0,color='red')
        #[A2,B2], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, TANT_NS1Vector) # your data x, y to fit          
        #pl.plot(TemperatureSwept, A2*TemperatureSwept+B2,label='%.4f*T+%.2f, R:%.2f K'%(A2,B2,np.sqrt(residuals)/len(XcoordmeanRadTemperatureVector )), linewidth = 2.0,color='blue')
        pl.grid(True)
        pl.xlabel('Tph NS [C]')
        pl.ylabel('$T_{NS}$ [K]')
        title='TNSx Vs NS Temperature for '+ ChannelName
        fig.suptitle(title, fontsize=10)
        pl.legend(loc = 'best',shadow = True)
        pl.show(block=False) 
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig.savefig(figfilename)
        
        fignum=1302
        fig = pl.figure(fignum)
        ax = fig.add_subplot(111)
        XcoordNSTemperature = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                   
        pl.plot(NSTemperature,normalizedNDDREF_NS1Vector, marker='o', label='$NDD_{REF}$', linestyle = 'None',color='red')                
        pl.plot(NSTemperature,normalizedNDDANT_NS1Vector, marker='o', label='$NDD_{ANT}$', linestyle = 'None',color='blue')
        #[A1,B1], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, normalizedNDDREF_NS1Vector) # your data x, y to fit           
        #pl.plot(TemperatureSwept, A1*TemperatureSwept+B1,label='%.4f*T+%.2f, R:%.3f %%'%(A1,B1,np.sqrt(residuals)*100/len(XcoordmeanRadTemperatureVector )), linewidth = 2.0,color='red')
        #[A2,B2], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, normalizedNDDANT_NS1Vector) # your data x, y to fit          
        #pl.plot(TemperatureSwept, A2*TemperatureSwept+B2,label='%.4f*T+%.2f, R:%.3f %%'%(A2,B2,np.sqrt(residuals)*100/len(XcoordmeanRadTemperatureVector )), linewidth = 2.0,color='blue')
        pl.grid(True)
        pl.xlabel('Tph NS [C]')
        pl.ylabel('normalized $NDD_{NS}$')
        title='Normalized NDDx Vs NS Temperature for '+ ChannelName
        fig.suptitle(title, fontsize=10)
        pl.legend(loc = 'best',shadow = True)
        pl.show(block=False) 
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig.savefig(figfilename)
         
     
        fignum=1303
        fig = pl.figure(fignum)
        TrecVector2Swept=np.linspace(np.min(normalizedNDDREF_NS1Vector),np.max(normalizedNDDREF_NS1Vector),100)  
        XcoordnormalizedTrecVector2Swept = np.vstack([normalizedNDDREF_NS1Vector, np.ones(len(normalizedNDDREF_NS1Vector))]).T                           
        #pl.plot(normalizedNDDREF_NS1Vector, normalizedNDDANT_NS1Vector , marker='o', label='$NDD_{ANT}$', linestyle = 'None',color='blue')
        #[A2,B2], residuals2, rank, s= np.linalg.lstsq(XcoordnormalizedTrecVector2Swept,  normalizedNDDANT_NS1Vector) # your data x, y to fit    
        #R=np.sqrt(residuals2)*100/L    
        #ANDD2.append(A2), BNDD2.append(B2), RNDD2.append(R[0])
        #pl.plot(TrecVector2Swept, A2*TrecVector2Swept+B2,label='%.4f*$NDD_{REF}$+%.2f, R:%.3f %%'%(A2,B2,R[0]), linewidth = 2.0,color='blue')      
        pl.grid(True)
        pl.xlabel('$NDD_{REF}$')
        pl.ylabel('$NDD_{ANT}$') 
        title='Normalized NDD_ANT Vs NS NDD_REF for '+ ChannelName
        fig.suptitle(title, fontsize=10)
        pl.legend(loc = 'best',shadow = True)
        pl.show(block=False) 
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig.savefig(figfilename)
    
    
        fignum=1304
        fig = pl.figure(fignum)
        ax = fig.add_subplot(111)
        XcoordNSTemperature = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                   
        #pl.plot(NSTemperature,normalizedNDDREF_iVector, marker='o', label='$NDD_{REF} i$', linestyle = 'None',color='red')                
        #pl.plot(NSTemperature,normalizedNDDANT_iVector, marker='o', label='$NDD_{ANT} i$', linestyle = 'None',color='blue')
        #[A1,B1], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, normalizedNDDREF_iVector) # your data x, y to fit           
        #pl.plot(TemperatureSwept, A1*TemperatureSwept+B1,label='%.4f*T+%.2f, R:%.3f %%'%(A1,B1,np.sqrt(residuals)*100/len(XcoordmeanRadTemperatureVector )), linewidth = 2.0,color='red')
        #[A2,B2], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, normalizedNDDANT_iVector) # your data x, y to fit          
        #pl.plot(TemperatureSwept, A2*TemperatureSwept+B2,label='%.4f*T+%.2f, R:%.3f %%'%(A2,B2,np.sqrt(residuals)*100/len(XcoordmeanRadTemperatureVector )), linewidth = 2.0,color='blue')
        pl.grid(True)
        pl.xlabel('Tph NS [C]')
        pl.ylabel('normalized Isolated Port $NDD_{NS}$')
        title='Normalized Isolated Port NDDx Vs Receiver Temperature for '+ ChannelName
        fig.suptitle(title, fontsize=10)
        pl.legend(loc = 'best',shadow = True)
        pl.show(block=False) 
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig.savefig(figfilename)
    
        fignum=1305
        fig = pl.figure(fignum)
        ax = fig.add_subplot(111)
        XcoordNSTemperature = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                   
        pl.plot(NSTemperature,TREF_iVector, marker='o', label='$T_{REF} isolated$', linestyle = 'None',color='red')                
        pl.plot(NSTemperature,TANT_iVector, marker='o', label='$T_{ANT} isolated$', linestyle = 'None',color='blue')
        #[A1,B1], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, TREF_iVector) # your data x, y to fit           
        #pl.plot(TemperatureSwept, A1*TemperatureSwept+B1,label='%.4f*T+%.2f, R:%.3f K'%(A1,B1,np.sqrt(residuals)*100/len(XcoordmeanRadTemperatureVector )), linewidth = 2.0,color='red')
        #[A2,B2], residuals, rank, s= np.linalg.lstsq(XcoordNSTemperature, TANT_iVector) # your data x, y to fit          
        #pl.plot(TemperatureSwept, A2*TemperatureSwept+B2,label='%.4f*T+%.2f, R:%.3f K'%(A2,B2,np.sqrt(residuals)*100/len(XcoordmeanRadTemperatureVector )), linewidth = 2.0,color='blue')
        pl.grid(True)
        pl.xlabel('Tph NS [C]')
        pl.ylabel('Isolated Port $T_{NS}$ [K]')
        title='Normalized Isolated Port TNSx Vs Receiver Temperature for '+ ChannelName
        fig.suptitle(title, fontsize=10)
        pl.legend(loc = 'best',shadow = True)
        pl.show(block=False) 
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig.savefig(figfilename)
    
        
        #ENR2=normalizedNDDANT_NS1Vector/normalizedNDDREF_NS1Vector
    
    
        fignum=8304
        fig = pl.figure(fignum)
        ax = fig.add_subplot(111)
        NSTemperature2=np.array(NSTemperature,dtype=np.float64)
        NSTemperatureVectorSwept=np.linspace(np.min(NSTemperature2),np.max(NSTemperature2),100)  
        XcoordnormalizedTrecVector2Swept = np.vstack([NSTemperature, np.ones(len(NSTemperature))]).T                           
        #pl.plot(NSTemperature, ENR2 , marker='o', label='$NDDR_{ANT/REF}$', linestyle = 'None',color='blue')
        #[A2,B2], residualsNDDR2, rank, s= np.linalg.lstsq(XcoordnormalizedTrecVector2Swept,  ENR2) # your data x, y to fit    
        #pl.plot(NSTemperatureVectorSwept, A2*NSTemperatureVectorSwept+B2,label='%.4f*$T_{ph} NS$+%.2f, R:%.3f %%'%(A2,B2,np.sqrt(residuals/L)*100), linewidth = 2.0,color='blue')      
        pl.grid(True)
        pl.xlabel('Tph NS [C]')
        pl.ylabel('$NDDR_{ANT/REF}$ ')
        title='NDDRx Vs Tph NS for '+ ChannelName
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
        #pl.plot(meanRadTemperatureVector, ENR2-(A2*NSTemperature2+B2) , marker='o', label='Residuals $NDDR_{21}$', linestyle = 'None',color='blue')
        pl.grid(True)
        pl.xlabel('Tph receiver [C]')
        pl.ylabel('Residual $NDDR_{ANT/REF}$ ')
        title='Residual NDDRx Vs Tph receiver for '+ ChannelName
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
        #pl.plot(TrecVector, ENR2-(A2*NSTemperature2+B2) , marker='o', label='Residuals $NDDR_{21}$', linestyle = 'None',color='blue')
        pl.grid(True)
        pl.xlabel('Trec [k]')
        pl.ylabel('Residual $NDDR_{ANT/REF}$ ')
        title='Residual NDDRx Vs Trec for '+ ChannelName
        fig.suptitle(title, fontsize=10)
        pl.legend(loc = 'best',shadow = True)
        pl.show(block=False) 
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig.savefig(figfilename)
    
    
        fignum=8305
        fig = pl.figure(fignum)
        ax = fig.add_subplot(111)                  
        #pl.plot(Time,ENR2-(A2*NSTemperature2+B2), marker='o', label='Residuals $NDDR_{21}$', linestyle = 'None',color='blue')
        pl.grid(True)
        pl.xlabel('Time')
        pl.ylabel('Reiduals $NDDR_{ANT/REF}$')
        title='Residuals NDDRx time series for '+ ChannelName
        fig.suptitle(title, fontsize=10)
        pl.legend(loc = 'best',shadow = True)
        pl.show(block=False) 
        figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
        fig.savefig(figfilename)
 
       
csvfileOpenWrite.close()        
print( Again, Bgain, Rgain )    
print( ATrec, BTrec, RTrec)
print( ANDD2, BNDD2, RNDD2)

print('FINISHED!!!')