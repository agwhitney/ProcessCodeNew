import os
import sys
import pylab as pl
configfile='./Core/PL1b.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from PL1b import P_L1b

CreateKMLData=True
mapping=True 
FlagsL1b={"CreateKMLData":CreateKMLData, "mapping":mapping}
##############################################################################
##############################################################################
#######################
InitialTime=0
FinalTime=299
El=45
GroundAltitude=0 # Sea Level
ChannelVectorToAnalyse=['18_GHz','34_GHz','24_GHz'] #,'118p0_25_GHz','34_GHz','24_GHz','90_GHz','130_GHz','168_GHz','118p0_5_GHz','118p1_GHz','118p2_GHz','118p3_GHz','118p4_GHz','118p5_GHz', '183m1_GHz', '183m2_GHz','183m3_GHz', '183m4_GHz','183m5_GHz', '183m6_GHz','183m7_GHz', '183m8_GHz']#,'118p5_GHz'] #,'18_GHz_QH', '118p5_GHz']		
#######################
##############################################################################
##############################################################################
#GroundAltitude=1113 # Lake Powell
#GroundAltitude=1946 # Mono Lake
#GroundAltitude=1850 # Lake Tahoe
CVSfilenamebatch_D7_01_10_SJR='SingleFile_2014_11_06__16_09_42__1of10_WCFC_Day3_SanJoaquinRiver'
CVSfilenamebatch_D7_02_10_SJR='SingleFile_2014_11_06__16_14_52__2of10_WCFC_Day3_SanJoaquinRiver'
#CVSfilenamebatch_D7_03_14_LT='SingleFileTest_2014_11_12__12_33_50__3of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_04_14_LT='SingleFileTest_2014_11_12__12_38_50__4of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_10_14_LT='SingleFileTest_2014_11_12__13_08_56__10of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_06_14_LT='SingleFileTest_2014_11_12__12_48_53__6of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_07_14_LT='SingleFileTest_2014_11_12__12_53_53__7of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_01_14_LT='SingleFileTest_2014_11_12__12_23_41__1of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
##############################################################################
CVSAnalyzeVector=[CVSfilenamebatch_D7_01_10_SJR]


for  CVSfilenamebatch in CVSAnalyzeVector:
	L1b = P_L1b(CVSfilenamebatch, InitialTime, FinalTime, El, ChannelVectorToAnalyse, GroundAltitude, FlagsL1b)
	L1b.run()