import numpy as np
import os
import sys
import pylab as pl
import matplotlib as mpl
from pylab import *
import tables as tb
import utm as utm
import time 
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
#import matplotlib.pyplot as plt
import numpy as np
#configfile='..\..\GeneralPaths.py'
configfile='../GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import L2a_DATA_PROCESSED_PATH, L2b_DATA_PROCESSED_PATH, CALVERSION
configfile='./Core/KMLfileAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from KMLfileAux import fileKML
configfile='./Core/GeoMappingAux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
configfile='./Core/ReadL2Aux.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from ReadL2Aux import readL2file
from GeoMappingAux import datamapping
from OpenCVSBatchFile import OpenCVSBatchFile
import scipy.io as sio

CreateKMLData=True
MAP_LatLon=True
MAP_UTM=False


#CVSfilenamebatch='Day3_C_SJR'
#CVSfilenamebatch='Day4_A_SJR'
#CVSfilenamebatch='Day6_C_SJR_at_Dusk'
#CVSfilenamebatch='Day8_B_SJR'
#CVSfilenamebatch='Day11_A_MonoLake'
#CVSfilenamebatch='Day7_D_MonoLake'
#CVSfilenamebatch='Day7_B_LakeTahoe'
#CVSfilenamebatch='Day7_D_MonoLake'
#CVSfilenamebatch='Day7_B_LakeTahoe'

#CVSfilenamebatch='Day5_A_GoingToCanadianBorder'
#CVSfilenamebatch='Day5_B_DescendingOverTheSea'
CVSfilenamebatch='Day5_C_SeatleAreaAndBack'
CVSfilenamebatch='Day8_C_GoingToSanLuisObispo'
CVSfilenamebatch='Day1_B_LakePowell'
CVSfilenamebatch='Day11_D_LakePowellNight'
CVSfilenamebatch='Day10_A_CamarilloCoast'

CVSfilenamebatch='Day6_B_GoingSouthToCarlsonCity'
CVSfilenamebatch='Day6_A_GoingSouthFromSalem'
CVSfilenamebatch='Day4_D_GoingToSalem'
CVSfilenamebatch='Day4_C_GoingToCrescentCityDescending'
CVSfilenamebatch='Day9_CamarilloMarineLayer'
#CVSfilenamebatch='Day2'
#CVSfilenamebatch='Day3_A_GoingToStockton'
#CVSfilenamebatch='Day4_B_GoingToCrescentCity'


#CVSfilenamebatch_D7_01_10_SJR='SingleFile_2014_11_06__16_09_42__1of10_WCFC_Day3_SanJoaquinRiver'
#CVSfilenamebatch_D7_02_10_SJR='SingleFile_2014_11_06__16_14_52__2of10_WCFC_Day3_SanJoaquinRiver'
#CVSfilenamebatch_D7_03_14_LT='SingleFileTest_2014_11_12__12_33_50__3of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_04_14_LT='SingleFileTest_2014_11_12__12_38_50__4of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_10_14_LT='SingleFileTest_2014_11_12__13_08_56__10of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
CVSfilenamebatch_D7_06_14_LT='SingleFileTest_2014_11_12__12_48_53__6of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_07_14_LT='SingleFileTest_2014_11_12__12_53_53__7of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
#CVSfilenamebatch_D7_01_14_LT='SingleFileTest_2014_11_12__12_23_41__1of14_WCFC_Day7_LakeTahoe'; GroundAltitude=1850 # Lake Tahoe
##############################################################################
#CVSfilenamebatch=CVSfilenamebatch_D7_06_14_LT
CVSfilenamebatch='Day9_CamarilloMarineLayer'

def main():



	matplotlib.rc('xtick', labelsize=11)    # xlabel tics size
	matplotlib.rc('ytick', labelsize=11)    # ylabel tics size
	font = {'family':'serif','size': 12}    # general font type and sizeSingleFile_2014_11_10__15_36_32__3of36_WCFC_Day5_SeatleAreaAndBack
	matplotlib.rc('font', **font)


	#CVSfilenamebatch='Day3_B_GoingToStockton'
	#CVSfilenamebatch='Day3_A_GoingToStockton'
	filenameroot='HAMMR_L2a_v00' + str(CALVERSION) + '_'+CVSfilenamebatch 
	############################################################################
	pathfordata=os.path.join(L2b_DATA_PROCESSED_PATH,filenameroot)
	if not os.path.exists(pathfordata): 
		os.makedirs(pathfordata)
		print '-->',pathfordata, 'has been created'

	Channel='MW'
	L2File=readL2file(filenameroot, Channel)

	#plt.figure()
	#plt.plot(L2File.Altitude)
	#plt.show()

	PDret=L2File.PD
	CLWg=L2File.CLW
	WSg=L2File.WS
	Latitude=L2File.Latitude
	Longitude=L2File.Longitude
	Altitude=L2File.Altitude
	Time=L2File.GPSTime


	latlonSpacing=0.02
	llcrnrlon=np.min(Longitude)-latlonSpacing
	llcrnrlat=np.min(Latitude)-latlonSpacing
	urcrnrlon=np.max(Longitude)+latlonSpacing
	urcrnrlat=np.max(Latitude)+latlonSpacing
	
	Mapping=datamapping(Channel, filenameroot, pathfordata)
	Mapping.SetCoordinates(urcrnrlat, llcrnrlat, urcrnrlon, llcrnrlon, 20, 20, 0.0002, 0.0002)	    
	print '---> llc: (', llcrnrlon,'|', llcrnrlat, ') ---- urc: (', urcrnrlon,'|', urcrnrlat, ')'
	start_time = time.time()
	Easting=[]
	Northing=[]
	for x in range(0, len(Latitude)):
		#print Latitude[x], Longitude[x]
		UTMconversion=utm.from_latlon(Latitude[x], Longitude[x])
		Easting.append(UTMconversion[0])
		Northing.append(UTMconversion[1]) 
		Mapping.UTMZoneNumber=UTMconversion[2] 
		Mapping.UTMZoneLetter=UTMconversion[3] 
	###################################################	
	DisplayFileName=True
	fignumPD=100000
	fignumCLW=200000
	fignumWS=300000
	z_min_PD=5.5
	z_max_PD=12.5		
	z_min_WS=0
	z_max_WS=50
	z_min_CLW=0.4
	z_max_CLW=1.2

	if MAP_UTM==True:
		print "----> mapping in UTM ...."
		MAP_PDret_UTM= Mapping.MapAssigment(Easting, Northing, Mapping.SpatialResolutionX, Mapping.SpatialResolutionY, Mapping.Xm, Mapping.Ym, PDret)
		MAP_CLWg_UTM= Mapping.MapAssigment(Easting, Northing, Mapping.SpatialResolutionX, Mapping.SpatialResolutionY, Mapping.Xm, Mapping.Ym, CLWg)
		MAP_WSg_UTM= Mapping.MapAssigment(Easting, Northing, Mapping.SpatialResolutionX, Mapping.SpatialResolutionY, Mapping.Xm, Mapping.Ym, WSg)
		###########################################################################
		Mapping.createUTMImage(fignumPD,Mapping.Xm,Mapping.Ym, MAP_PDret_UTM, z_min_PD, z_max_PD, DisplayFileName=DisplayFileName, title='Wet Path Delay ',  Legend='cm')
		Mapping.createUTMImage(fignumCLW,Mapping.Xm,Mapping.Ym, MAP_CLWg_UTM, z_min_CLW, z_max_CLW, DisplayFileName=DisplayFileName, title='Cloud Liquid Water ',  Legend='mm')
		Mapping.createUTMImage(fignumWS,Mapping.Xm,Mapping.Ym, MAP_WSg_UTM, z_min_WS, z_max_WS, DisplayFileName=DisplayFileName, title='Wind Speed ',  Legend='m/s')
	
	if MAP_LatLon==True:
	## Latitude-Longitude Mapp assigment
		print "----> mapping in Lat-Lon ...."
		pMAP_PDret_LatLon=Mapping.MapAssigment(Longitude, Latitude, Mapping.SpatialResolutionlon, Mapping.SpatialResolutionlat, Mapping.LonM, Mapping.LatM, PDret)
		print "------> PD done!"
		MAP_CLWg_LatLon= Mapping.MapAssigment(Longitude, Latitude, Mapping.SpatialResolutionlon, Mapping.SpatialResolutionlat, Mapping.LonM, Mapping.LatM, CLWg)
		print "------> CLW done!"
		MAP_WSg_LatLon= Mapping.MapAssigment(Longitude, Latitude, Mapping.SpatialResolutionlon, Mapping.SpatialResolutionlat, Mapping.LonM, Mapping.LatM, WSg)
		print "------> WS done!"
		###########################################################################
		print "----> Generating images in Lat-Lon ...."
		import scipy.signal as signal

		MAP_PDret_LatLon=pMAP_PDret_LatLon  #signal.wiener()
		Mapping.createLatLonImage(fignumPD+20, Mapping.LonM, Mapping.LatM, MAP_PDret_LatLon, z_min_PD, z_max_PD, DisplayFileName=DisplayFileName, title='Wet Path Delay ',  Legend='cm')
		Mapping.createLatLonImage(fignumCLW+20, Mapping.LonM, Mapping.LatM, MAP_CLWg_LatLon, z_min_CLW, z_max_CLW, DisplayFileName=DisplayFileName, title='Cloud Liquid Water ',  Legend='mm')
		Mapping.createLatLonImage(fignumWS+20, Mapping.LonM, Mapping.LatM, MAP_WSg_LatLon, z_min_WS, z_max_WS, DisplayFileName=DisplayFileName, title='Wind Speed ',  Legend='m/s')

		if CreateKMLData== True:
			## Has the overlay image to be in lat-lon format ???
			print "----> Generating KML files"
			fignum=500002
			Mapping.createKMLfile(fignum, Mapping.LonM, Mapping.LatM, MAP_PDret_LatLon, z_min_PD, z_max_PD)
			############################################################################ 

	L2File.fileclose()

		

if __name__ == "__main__":
    main()
