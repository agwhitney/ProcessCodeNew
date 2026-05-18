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
import numpy as np
#configfile='..\..\GeneralPaths.py'
configfile='../GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import L1a_DATA_PROCESSED_PATH, CALVERSION
from KMLfileAux import fileKML
from L1bFileAux import CreateGeoReferencedAntennaTempeartureFile
from GeoMappingAux import datamapping
from GeoReferencingAux import dataproject
from OpenCVSBatchFile import OpenCVSBatchFile



class P_L1b():
    
    def __init__(self, CVSfilenamebatch, InitialTime, FinalTime, El, ChannelVector, GroundAltitude, FlagsL1b):


	  	self.InitialTime=InitialTime
	  	self.FinalTime=FinalTime
	  	self.El=El 
	  	self.GroundAltitude=GroundAltitude
	  	self.mapping=FlagsL1b['mapping']
	  	self.CreateKMLData=FlagsL1b['CreateKMLData'] 
		self.RadiometricDataSet={'18_GHz_QV':'MW','24_GHz_QV':'MW','34_GHz_QV':'MW','18_GHz_QH':'MW','24_GHz_QH':'MW','34_GHz_QH':'MW','90_GHz':'MMW','130_GHz':'MMW', '168_GHz':'MMW', '118p0_GHz':'SND','118p0_25_GHz':'SND','118p0_5_GHz':'SND','118p1_GHz':'SND', '118p2_GHz':'SND', '118p3_GHz':'SND','118p4_GHz':'SND', '118p5_GHz':'SND', '183m1_GHz':'SND','183m2_GHz':'SND','183m3_GHz':'SND','183m4_GHz':'SND','183m5_GHz':'SND','183m6_GHz':'SND','183m7_GHz':'SND','183m8_GHz':'SND'}		
		self.ChannelVector=ChannelVector

        ##############################################################################
        ##############################################################################
		self.CVSBatchFiles=OpenCVSBatchFile(CVSfilenamebatch)
		self.pathfordata=self.CVSBatchFiles.pathfordata
		return

    def run(self):

		matplotlib.rc('xtick', labelsize=11)    # xlabel tics size
		matplotlib.rc('ytick', labelsize=11)    # ylabel tics size
		font = {'family':'serif','size': 12}    # general font type and sizeSingleFile_2014_11_10__15_36_32__3of36_WCFC_Day5_SeatleAreaAndBack
		matplotlib.rc('font', **font)
       
		for CalIndex in range(0,len(self.CVSBatchFiles.filenamerootVector)-1):

			filenameroot=self.CVSBatchFiles.filenamerootVector[CalIndex]
			#print filenameroot
			############################################################################
			filenameroot23='HAMMR_L1b_v00' + str(CALVERSION) + '_'+filenameroot[:-3] 
			GeoANTFile=CreateGeoReferencedAntennaTempeartureFile(filenameroot23)  
			filenameroot='HAMMR_L1a_v00' + str(CALVERSION)+ '_'+filenameroot[:-3] 
		

			############################################################################
			pathfordata=os.path.join(L1a_DATA_PROCESSED_PATH,filenameroot)
			if not os.path.exists(pathfordata): 
				os.makedirs(pathfordata)
				print '-->',pathfordata, 'has been created'
			############################################################################

			for Channel in self.ChannelVector:

				matplotlib.pyplot.close("all")
				RadDataSet=self.RadiometricDataSet[Channel]
				DataProjection=dataproject(filenameroot, Channel, pathfordata, RadDataSet, self.GroundAltitude)
				print "\n\n\n #####################################################################"
				print "- Projecting Antenna Temperature for " + Channel + ' | '+filenameroot
				print "This may take a while."
				start_time = time.time()
				DataProjection.ProjectAntennaTemperature(InitialTime=self.InitialTime, FinalTime=self.FinalTime, SceneMaxAngle=self.El, Verbose=False, PrintWholeEllipse=False)
				
				# fignum=220
				# fig0=pl.figure(fignum)
				# ax = fig0.add_subplot(111)    
				# pl.plot( np.array(DataProjection.GroundAz)*180/np.pi, '.', label='Azimuth')
				# pl.plot(np.array(DataProjection.GroundEl)*180/np.pi, '.', label='Elevation')    	
	   			    
				# pl.ylabel('Ground Angle')  
				# pl.xlabel('Steps') 			
				# title='Ground AnglesVs Motor Position '
				# plt.title(title)
				# pl.grid()		
				# pl.legend(loc = 'best',shadow = True)
				# fig0.suptitle(filenameroot, fontsize=5)				    
				# figfilename =os.path.join(DataProjection.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
				# fig0.savefig(figfilename)     
				##############################################
				elapsed_time = time.time() - start_time
				print "---> Projection done in ", elapsed_time, 'seconds'
				print "- Creating maps for " + Channel + ' | '+filenameroot

		

				elapsed_time2 = time.time() - start_time
				if self.mapping==True:
					
					Mapping=datamapping(Channel, filenameroot, pathfordata)
					if Channel=='18_GHz_QH':
					    #DataProjection.plotAuxData(filenameroot)				
					    ECenterLonVector2=np.array(DataProjection.ECenterLonVector).reshape((len(DataProjection.ECenterLonVector),1))
					    ECenterLatVector2=np.array(DataProjection.ECenterLatVector).reshape((len(DataProjection.ECenterLatVector),1))	    	
					    latlonSpacing=0.02
					    llcrnrlon=np.min(ECenterLonVector2)-latlonSpacing
					    llcrnrlat=np.min(ECenterLatVector2)-latlonSpacing
					    urcrnrlon=np.max(ECenterLonVector2)+latlonSpacing
					    urcrnrlat=np.max(ECenterLatVector2)+latlonSpacing
					
					Mapping.SetCoordinates(urcrnrlat, llcrnrlat, urcrnrlon, llcrnrlon, 20, 20, 0.0002, 0.0002)	    
					print '---> llc: (', llcrnrlon,'|', llcrnrlat, ') ---- urc: (', urcrnrlon,'|', urcrnrlat, ')'
					start_time = time.time()
					print "----> mapping in UTM ...."

					MAP_AT_UTM= Mapping.MapAssigment(DataProjection.ECenter_EastingVector, DataProjection.ECenter_NorthingVector, Mapping.SpatialResolutionX, Mapping.SpatialResolutionY, Mapping.Xm, Mapping.Ym, DataProjection.AntennaTemperatureVector)
					#MAP_AT_LatLon= DataProjection.Mapping(DataProjection.ECenterLonVector, DataProjection.ECenterLatVector, DataProjection.SpatialResolutionlon, DataProjection.SpatialResolutionlat, DataProjection.LatM, DataProjection.LonM, DataProjection.AntennaTemperatureVector)
					# MAP_Gel_UTM= Mapping.MapAssigment(DataProjection.ECenter_EastingVector, DataProjection.ECenter_NorthingVector, Mapping.SpatialResolutionX, Mapping.SpatialResolutionY, Mapping.Xm, Mapping.Ym, np.array(DataProjection.GroundEl)*180/np.pi)
					# MAP_Gaz_UTM= Mapping.MapAssigment(DataProjection.ECenter_EastingVector, DataProjection.ECenter_NorthingVector, Mapping.SpatialResolutionX, Mapping.SpatialResolutionY, Mapping.Xm, Mapping.Ym, np.array(DataProjection.GroundAz)*180/np.pi)

					elapsed_time2 = time.time() - start_time	    
					print "----> end mapping. Total mapping time: ", elapsed_time2, 'seconds'
					############################################################################
					############################################################################
					print "- Creating images for " + Channel + ' | '+filenameroot
					start_time = time.time()

					masked_array=np.ma.masked_where(MAP_AT_UTM<1, MAP_AT_UTM)
					if RadDataSet=='MW':
						maskindex=np.logical_or((MAP_AT_UTM<=0),(MAP_AT_UTM>265))
						masked_array=np.ma.masked_where(maskindex, MAP_AT_UTM)
						masked_array_MW=masked_array
						#print np.mean(np.mean(masked_array)), np.max(masked_array), np.min(masked_array)
						z_minSat=np.mean(np.mean(masked_array))-15 #125
						z_maxSat=np.mean(np.mean(masked_array))+10 #150
						#DataProjection.Channel=Channel[:-2]+'First Stokes'
						#Mapping.Channel=Channel[:-2]+'First Stokes'
						DataProjection.Channel=Channel
						Mapping.Channel=Channel    							    	
					elif RadDataSet=='MMW':
						maskindex=np.logical_or((MAP_AT_UTM<=0),(MAP_AT_UTM>265))
						masked_array=np.ma.masked_where(maskindex, MAP_AT_UTM)
						masked_array_MMW=masked_array
						z_minSat=np.mean(np.mean(masked_array))-10 #205
						z_maxSat=np.mean(np.mean(masked_array))+10   #235 	
					elif RadDataSet=='SND':
						maskindex=np.logical_or((MAP_AT_UTM<=0),(MAP_AT_UTM>300))
						masked_array=np.ma.masked_where(maskindex, MAP_AT_UTM)
						masked_array_SND=masked_array
						z_minSat=np.mean(np.mean(masked_array))-10
						z_maxSat=np.mean(np.mean(masked_array))+10  

					z_min=120
					z_max=310
					###########################################################################
					#DisplayFileName=True
					#fignum=100000
					#Mapping.createUTMImage(fignum,Mapping.Xm,Mapping.Ym, MAP_AT_UTM, z_min, z_max, DisplayFileName=DisplayFileName)
					
					## Uncomment for creating images!!!!
					#fignum=100001
					#pl.close('all')
					#Mapping.createUTMImage(fignum,Mapping.Xm,Mapping.Ym, MAP_AT_UTM, z_minSat, z_maxSat)
					
					#fignum=100002
					#Mapping.createUTMImage(fignum,Mapping.Xm,Mapping.Ym, MAP_Gel_UTM, np.min(np.array(DataProjection.GroundEl)*180/np.pi), np.max(np.array(DataProjection.GroundEl)*180/np.pi), DisplayFileName=DisplayFileName, title='Ground Elevation for ', Legend='Degree')
					#fignum=100003
					#Mapping.createUTMImage(fignum,Mapping.Xm,Mapping.Ym, MAP_Gaz_UTM, np.min(np.array(DataProjection.GroundAz)*180/np.pi), np.max(np.array(DataProjection.GroundAz)*180/np.pi), DisplayFileName=DisplayFileName, title='Ground Azimuth for ', Legend='Degree')

					self.CreateKMLData=False
					if self.CreateKMLData== True:
						## Has the overlay image to be in lat-lon format ???
						print "----> Generating KML data"
						#print "----> mapping in Lat/Lon...."
						print "Checking vector lengths: ", len(DataProjection.ECenterLonVector), len( DataProjection.AntennaTemperatureVectorLatLon)
						MAP_AT_LatLon=Mapping.MapAssigment(DataProjection.ECenterLonVector, DataProjection.ECenterLatVector, Mapping.SpatialResolutionlon, Mapping.SpatialResolutionlat, Mapping.LonM, Mapping.LatM, DataProjection.AntennaTemperatureVectorLatLon)
						#print "----> mapping trajectory in Lat/Lon...."
						#MAP_AT_LatLon=DataProjection.Mapping(DataProjection.TrajectoryLatVector, DataProjection.TrajectoryLonVector,DataProjection.SpatialResolutionlat, DataProjection.SpatialResolutionlon, DataProjection.LatM, DataProjection.LonM, DataProjection.AntennaTemperatureVectorLatLon)
						fignum=500002
						#Mapping.createKMLfile(fignum, Mapping.LonM, Mapping.LatM, MAP_AT_LatLon, z_min, z_max)
						Mapping.createKMLfile(fignum, Mapping.LonM, Mapping.LatM, MAP_AT_LatLon, z_minSat, z_maxSat)
						############################################################################ 
				
				print "- TOTAL ELAPSED TIME: ", elapsed_time2+ elapsed_time , 'seconds'
				ZZ=np.zeros_like(DataProjection.AntennaTemperatureVector)
				 ## If the file does not have navigation data, then insert it.
				if GeoANTFile.TrajDataTable==False: 
					GeoANTFile.InsertAircraftTrajectory(DataProjection.Latitude, DataProjection.Longitude, DataProjection.GPSTime, DataProjection.Altitude)
				GeoANTFile.InsertTable(RadDataSet, Channel, DataProjection.ECenterLatVector, DataProjection.ECenterLonVector, DataProjection.AntennaTemperatureVector, DataProjection.AltitudeVector , np.array(DataProjection.GroundEl)*180/np.pi, np.array(DataProjection.GroundAz)*180/np.pi, np.array(DataProjection.mayorsemiaxis), np.array(DataProjection.minorsemiaxis), np.array(DataProjection.footprintangle), DataProjection.TimeVector )


				elapsed_time3 = time.time() - start_time	    	    
				print "----> end Imaging. Total Imaging  time: ", elapsed_time3, 'seconds'
				print "-- TOTAL ELAPSED TIME: ", elapsed_time2+ elapsed_time+elapsed_time3 , 'seconds'


		GeoANTFile.fileclose()	


if __name__ == "__main__":


	CreateKMLData=True
	mapping=True 
	FlagsL1b={"CreateKMLData":CreateKMLData, "mapping":mapping}
	InitialTime=0
  	FinalTime=299
  	El=45

	CVSfilenamebatch_D7_01_10_SJR='SingleFile_2014_11_06__16_09_42__1of10_WCFC_Day3_SanJoaquinRiver'
	CVSfilenamebatch_D7_02_10_SJR='SingleFile_2014_11_06__16_14_52__2of10_WCFC_Day3_SanJoaquinRiver'
	CVSfilenamebatch_D7_03_14_LT='SingleFileTest_2014_11_12__12_33_50__3of14_WCFC_Day7_LakeTahoe'
	CVSfilenamebatch_D7_04_14_LT='SingleFileTest_2014_11_12__12_38_50__4of14_WCFC_Day7_LakeTahoe'
	CVSfilenamebatch_D7_10_14_LT='SingleFileTest_2014_11_12__13_08_56__10of14_WCFC_Day7_LakeTahoe'
	CVSfilenamebatch_D7_06_14_LT='SingleFileTest_2014_11_12__12_48_53__6of14_WCFC_Day7_LakeTahoe'
	CVSfilenamebatch_D7_07_14_LT='SingleFileTest_2014_11_12__12_53_53__7of14_WCFC_Day7_LakeTahoe'
	CVSfilenamebatch_D7_01_14_LT='SingleFileTest_2014_11_12__12_23_41__1of14_WCFC_Day7_LakeTahoe'
	ChannelVectorToAnalyse=['18_GHz'] #,'34_GHz','24_GHz'] #,'118p0_25_GHz','34_GHz','24_GHz','90_GHz','130_GHz','168_GHz','118p0_5_GHz','118p1_GHz','118p2_GHz','118p3_GHz','118p4_GHz','118p5_GHz', '183m1_GHz', '183m2_GHz','183m3_GHz', '183m4_GHz','183m5_GHz', '183m6_GHz','183m7_GHz', '183m8_GHz']#,'118p5_GHz'] #,'18_GHz_QH', '118p5_GHz']		
	CVSfilenamebatch=CVSfilenamebatch_D7_01_10_SJR
	GroundAltitude=0 # Sea Level
	#GroundAltitude=1113 # Lake Powell
	#GroundAltitude=1946 # Mono Lake
	#GroundAltitude=1850 # Lake Tahoe

	L1b = P_L1b(CVSfilenamebatch, InitialTime, FinalTime, El, ChannelVectorToAnalyse, GroundAltitude,FlagsL1b)
	L1b.run()