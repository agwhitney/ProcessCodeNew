import os
import sys
import pylab as pl
configfile='./Core/PL2a.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from PL2a import P_L2a
###########################################################################
## L2a Parameters
#RetrievalMatlabFunction='HAMMR_retrieval_alg_XBmodified_V002'
RetrievalMatlabFunction='HAMMR_retrieval_alg_XBmodified_V003'
CreateKMLData=True
MAP_LatLon=True 
MAP_UTM=False
## Save Antenna temperature Optioons
### MW, MMW, SND
AntennaTemperatureSavingVector={"MW":True, "MMW": True, "SND":True}


CVSfilenamebatch_Day9='Day9_CamarilloMarineLayer'
#CVSAnalyzeVector=[CVSfilenamebatch_Day9]

#CVSfilenamebatch_D7_01_10_SJR='SingleFile_2014_11_06__16_09_42__1of10_WCFC_Day3_SanJoaquinRiver'
#CVSfilenamebatch_D7_02_10_SJR='SingleFile_2014_11_06__16_14_52__2of10_WCFC_Day3_SanJoaquinRiver'
#CVSfilenamebatch_D7_03_14_LT='SingleFileTest_2014_11_12__12_33_50__3of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_04_14_LT='SingleFileTest_2014_11_12__12_38_50__4of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_10_14_LT='SingleFileTest_2014_11_12__13_08_56__10of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_06_14_LT='SingleFileTest_2014_11_12__12_48_53__6of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_07_14_LT='SingleFileTest_2014_11_12__12_53_53__7of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_01_14_LT='SingleFileTest_2014_11_12__12_23_41__1of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
##############################################################################
CVSfilenamebatch_D3_11_15_gtS='SingleFile_2014_11_06__15_44_23__11of15_WCFC_Day3_going_to_Stockton'; GroundAltitude=0
CVSAnalyzeVector=[CVSfilenamebatch_D3_11_15_gtS]


PD=[5.5, 13 ] 
CLS=[0.4,1.2]
WS=[0, 50]

WS=[0, 50]

for  CVSfilenamebatch in CVSAnalyzeVector:

	L2a = P_L2a(CVSfilenamebatch, PD, CLS, WS, CreateKMLData, MAP_LatLon, MAP_UTM, AntennaTemperatureSavingVector, RetrievalMatlabFunction)
	L2a.run()