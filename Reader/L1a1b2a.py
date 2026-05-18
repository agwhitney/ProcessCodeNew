# -*- coding: utf-8 -*-
""" 
Created on Thu Dec 18 16:22:15 2014

@author: xbosch
"""
import os
import sys
import pylab as pl
configfile='./Core/PL1a.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from PL1a import P_L1a
configfile='./Core/PL1b.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from PL1b import P_L1b
configfile='./Core/PL2a.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from PL2a import P_L2a
##############################################################################
##############################################################################
## L1a Parameters
PlotAngularImage=True
PlotTipingCurve=False
DisplayAuxData=True
ExtendedData=True
FlagsL1a={"ExtendedData":ExtendedData, "PlotAngularImage":PlotAngularImage, "PlotTipingCurve":PlotTipingCurve, "DisplayAuxData":DisplayAuxData}
ChannelSetToAnalyzeVector=['MW','MMW','SND']
CalibrationFilesNames={'MW': '2014_12_18_1548_47_WCFC LN2 Calibration Points 2_WCFC_LN2_Trec_model_MW','MMW':'2014_12_18_1541_36_WCFC LN2 Calibration Points 2_WCFC_LN2_Trec_model_MMW', 'SND':'2014_12_18_1552_16_WCFC LN2 Calibration Points 2_WCFC_LN2_Trec_model_SND' }
TotalSecondsToAnalyzeVector=[300]   # Time for calibration and data processing files, respectevily. 
AngularAverageDegrees=1             # Mimimum resolution 0.0225, one motor sample per sample, i.e: no averaging
sixtyHertzFilter = [True]           # The 60 Hz filter for the calibration and the data files, respectevil. Only has effect for the SND channels. -- **Recomendation: Do not change it** .
##############################################################################
## L1b Parameters
CreateKMLData=True
mapping=True 
FlagsL1b={"CreateKMLData":CreateKMLData, "mapping":mapping}
InitialTime=0
FinalTime=299
El=45
GroundAltitude=0 # Sea Level. Overground you should provide an estimate of the height MSL otherwise the projection will not match the map
ChannelVectorToAnalyse=['18_GHz_QH','90_GHz','168_GHz','130_GHz','34_GHz_QH','34_GHz_QV','18_GHz_QV','24_GHz_QH','24_GHz_QV','118p0_25_GHz', '118p0_5_GHz','118p1_GHz','118p2_GHz','118p3_GHz','118p4_GHz','118p5_GHz', '183m1_GHz', '183m2_GHz','183m3_GHz', '183m4_GHz','183m5_GHz', '183m6_GHz','183m7_GHz', '183m8_GHz']#,'118p5_GHz'] #,'18_GHz_QH', '118p5_GHz']        
##############################################################################
## L2a Parameters
RetrievalMatlabFunction='HAMMR_retrieval_alg_XBmodified_V003'
CreateKMLData=False
MAP_LatLon=False 
MAP_UTM=False

## Save Antenna temperature Options
### MW, MMW, SND
AntennaTemperatureSavingVector={"MW":True, "MMW": True, "SND":True}

## Display options
PD=[5.5, 13 ] 
CLS=[0.4,1.2]
WS=[0, 50]


##############################################################################
GroundAltitude=0
CVSfilenamebatch_D8_SJR='Day8_B_SJR'
CVSfilenamebatch_D6_SJR='Day6_C_SJR_at_Dusk'
##############################################################################
#GroundAltitude=0; 	  CVS=['Day3_B_GoingToStockton', 'Day3_C_SJR', 'Day2','Day3_A_GoingToStockton'] #,   
#GroundAltitude=0;    CVS=['Day4_C_GoingToCrescentCityDescending', 'Day4_D_GoingToSalem', 'Day4_E_GoingToSalemOverLandDescending', 'Day4_A_SJR', 'Day4_B_GoingToCrescentCity','Day3_A_GoingToStockton']#, 
#GroundAltitude=0;    CVS=['Day8_B_SJR', 'Day8_C_GoingToSanLuisObispo', 'Day8_D_GoingToCamarillo', 'Day9_CamarilloMarineLayer','Day8_A_OverlandGoingToSJR']#, 
#GroundAltitude=0;    CVS=['Day10_B_TransitToMamooth', 'Day10_A_CamarilloCoast']
#GroundAltitude=0;    CVS=['Day5_A_GoingToCanadianBorder', 'Day5_B_DescendingOverTheSea', 'Day5_C_SeatleAreaAndBack', 'Day6_A_GoingSouthFromSalem', 'Day6_B_GoingSouthToCarlsonCity', 'Day6_C_SJR_at_Dusk', 'Day6_D_Overland_Night']
#GroundAltitude=1850; CVS=['Day7_A_TransitToTahoe', 'Day7_B_LakeTahoe']
GroundAltitude=0; 	  CVS=['Day3_C_SJR']
#GroundAltitude=1946; CVS=['Day7_C_TransitToMono', 'Day7_D_MonoLake', 'Day7_E_TransitToCarslonCity','Day11_A_MonoLake']
#GroundAltitude=1080; CVS=['Day1_B_LakePowell', 'Day1_C_GoingToCamarillo', 'Day11_B_TransitOverLand', 'Day11_C_GoingToLakePowell', 'Day11_D_LakePowellNight']
##############################################################################
CVSAnalyzeVector=[CVSfilenamebatch_D8_SJR]
#CVSAnalyzeVector=CVS
FL1a=True
FL1b=False
FL2a=False

for  CVSfilenamebatch in CVSAnalyzeVector:
  
    if FL1a==True:
        L1a = P_L1a(CVSfilenamebatch, TotalSecondsToAnalyzeVector, AngularAverageDegrees, CalibrationFilesNames, ChannelSetToAnalyzeVector, sixtyHertzFilter,FlagsL1a)
        L1a.run()
    if FL1b==True:
        L1b = P_L1b(CVSfilenamebatch, InitialTime, FinalTime, El, ChannelVectorToAnalyse, GroundAltitude, FlagsL1b)
        L1b.run()
    if FL2a==True:
        L2a = P_L2a(CVSfilenamebatch, PD, CLS, WS, CreateKMLData, MAP_LatLon, MAP_UTM, AntennaTemperatureSavingVector, RetrievalMatlabFunction)
        L2a.run()