import numpy as np
import os
import sys
import pylab as pl
import matplotlib as mpl
from pylab import *
import tables as tb
import utm as utm
import time 
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
#import matplotlib.pyplot as plt
import numpy as np
#configfile='..\..\GeneralPaths.py'
configfile='../GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import L2a_DATA_PROCESSED_PATH, L1b_DATA_PROCESSED_PATH, CALVERSION
from KMLfileAux import fileKML
from GeoMappingAux import datamapping
from OpenCVSBatchFile import OpenCVSBatchFile
from RunMatlabAux import RunMatlabCode
from L2aFileAux import CreateL2File
import scipy.io as sio
class P_L2a():
    
	def __init__(self, CVSfilenamebatch, PD, CLW, WS, CreateKMLData,MAP_LatLon, MAP_UTM, AntennaTemperatureSavingVector, MatlabFunction):


		self.CreateKMLData=CreateKMLData #True
		self.MAP_LatLon=MAP_LatLon #True
		self.MAP_UTM=MAP_UTM #False
		self.AntennaTemperatureSavingVector=AntennaTemperatureSavingVector


		self.z_min_PD=PD[0]
		self.z_max_PD=PD[1]	
		self.z_min_WS=WS[0]
		self.z_max_WS=WS[1]
		self.z_min_CLW=CLW[0]
		self.z_max_CLW=CLW[1]

		self.MatlabFunction=MatlabFunction
		PID=os.getpid()
		self.MatFileName='Filename2process_'+ str(PID)

		self.CVSBatchFiles=OpenCVSBatchFile(CVSfilenamebatch)
		filenameroot23='HAMMR_L2a_v00' + str(CALVERSION) + '_'+CVSfilenamebatch 
		self.RetrievalFile=CreateL2File(filenameroot23) 		
		return



	#pathfordata=CVSBatchFiles.pathfordata
	def run(self):

		matplotlib.rc('xtick', labelsize=11)    # xlabel tics size
		matplotlib.rc('ytick', labelsize=11)    # ylabel tics size
		font = {'family':'serif','size': 12}    # general font type and sizeSingleFile_2014_11_10__15_36_32__3of36_WCFC_Day5_SeatleAreaAndBack
		matplotlib.rc('font', **font)
		
 
		for CalIndex in range(0,len(self.CVSBatchFiles.filenamerootVector)-1):
			matplotlib.pyplot.close("all")
			filenameroot=self.CVSBatchFiles.filenamerootVector[CalIndex]
			print filenameroot
			############################################################################
			DataToProcessFileName='HAMMR_L1b_v00' + str(CALVERSION) + '_'+filenameroot[:-3] 

			############################################################################
			pathfordata=os.path.join(L2a_DATA_PROCESSED_PATH,filenameroot[:-3] )
			if not os.path.exists(pathfordata): 
				os.makedirs(pathfordata)
				print '-->',pathfordata, 'has been created'
			############################################################################
			## Read hdf5 first and then save it
			## for all 3 channels... bla bla bal 
			
			RMC=RunMatlabCode(self.MatlabFunction, self.MatFileName, DataToProcessFileName)
			RMC.run()
			os.chdir(L1b_DATA_PROCESSED_PATH)
			DataFromMatlab=sio.loadmat(DataToProcessFileName+'.mat')
			#print 
			PDret=DataFromMatlab['PDret'][0]
			CLWg=DataFromMatlab['CLWg']
			WSg=DataFromMatlab['WSg']

			Latitude=DataFromMatlab['mwLat'][0]
			Longitude=DataFromMatlab['mwLon'][0]
			Altitude=DataFromMatlab['mwAltitude'][0]
			Time=DataFromMatlab['mwTime'][0]

			### Read it from the matlab output file and save it! 
			for RadiometricDataType in self.RetrievalFile.ChannelSetToAnalyzeVector:
				if self.AntennaTemperatureSavingVector[RadiometricDataType]==True:
					tablenum=0
					for channel in self.RetrievalFile.Ch[RadiometricDataType]:
						#print channel, RadiometricDataType, self.RetrievalFile.ChNames[RadiometricDataType][channel]  #, DataFromMatlab[self.RetrievalFile.ChNames[RadiometricDataType][channel]]
						self.RetrievalFile.InsertAntennaTemperatureTable(RadiometricDataType, self.RetrievalFile.ChNames[RadiometricDataType][channel], DataFromMatlab[self.RetrievalFile.ChNames[RadiometricDataType][channel]],tablenum)
						tablenum=tablenum+1

		
			### It needs to append data!!!!
			RadiometricDataType='MW'
			self.RetrievalFile.InsertRetrievalTable(RadiometricDataType,  PDret, CLWg, WSg, Latitude, Longitude, Altitude, Time)


	 		latlonSpacing=0.02
	 		llcrnrlon=np.min(Longitude)-latlonSpacing
			llcrnrlat=np.min(Latitude)-latlonSpacing
			urcrnrlon=np.max(Longitude)+latlonSpacing
			urcrnrlat=np.max(Latitude)+latlonSpacing
			Channel=' MW'
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

			DisplayFileName=True
			fignumPD=100000
			fignumCLW=200000
			fignumWS=300000


			if self.MAP_UTM==True:
				print "----> mapping in UTM ...."
				MAP_PDret_UTM= Mapping.MapAssigment(Easting, Northing, Mapping.SpatialResolutionX, Mapping.SpatialResolutionY, Mapping.Xm, Mapping.Ym, PDret)
				MAP_CLWg_UTM= Mapping.MapAssigment(Easting, Northing, Mapping.SpatialResolutionX, Mapping.SpatialResolutionY, Mapping.Xm, Mapping.Ym, CLWg)
				MAP_WSg_UTM= Mapping.MapAssigment(Easting, Northing, Mapping.SpatialResolutionX, Mapping.SpatialResolutionY, Mapping.Xm, Mapping.Ym, WSg)
				###########################################################################
				Mapping.createUTMImage(fignumPD,Mapping.Xm,Mapping.Ym, MAP_PDret_UTM, self.z_min_PD, self.z_max_PD, DisplayFileName=DisplayFileName, title='Wet Path Delay ',  Legend='cm')
				Mapping.createUTMImage(fignumCLW,Mapping.Xm,Mapping.Ym, MAP_CLWg_UTM, self.z_min_CLW, self.z_max_CLW, DisplayFileName=DisplayFileName, title='Cloud Liquid Water ',  Legend='mm')
				Mapping.createUTMImage(fignumWS,Mapping.Xm,Mapping.Ym, MAP_WSg_UTM, self.z_min_WS, self.z_max_WS, DisplayFileName=DisplayFileName, title='Wind Speed ',  Legend='m/s')
			
			if self.MAP_LatLon==True:
			## Latitude-Longitude Mapp assigment
				print "----> mapping in Lat-Lon ...."
				MAP_PDret_LatLon=Mapping.MapAssigment(Longitude, Latitude, Mapping.SpatialResolutionlon, Mapping.SpatialResolutionlat, Mapping.LonM, Mapping.LatM, PDret)
				MAP_CLWg_LatLon= Mapping.MapAssigment(Longitude, Latitude, Mapping.SpatialResolutionlon, Mapping.SpatialResolutionlat, Mapping.LonM, Mapping.LatM, CLWg)
				MAP_WSg_LatLon= Mapping.MapAssigment(Longitude, Latitude, Mapping.SpatialResolutionlon, Mapping.SpatialResolutionlat, Mapping.LonM, Mapping.LatM, WSg)
				###########################################################################
				Mapping.createLatLonImage(fignumPD+20, Mapping.LonM, Mapping.LatM, MAP_PDret_LatLon, self.z_min_PD, self.z_max_PD, DisplayFileName=DisplayFileName, title='Wet Path Delay ',  Legend='cm')
				Mapping.createLatLonImage(fignumCLW+20, Mapping.LonM, Mapping.LatM, MAP_CLWg_LatLon, self.z_min_CLW, self.z_max_CLW, DisplayFileName=DisplayFileName, title='Cloud Liquid Water ',  Legend='mm')
				Mapping.createLatLonImage(fignumWS+20, Mapping.LonM, Mapping.LatM, MAP_WSg_LatLon, self.z_min_WS, self.z_max_WS, DisplayFileName=DisplayFileName, title='Wind Speed ',  Legend='m/s')

				if self.CreateKMLData== True:
					## Has the overlay image to be in lat-lon format ???
					print "----> Generating KML data"
					fignum=500002
					Mapping.createKMLfile(fignum, Mapping.LonM, Mapping.LatM, MAP_PDret_LatLon, self.z_min_PD, self.z_max_PD)
					############################################################################ 


		self.RetrievalFile.fileclose()

		

if __name__ == "__main__":

	CreateKMLData=True
	MAP_LatLon=True #True #True
	MAP_UTM=False
	RetrievalMatlabFunction='HAMMR_retrieval_alg_XBmodified_V003'

	CVSfilenamebatch='Day9_CamarilloMarineLAyer'

	z_min_PD=5.5
	z_max_PD=13	
	z_min_WS=0
	z_max_WS=50
	z_min_CLW=0.4
	z_max_CLW=1.2
	### MW, MMW, SND
	SaveVector=[True, True, True]
	
	PD=[z_min_PD,z_max_PD ]	
	CLS=[z_min_CLW,z_max_CLW ]
	WS=[z_min_WS, z_max_WS]

	L2a = P_L2a(CVSfilenamebatch, PD, CLS, WS, CreateKMLData, MAP_LatLon, MAP_UTM, SaveVector, RetrievalMatlabFunction )
	L2a.run()




