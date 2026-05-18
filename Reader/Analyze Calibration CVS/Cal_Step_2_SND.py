
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
configfile='./../Core/DataProcessorAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from DataProcessorAux import dataprocess
configfile='./Core/ThermistorsAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from DataProcessorAux import thermistors
from scipy.interpolate import griddata
#configfile='./Core/AntennaTemperatureFileAux.py'
#sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
#from AntennaTemperatureFileAux import CreateAntennaTempeartureFile
configfile='./Core/GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import H5_DATA_BASE_PATH, CVS_FILES_DATA_BASE_PATH,L0b_DATA_PROCESSED_PATH
import csv
from scipy.optimize import curve_fit
def f(x, A, B): # this is your 'straight line' y=f(x)
    return A*x + B    

RadiometricDataType='SND'
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
cvsFileName='BASCII LN2 Calibration test'
t=datetime.datetime.now().strftime("%Y_%m_%d_%H%M_%S")
pathfordata=os.path.join(L0b_DATA_PROCESSED_PATH, cvsFileName+'CVS')
if not os.path.exists(pathfordata): 
    os.makedirs(pathfordata)
    print( '-->',pathfordata, 'has been created')
    
pathfordata=os.path.join(pathfordata, t+'_'+cvsFileName+'_WCFC_LN2_Trec_model_'+RadiometricDataType+'.csv')
csvfileOpenWrite = open(pathfordata, 'w', newline='')
fieldnames=['Channel Name', 'A', 'B', 'RMS']
writer = csv.DictWriter(csvfileOpenWrite, fieldnames=fieldnames, dialect=csv.excel,  delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, escapechar='\\')
writer.writeheader()



##################################################################### 
cvsFileName='BASCII LN2 Calibration testOut_SND_All_v005'
FromCVSFile=True
##################################################################### 
pathfordata=os.path.join(L0b_DATA_PROCESSED_PATH, 'BASCII LN2 Calibration testCVS',  cvsFileName+'.csv')
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
preMultuiplierTemperatureVector=[]      



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
    preMultuiplierTemperatureVector.append(row[16])  

    
for ChannelNameNumber in ChannelsToAnalyze:   

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
    MultuiplierTemperatureVector=[]
    
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
    MultuiplierTemperatureVector=list( preMultuiplierTemperatureVector[i] for i in indexes ) 


    
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
    pl.plot(XvariablemeanRadTemperatureVector,normalizedGain, marker='o', label='Calibration Gain', linestyle = 'None',color='red')                     
    [Ag,Bg], residualsGain, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedGain) # your data x, y to fit 
    R=np.sqrt(residualsGain/L)*100
    Again.append(Ag), Bgain.append(Bg), Rgain.append(R[0])    
    pl.plot(TemperatureSwept, Ag*TemperatureSwept+Bg,label='%.4f*T+%.2f, R:%.3f%%'%(Ag,Bg,R[0]), linewidth = 2.0,color='black')    
    pl.grid(True)
    #pl.ylim([0, 3])
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
    pl.plot(XvariablemeanRadTemperatureVector,normalizedTrecVector, marker='o', linestyle = 'None', label='Trec',color='blue')
    [At,Bt], residuals, rank, s= np.linalg.lstsq(XcoordmeanRadTemperatureVector, normalizedTrecVector) # your data x, y to fit    
    R=np.sqrt(residuals/L)*100    
    ATrec.append(At), BTrec.append(Bt), RTrec.append(R[0])      
    
    pl.plot(TemperatureSwept, At*TemperatureSwept+Bt,label='%.4f*T+%.2f, R:%.3f%%'%(At,Bt,R[0]), linewidth = 2.0,color='black')                
    #print 'Residuals Trec:', np.sqrt(np.sum(np.square(normalizedTrecVector-(At*XvariablemeanRadTemperatureVector+Bt)))/len(meanRadTemperatureVector))*100, residuals*100
    
    pl.grid(True)
    #pl.ylim([0.6, 1.5])
    pl.ylim([0, 3])    
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
    print( np.sqrt(np.mean(np.square(error))))      
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
  #  pl.ylim([-2.6, 2.6])
    pl.xlabel('Time [s]')
    pl.ylabel('Residual [%]')
    title='Normalized Gain Error after Compensating for Radiometer Temperature Time Series  '+ ChannelName
    fig.suptitle(title, fontsize=10)
    pl.legend(loc = 'best',shadow = True)
    pl.show(block=False) 
    figfilename =os.path.join(pathfordata,filenameroot+'_'+str(fignum)+'_'+title.replace(" ", "_")+'.png')
    fig.savefig(figfilename)    

########################################################
########################################################
########################################################
########################################################
    x=np.array(MultuiplierTemperatureVector, dtype=float64)
    y=np.array(meanRadTemperatureVector, dtype=float64)
    z=np.array(normalizedTrecVector, dtype=float64)

    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
    import matplotlib.pyplot as plt
    from scipy.interpolate import griddata
    import numpy as np

    ax = plt.figure().add_subplot(projection='3d')

    print( type(x))
    print( np.max(x),np.min(x), np.max(y), np.min(y), )
    xi = np.linspace(np.min(x), np.max(x))
    yi = np.linspace(np.min(y), np.max(y))

    X, Y = np.meshgrid(xi, yi)
    Z = griddata(np.vstack((x,y)).T,z,(X,Y),method='nearest')

    surf = ax.plot_surface(X, Y, Z, rstride=5, cstride=5, cmap=cm.jet, linewidth=1, antialiased=True)

    ax.set_zlim3d(np.min(Z), np.max(Z))
    fig.colorbar(surf)

    plt.show()

    fignum=92401
    MatrixA=np.vstack([XvariablemeanRadTemperatureVector, MultuiplierTemperatureVector,  np.ones(len(XvariablemeanRadTemperatureVector))]).T      
    Time=np.array(GPSTimeVector,dtype=np.float64)
    XvariablemeanRadTemperatureVector=np.array(meanRadTemperatureVector,dtype=np.float64)
    XcoordmeanRadTemperatureVector = np.vstack([XvariablemeanRadTemperatureVector, np.ones(len(XvariablemeanRadTemperatureVector))]).T       
    L=len(XcoordmeanRadTemperatureVector)    

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
    print( np.sqrt(np.mean(np.square(error))))      
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
        
    
   
csvfileOpenWrite.close()     
print( Again, Bgain, Rgain)     
print( ATrec, BTrec, RTrec)

print('FINISHED!')
