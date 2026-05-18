import numpy as np
import os
import sys
import pylab as pl
import matplotlib as mpl
import geomag
from pylab import *
import tables as tb
import utm as utm
from scipy import linalg
#from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid, cm
configfile='..\..\GeneralPaths.py'
#configfile='..\GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import L1a_DATA_PROCESSED_PATH
from KMLfileAux import fileKML
from L1bFileAux import CreateGeoReferencedAntennaTempeartureFile

class dataproject:

    def __init__(self, filenameroot, Channel, pathfordata, RadDataSet, verbose=False):
       # try:        
        filename=filenameroot+'.h5'
        if not os.path.isabs(filename):
            filenameh5 = os.path.join(L1a_DATA_PROCESSED_PATH, filename)
        h5file=tb.openFile(filenameh5, mode = "r")
        if verbose==True:
            print "-----------------------------------------"
            for group in h5file.walkGroups('/'):
                print "--", group
            print "-----------------------------------------"        
        #except:
        #   print "File not found:", filename
    	##########################################################################
    	###########################################################################        
    	#try:
        self.RadiometricSubset=RadDataSet
        Channel_Tant='Ch_'+Channel+'_AntTemp'
        datasource='h5file.root.RadiometricData.%s.%s'%(self.RadiometricSubset,Channel_Tant)
        print datasource
        data =eval(datasource)
        print data
        #print "INFO: new instance of dataprocessor for ", data   
        self.AntennaTemperature=  np.array([x['AntTempAngular'] for x in data.iterrows()], np.uint16)/10.
        self.CalCoef= np.array([x['CalCoef'] for x in data.iterrows()],np.uint16)/10.
        self.NDDR1= np.array([x['NDDR1'] for x in data.iterrows()], np.uint16)
        self.NDDR2= np.array([x['NDDR2'] for x in data.iterrows()], np.uint16)
        self.Trec= np.array([x['Trec'] for x in data.iterrows()], np.uint16)/10.
        self.Tref= np.array([x['Tref'] for x in data.iterrows()], np.uint16)/10.               
        #except:
        #    print "No ", Channel, " Channel data found!"	        
        #try:
        datasource='h5file.root.NavigationData'
        data =eval(datasource)
        #print "INFO: new instance of dataprocessor for ", data  
        self.Altitude= np.array( [x['Altitude'] for x in data.Navigation.iterrows()],'double')
        self.CPUTime= np.array( [x['CPUTime'] for x in data.Navigation.iterrows()],'double')
        self.GPSTime= np.array( [x['GPSTime'] for x in data.Navigation.iterrows()],'double')
        self.Latitude= np.array( [x['Latitude'] for x in data.Navigation.iterrows()],'double')
        self.Longitude= np.array( [x['Longitude'] for x in data.Navigation.iterrows()],'double')
        self.Pitch= np.array( [x['Pitch'] for x in data.Navigation.iterrows()],'double')
        self.Roll= np.array( [x['Roll'] for x in data.Navigation.iterrows()],'double')
        self.Yaw= np.array( [x['Yaw'] for x in data.Navigation.iterrows()],'double')             

        #except:
        #    print "No Navigation Data found!"
        datasource='h5file.root.RadiometricData.%s.TrueCourse'%(self.RadiometricSubset)
        print datasource
        data =eval(datasource)
        print data
        #print "INFO: new instance of dataprocessor for ", data   
       
        self.truecourse_x= np.array([x['x'] for x in data.iterrows()],'double')
        self.truecourse_y= np.array([x['y'] for x in data.iterrows()],'double')
        self.truecourse_z= np.array([x['z'] for x in data.iterrows()],'double')

        datasource='h5file.root.RadiometricData.%s'%(self.RadiometricSubset)
        print datasource
        data =eval(datasource)
        print data
        #print "INFO: new instance of dataprocessor for ", data   
        #self.MotorPosition=  np.array([x['0'] for x in data.iterrows()],'double')
        self.MotorPosition= np.array( [x for x in data.MotorPosition.iterrows()],'double')
        ####################################################################
        self.Nscans=len(self.Yaw)
        ##################
        self.filenameroot=filenameroot    
        self.pathfordata=pathfordata
        self.Channel=Channel
        self.masked_array=[]
		####################################################################
        Beam_width={'18_GHz_QH':3.46,'24_GHz_QH':3.06,'34_GHz_QH':2.14,'18_GHz_QV':3.46,'24_GHz_QV':3.06,'34_GHz_QV':2.14,'90_GHz':1.36,'130_GHz':0.44, '168_GHz':0.34, '118p0_GHz':0.95,'118p0_25_GHz':0.95,'118p0_5_GHz':0.95,'118p1_GHz':0.95, '118p2_GHz':0.95,'118p3_GHz':0.95,'118p4_GHz':0.95, '118p5_GHz':0.95, '183m1_GHz':0.67,'183m2_GHz':0.67,'183m3_GHz':0.67,'183m4_GHz':0.67,'183m5_GHz':0.67,'183m6_GHz':0.67,'183m7_GHz':0.67,'183m8_GHz':0.67}
        #Beam_offset={'MW':15.65, 'MMW':0, 'SND':-3.4}
        Beam_offset={'MW':-15.65, 'MMW':0, 'SND':3.4}
        self.AntennaAngularOffset=Beam_offset[self.RadiometricSubset]*np.pi/180
        self.Antenna_BeamWidth3dB=Beam_width[self.Channel]
    	####################################################################
        self.SpatialResolutionX=40
        self.SpatialResolutionY=40
        self.SpatialResolutionlon=0.0004
        self.SpatialResolutionlat=0.0004    
	    ##############################################
        self.zb2vector=[]	
        self.GroundAz=[]
        self.GroundEl=[]
        self.ECenterLatVector=[]
        self.ECenterLonVector=[]
        self.ECenter_EastingVector=[]
        self.ECenter_NorthingVector=[]
        self.TrajectoryLatVector=[]
        self.TrajectoryLonVector=[]	    
        self.AntennaTemperatureVector=[]
        self.AntennaTemperatureVectorLatLon=[]
        self.AltitudeVector=[]
        self.TimeVector=[]
        self.AzimuthAngleVector=[]
        self.NadirAngleVector=[]
        self.NadirPointingGroundElevationAngle=[]
        self.mayorsemiaxis=[]
        self.minorsemiaxis=[]
        self.footprintangle=[]      


        #Normalizedmotorposition=np.copy(self.MotorPosition)
        Normalizedmotorposition=self.MotorPosition #-np.pi #-(18)*np.pi/180
        #self.MotorPosition=self.MotorPosition+np.pi-(18*1)*np.pi/180  #[::-1] -(18*2)*np.pi/180        
       

        #self.truecourse_z=(-np.cos(Normalizedmotorposition)*np.sin(Normalizedmotorposition)*np.sin(self.AntennaAngularOffset)-np.sin(Normalizedmotorposition)*np.cos(self.AntennaAngularOffset))
        #self.truecourse_x= np.cos(Normalizedmotorposition)*np.sin(self.AntennaAngularOffset)
        #self.truecourse_y= np.cos(self.AntennaAngularOffset)*np.cos(Normalizedmotorposition)-np.sin(self.AntennaAngularOffset)*np.sin(Normalizedmotorposition)**2             

        self.zmotor=-np.sin(Normalizedmotorposition)
        self.ymotor=np.cos(Normalizedmotorposition)
        self.xmotor=0
        

	    ##############################################   
        self.BeamNadirAngle=np.arctan2(self.truecourse_z, self.truecourse_y)*180/np.pi
        self.BeamNadirAngle=np.mod(self.BeamNadirAngle, 360)
        self.ElevationAngle=self.BeamNadirAngle

        return


    def calculateEllipse(self, x, y, a, b, angle, angular_resolution):
	   # calculating the ellipse's contour 

		beta = angle*np.pi/180;
		alpha_vector= np.linspace(0.0, 360.0-angular_resolution, num=np.round(360/angular_resolution))*np.pi/180
		i=0
		#print angular_resolution, len(alpha_vector)
		SpatialResolutionX=100
		SpatialResolutionY=100
		l1=np.floor(a/SpatialResolutionX)
		l2=np.floor(b/SpatialResolutionY)
		FillingSteps=np.max([l1,l2])
		#print FillingSteps
		if FillingSteps>0:
			a_vector=linspace(SpatialResolutionX,a,FillingSteps)
			b_vector=linspace(SpatialResolutionY,b,FillingSteps)
		else:
			a_vector=[a]
			b_vector=[b]
		#print a_vector, b_vector
		X = np.zeros((np.round(360/angular_resolution))*len(a_vector));
		Y = np.zeros((np.round(360/angular_resolution))*len(a_vector));

		for alpha in alpha_vector:
			for  j in range(len(a_vector)):
				X[i]=x+(a_vector[j] * np.cos(alpha) * np.cos(beta) - b_vector[j] * np.sin(alpha) * np.sin(beta));
				Y[i]=y+(a_vector[j] * np.cos(alpha) * np.sin(beta) + b_vector[j] * np.sin(alpha) * np.cos(beta));
				i=i+1
	
		return X,Y 
   

    def calculateEllipseCenterandAxis(self, Latitude, Longitude, altitude, Zb, Antenna_BeamWidth3dB, verbose=False):
		UTMconversion=utm.from_latlon(Latitude, Longitude)
		# X, Y are the nadir position in UTM
		# X_, Y_ are the projected center of the ellipse in UTM	
		Phi=np.arccos(-Zb[2])
		Theta=np.arctan2(Zb[1], Zb[0])
		radius=altitude*np.tan(Phi)
		Y__=radius*np.cos(Theta)
		X__=radius*np.sin(Theta)
		#verbose=True
		if verbose==True:
			print "********************"
			print "Antenna direction angles:", np.arctan2(Zb[1], Zb[0])*180/np.pi, np.arccos(Zb[2])*180/np.pi 
			print "radius, Y and X:", radius, Y__, X__
			print "Current Y and X:", altitude/Zb[2]*Zb[1], altitude/Zb[2]*Zb[0]

		X=UTMconversion[0] 
		X_= X - X__  ##altitude/Zb[2]*Zb[0] 
		Y=UTMconversion[1] 
		Y_= Y - Y__ ## altitude/Zb[2]*Zb[1]
		r=np.sqrt(np.square(X_-X)+np.square(Y_-Y)+np.square(altitude))
		#send back the angle between the footprint semi mayor axis respect to the axis y of the Earth system
		EllipseDirection=np.array([X_-X,Y_-Y, 0])
		ang=self.ang_footprint(EllipseDirection)
		Antenna_BeamWidth3dBrad=Antenna_BeamWidth3dB*np.pi/180. # in degrees
		a=0.5*r*r*Antenna_BeamWidth3dBrad/altitude  #Computing the major semi-axis 
		b=0.5*r*Antenna_BeamWidth3dBrad             #Computing the minor semi-axis 

		self.mayorsemiaxis.append(a)
		self.minorsemiaxis.append(b)
		self.footprintangle.append(ang)
		#print "Ellipse angle:", ang
		#print "a,b:", a, b

		#print "r, Antenna_BeamWidth3dB, altitude:", r, Antenna_BeamWidth3dB, altitude
		#print "center:", altitude/(Zb[2]*Zb[0]), altitude/(Zb[2]*Zb[1])
		Xe,Ye=self.calculateEllipse(X_, Y_,a,b, ang, 5)
		return Xe, Ye, UTMconversion[2], UTMconversion[3], X_, Y_

    def ang_footprint(self, EllipseDirection):
		#Calculating the orientation of the footprint respect to the local Earth coordinates.
		u=EllipseDirection
		ux=np.array([1,0,0])

		module_u=np.sqrt(np.square(u[0])+np.square(u[1])+np.square(u[2]))
		module_ux=np.sqrt(np.square(ux[0])+np.square(ux[1])+np.square(ux[2]))
		mult=module_u*module_ux
		if mult!=0: 
			angle=np.arccos(np.dot(u,ux)/mult)*180./np.pi;
			if u[1]>=0:
				angle=angle
			else:
				angle=(np.pi-angle)
		else:
			angle=0
		return angle 
	
  #   def SetCoordinates(self, urcrnrlat, llcrnrlat, urcrnrlon, llcrnrlon, SpatialResolutionX=10, SpatialResolutionY=10, SpatialResolutionlon=0.0001,  SpatialResolutionlat= 0.0001):
		# ####################################################################
		# self.urcrnrlat=urcrnrlat
		# self.llcrnrlat=llcrnrlat
		# self.urcrnrlon=urcrnrlon
		# self.llcrnrlon=llcrnrlon
		# ####################################################################
		# self.SpatialResolutionX=SpatialResolutionX
		# self.SpatialResolutionY=SpatialResolutionY
		# self.SpatialResolutionlon=SpatialResolutionlon
		# self.SpatialResolutionlat=SpatialResolutionlat
		# ####################################################################		
		# llcUTMconversion=utm.from_latlon(llcrnrlat, llcrnrlon)
		# urcUTMconversion=utm.from_latlon(urcrnrlat, urcrnrlon)
		# # X, Y are the nadir position in UTM
		# # X_, Y_ are the projected center of the ellipse in UTM
		# Xllc=llcUTMconversion[0] 
		# Yllc=llcUTMconversion[1]
		# Xurc=urcUTMconversion[0] 
		# Yurc=urcUTMconversion[1] 
		# #print Xurc, Xllc, Xurc-Xllc, type(Xurc)
		# #print Yurc, Yllc, Yurc-Yllc    
		# ImagesizeXinMeters=np.abs(Xurc-Xllc)
		# ImagesizeYinMeters=np.abs(Yurc-Yllc)    
		# DeltaXMeters=np.round(ImagesizeXinMeters/SpatialResolutionX)
		# DeltaYMeters=np.round(ImagesizeYinMeters/SpatialResolutionY)
		# print "---> Map dimensions in meters X:", ImagesizeXinMeters, '  Y:', ImagesizeYinMeters
		# self.Ym, self.Xm =np.meshgrid(np.linspace(np.min([Yllc, Yurc]),np.max([Yllc, Yurc]) ,DeltaYMeters),np.linspace(np.min([Xllc, Xurc]), np.max([Xllc, Xurc]),DeltaXMeters)) 

		# Imagesizelon=np.abs(llcrnrlon-urcrnrlon)
		# Imagesizelat=np.abs(llcrnrlat-urcrnrlat)    
		# DeltaLon=np.round(Imagesizelon/SpatialResolutionlon)
		# DeltaLat=np.round(Imagesizelat/SpatialResolutionlat)
		# print "---> Map dimensions in Lon:", Imagesizelon, 'Degrees. Lat:', Imagesizelat, 'Degrees'
		# self.LatM, self.LonM,=np.meshgrid(np.linspace(np.min([llcrnrlat, urcrnrlat]),np.max([llcrnrlat, urcrnrlat]) ,DeltaLat),np.linspace(np.min([llcrnrlon, urcrnrlon]),np.max([llcrnrlon, urcrnrlon]) ,DeltaLon)) 
		# return

  #  

	

    def BearingFromLatLon(self, lat1, lat2, lon1, lon2, Verbose=False):
		# Bearing, if it is from north (true or magnetic): Having two locations A and B, bearing of B to A is the angle measured clockwise from north to B having as angle vertex location A.
		# This method uses the "haversine" formula to calculate the great-circle distance between two points. That is, the shortest distance over the earth surface.
		R = 6371000
		lat1 = lat1 * np.pi / 180.
		lat2 = lat2 * np.pi / 180.
		dlat = (lat2-lat1)
		dlon = (lon2-lon1)* np.pi / 180.
		a=np.sin(dlat/2)**2+np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
		c=2*np.arcsin(np.sqrt(a))
		d= R*c
		Bearing =(np.arctan2(np.sin(dlon)*np.cos(lat2),np.cos(lat1)*np.sin(lat2)-np.sin(lat1)*np.cos(lat2)*np.cos(dlon)) *180./np.pi +360)%360
		#Verbose=True
		if Verbose:
				print "---> Angular distance:", c*180./np.pi, "Distance [m]:", d, "Bearing:", Bearing
		return Bearing


    def correctingMagneticDeclination(self, hdg, Lat, Lon, Verbose=False):
    	# Magnetic declination or variation is the angle on the horizontal plane between magnetic north (the direction the north end of a compass needle points, 
        # corresponding to the direction of the Earth's magnetic field lines) and true north (the direction along a meridian towards the geographic North Pole)
		# Using a prebuild package/function for calculating it for each Lat-Lon point. 
		dec=geomag.declination(Lat,Lon)
		#hdg=(hdg+360)%360
		#chdg=(hdg + dec + 360.0) % 360
		#if hdg<180:
		#	dec=-dec
		#chdg=(hdg + dec + 360.0) % 360
		## Going South
		#chdg=hdg - dec
		## Going North
		chdg=hdg + dec
		#print hdg
		Verbose=True
		if Verbose:
			print "---> Magnetic Declination:", dec
			print "---> Yaw:", hdg, " ---> Heading: ", chdg
		return chdg


    def CorrectFlatReflectorPointingVector(self, pitch, roll, hdg, FlatReflectorPointingVector):
		# Converting from degrees to radiants
		P=pitch * np.pi / 180.
		R=roll  * np.pi / 180.
		Y=hdg   * np.pi / 180.

		# Calculating the RxRyRz rotation matrixeser
		#R1=np.array([[1, 0, 0], [0, np.cos(P), -np.sin(P)], [0, np.sin(P), np.cos(P)]])
		#R2=np.array([[np.cos(R), 0, np.sin(R)],[0, 1, 0],  [-np.sin(R), 0, np.cos(R)]])
		#R3=np.array([[np.cos(Y),-np.sin(Y), 0], [np.sin(Y), np.cos(Y), 0], [0, 0, 1],])

		Rz=np.array([[np.cos(Y),-np.sin(Y), 0], [np.sin(Y), np.cos(Y), 0], [0, 0, 1],])
		Ry=np.array([[np.cos(P), 0, np.sin(P)],[0, 1, 0],  [-np.sin(P), 0, np.cos(P)]])
		Rx=np.array([[1, 0, 0], [0, np.cos(R), -np.sin(R)], [0, np.sin(R), np.cos(R)]])
		RzRyRx=np.dot(np.dot(Rz,Ry),Rx) 	##Same result as RzRyRx=np.dot(Rz,np.dot(Ry,Rx))
		## Note that As for any rotation matrix, the inverse rotation equals to the transposed matrix i.e.:M.T=M^-1
		iRzRyRx=linalg.inv(RzRyRx) #RzRyRx.T  
		AntennaPointingVector=np.dot(iRzRyRx,FlatReflectorPointingVector)
		##################################################################################
		## Due to numerical errors on the matrix inversion sometimes AntennaPointingVector is lower than -1, 
		## this is physically impossible, so we correct for it
		## May 12, 2015 - XB says it was an error in the code, now it is fix, it should not happen again. 
		if AntennaPointingVector[2]<-1.0:
			print "-----------------WARNING WARNING WARNING WARNING :"
			print " ERROR on the AntennaPointingVector, something is wrong, please check it!!!!"
			print " AntennaPointingVector:" , AntennaPointingVector , "pay atention to the Z coordinate (the third one)"
			AntennaPointingVector[2]=-1.0
		# Calculating Elevation and Azimuth angle from ground 
		Az=np.arctan2(AntennaPointingVector[1], AntennaPointingVector[0])
		El=np.arccos(AntennaPointingVector[2])
		self.GroundAz.append(Az)
		self.GroundEl.append(El)		

		return AntennaPointingVector


    def ProjectAntennaTemperature(self,InitialTime=0, FinalTime=298, SceneMaxAngle=45, Verbose=False, PrintWholeEllipse=False):
    	##############################################
    	# This function takes the angular swath defined by SceneMaxAngle, starting at InitialTime scan and ending at FinalTime Scan and 
    	# pairs the projected UMT X-Y position of each footprint, corrected for the aircraft plane attitude, with the antenna temperature 
    	# for each motor scan and for each rotation angle of the antenna (angular swath) 
    	# The ouptut is a vector with paired ground X-Y and Tant, but not an image. 
		##############################################

		Normalizedmotorposition=[]
		TAoffset=[]

		##############################################
		# Verifying that the file contains as many seconds as we would like to process. 
		print "----> The file contains ",self.Nscans, " seconds of data."
		print "----> Projecting ", FinalTime-InitialTime, " seconds of data. Starting at ", InitialTime
		if self.Nscans<=FinalTime:
			FinalTime=self.Nscans
			print "----> WARNING: Only",self.Nscans, " seconds found in the file. Is this file the first one of a time series acquistion? "

	    # Calculation the position of the nadir angle on the BeamNadirAngle vector
		CenterToLookFor=270
		b=np.abs(np.abs(self.BeamNadirAngle)-CenterToLookFor)
		self.nadirIndex=np.where(b==np.min(b))[0][0]
       
        # Calculating the position of the maximum and minimum angle to project on the BeamNadirAngle vector
		b1=np.abs(np.abs(self.BeamNadirAngle)-CenterToLookFor-SceneMaxAngle)
		ElMin=np.where(b1==np.min(b1))[0][0]
		b2=np.abs(np.abs(self.BeamNadirAngle)-CenterToLookFor+SceneMaxAngle)
		ElMax=np.where(b2==np.min(b2))[0][0]

		# Generating the anlge array for the projection 
		L=len(self.BeamNadirAngle)
		self.SceneIndex=np.mod(np.array(range(ElMin, ElMax))+L, L)
		NumberAnglesPerScann=len(self.SceneIndex)

		## Information display
		print "---> NadirIndex:", self.nadirIndex, "Swap:",ElMax-ElMin, "elevation angle points. Corresponding to motor angle:", self.MotorPosition[self.nadirIndex]*180/np.pi, ElMax, ElMin
		print "---> MinAngle:",self.BeamNadirAngle[ElMin]
		print "---> MaxAngle:",self.BeamNadirAngle[ElMax]
		print "---> NadirAngle:",self.BeamNadirAngle[self.nadirIndex]		
		print "---> Max-Min:", self.BeamNadirAngle[ElMax]-self.BeamNadirAngle[ElMin], 
		print "---> Max-Nadir:", self.BeamNadirAngle[ElMax]-self.BeamNadirAngle[self.nadirIndex],
		print "---> Nadir-Min:", self.BeamNadirAngle[self.nadirIndex]-self.BeamNadirAngle[ElMin]



		# Preparing for interpolating the position of the aircraft for each motor position.  
		diffsqueezedLat=np.diff(np.squeeze([self.Latitude], axis=1))
		diffsqueezedLon=np.diff(np.squeeze([self.Longitude], axis=1))

		# Projecting the antenna temperature, for each scan of the motor 
		for i in range(InitialTime, FinalTime):

			# Reading Euler angles form the GPS
			Pitch=1*self.Pitch[i]
			Roll=1*self.Roll[i]
			Yaw=1*self.Yaw[i]
			# Correcting the Yaw with the magnetic declination for each lat-lon coordinates point. 
			Chdg=self.correctingMagneticDeclination(Yaw, self.Latitude[i], self.Longitude[i])
			# Calculating the Bearing from the coordinates 
			Bearing=self.BearingFromLatLon(self.Latitude[i], self.Latitude[i+1], self.Longitude[i], self.Longitude[i+1])


			Verbose=True
			if Verbose== True: 
				print self.Channel, " --> Second:", i, " --> Roll:", Roll, "Pitch:", Pitch, "Yaw:", Yaw
				print "---> Corrected Heading:", Chdg, "Bearing:", Bearing, " Difference", Chdg-Bearing	     

			# Interpolating the position of the aircraft for each motor position.     
			if i<FinalTime-2:			
				Latmaxrange=(diffsqueezedLat[i]/L)*NumberAnglesPerScann/2
				Lonmaxrange=(diffsqueezedLon[i]/L)*NumberAnglesPerScann/2
			else:
				Latmaxrange=(diffsqueezedLat[i-1]/L)*NumberAnglesPerScann/2
				Lonmaxrange=(diffsqueezedLon[i-1]/L)*NumberAnglesPerScann/2			
			LatScanningArray=np.linspace(self.Latitude[i]-Latmaxrange, self.Latitude[i]+Latmaxrange,NumberAnglesPerScann )
			LonScanningArray=np.linspace(self.Longitude[i]-Lonmaxrange, self.Longitude[i]+Lonmaxrange,NumberAnglesPerScann )

		    # Projecting the antenna temperature, for each elevation angle of the scan
			for j, ElevationIndex in enumerate(self.SceneIndex):

				if self.AntennaTemperature[i][ElevationIndex]>0:

				    TAoffset=0 
				    # Reading the true course of the antenna for each elevation angle, form the motor onboard
				    # Note that the coordinates are rotated 90 degrees in z, this is because the navigation coordinates and the reference frame that we used for 
				    # calculating the antenna rotation are 90 degrees rotated
				    #z=self.truecourse_z[ElevationIndex] 
				    #x=-self.truecourse_y[ElevationIndex] 
				    #y=self.truecourse_x[ElevationIndex] 

				    ## Matching the flat reflector coordiantes with the aircraft and GPS/IMU coordinates. 	
				    z=-self.truecourse_z[ElevationIndex] 
				    x=self.truecourse_x[ElevationIndex] 
				    y=-self.truecourse_y[ElevationIndex] 	
				    ## Calculating the flat reflector pointing vector, easy! 
				    FlatReflectorPointingVector=np.array([x,y,z])
				    ## Correcrting the pointing taking into account the aircraf attitude. 		    
				    AntennaPointingVector=self.CorrectFlatReflectorPointingVector(1*Pitch, -1*Roll, -Chdg, FlatReflectorPointingVector)
				    ## Just in case the Yaw of the GPS is not working properly
				    #AntennaPointingVector=self.CorrectFlatReflectorPointingVector(1*Pitch, 1*Roll, -Bearing, FlatReflectorPointingVector)
				    ## Calculating and storing the center of the footprint for each scan and for each elevation angle in UTM and Lat-Lon
				    X, Y, UTMZoneNumber, UTMZoneLetter, ECenter_Easting, ECenter_Northing=self.calculateEllipseCenterandAxis(LatScanningArray[j], LonScanningArray[j], self.Altitude[i], AntennaPointingVector, self.Antenna_BeamWidth3dB)
				    ECenterLat, ECenterLon=utm.to_latlon(ECenter_Easting, ECenter_Northing, UTMZoneNumber, UTMZoneLetter)
				    ## Storing results in Lat-Lon
				    self.ECenterLatVector.append(np.array(ECenterLat))
				    self.ECenterLonVector.append(np.array(ECenterLon))
				    self.AntennaTemperatureVectorLatLon.append(self.AntennaTemperature[i][ElevationIndex]-TAoffset)
				    ## Storing results in UTM
				    self.ECenter_EastingVector.append(ECenter_Easting)
				    self.ECenter_NorthingVector.append(ECenter_Northing)
				    self.AntennaTemperatureVector.append(self.AntennaTemperature[i][ElevationIndex])
				    ## Storing Auxilar information
				    self.TimeVector.append(self.GPSTime[i])
				    self.AltitudeVector.append(self.Altitude[i])

				    # Calculating the points of the whole footprint, not only the center but the contour
				    if PrintWholeEllipse==True:
					    for cou in range(0,len(X)):
					    	self.ECenter_EastingVector.append(np.array(X[cou]))
					    	self.ECenter_NorthingVector.append(np.array(Y[cou]))
					    	self.AntennaTemperatureVector.append(self.AntennaTemperature[i][ElevationIndex])			    	
				
				if ElevationIndex==self.nadirIndex:
					self.NadirPointingGroundElevationAngle.append(np.arccos(AntennaPointingVector[2]))	    		

		self.UTMZoneNumber=UTMZoneNumber
		self.UTMZoneLetter=UTMZoneLetter  

		
		# Displaying basic information regarding the overall projection 
		print "---> First point:", self.Latitude[0][0], self.Longitude[0][0]
		print "---> Last point:", self.Latitude[-1][0], self.Longitude[-1][0]
		return

###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################
## Display seciton
###############################################################################################################################################
###############################################################################################################################################
###############################################################################################################################################

    def Mapping(self, XVector, YVector, SpatialResolutionX, SpatialResolutionY, Xm, Ym, AntennaTemperatureVector):
    	##############################################
    	# This function maps a vector paired ground X-Y and Tant into a X-Y grid matrix with SpatialResolutionX and SpatialResolutionY resolution.
    	# The ouptut is an image. This function implements a basic mapping algorithm from a vector to matrix. 
		##############################################

		# Getting the shape of the grid 
		a=Xm.shape[0]
		b=Xm.shape[1]
		MAP=np.empty(Xm.shape)

		# starting the maping itself. 		
		for element in  range(0,len(XVector)): 
		    
		    # Only if the antenna temperature is bigger than 0. This is to prevent mapping values marked as missing (-9999). 
		    if AntennaTemperatureVector[element]>0:			
			    indexX = np.floor((XVector[element] - Xm[0,0])/SpatialResolutionX)
			    indexY = np.floor((YVector[element] - Ym[0,0])/SpatialResolutionY)
			    index = int(Xm.shape[0]*(indexY-1) + indexX)
			    x=np.mod(index,a)
			    y=index/int(a)

			    # Making sure that the calculated position fits into the matrix, otherwise rise a WARNING. 
			    if x<=a-1 and y<=b-1:
			    	# Assign the Ta to the right position 
			    	MAP[x,y]=AntennaTemperatureVector[element]
			    else:
			    	print "----> WARNING:: Image out of spatial range. This is not normal, most probably you set some parameters wrong."

		return MAP

    def plotAuxData(self,filenameroot):

		fignum=200
		fig0=pl.figure(fignum)
		ax = fig0.add_subplot(111)    
		pl.plot(180/np.pi*self.MotorPosition,self.truecourse_z, '.', color='blue',  label='True Course Z')
		pl.plot(180/np.pi*self.MotorPosition,self.truecourse_y, '.', color='green', label='True Course Y')
		pl.plot(180/np.pi*self.MotorPosition,self.truecourse_x, '.', color='red',  label='True Course X')	    
		pl.plot(180/np.pi*self.MotorPosition,self.zmotor, '*', color='blue', label='Motor Z')
		pl.plot(180/np.pi*self.MotorPosition,self.ymotor, '*', color='green',label='Motor Y')
		pl.ylabel('Beam Pointing Vector')
		pl.xlabel('Motor Angle') 			
		title='Beam Pointing Vector Vs Motor Position ' + self.RadiometricSubset
		pl.title(title)
		pl.grid(True)		
		pl.legend(loc = 'best',shadow = True)
		fig0.suptitle(filenameroot, fontsize=5)				    
		pl.show(block=False)
		figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
		fig0.savefig(figfilename)     

		fignum=2100
		fig0=pl.figure(fignum)
		title='Beam Pointing Vector Vs Motor Position ' + self.RadiometricSubset
		pl.title(title)		
		ax = fig0.add_subplot(311)    
		pl.plot(self.truecourse_z,self.AntennaTemperature[0], '.', color='blue',  label='True Course Z')
		pl.plot(self.truecourse_z[0],self.AntennaTemperature[0][0], 'o', color='red',  label='First SampleTrue Course Z')
		pl.grid(True)
		#pl.legend(loc = 'best',shadow = True)					
		ax = fig0.add_subplot(313)    		
		pl.plot(self.truecourse_x,self.AntennaTemperature[0], '.', color='blue',  label='True Course X')
		pl.plot(self.truecourse_x[0],self.AntennaTemperature[0][0], 'o', color='red',  label='First SampleTrue Course X')
		pl.grid(True)
		#pl.legend(loc = 'best',shadow = True)				
		ax = fig0.add_subplot(312)    		
		pl.plot(self.truecourse_y,self.AntennaTemperature[0], '.', color='blue',  label='True Course Y')
		pl.plot(self.truecourse_y[0],self.AntennaTemperature[0][0], 'o', color='red',  label='First SampleTrue Course Y')
		pl.grid(True)
		#pl.legend(loc = 'best',shadow = True)								
		#pl.plot(180/np.pi*self.MotorPosition,self.truecourse_y, '.', color='green', label='True Course Y')
		#pl.plot(180/np.pi*self.MotorPosition,self.truecourse_x, '.', color='red',  label='True Course X')	    
		#pl.plot(180/np.pi*self.MotorPosition,self.zmotor, '*', color='blue', label='Motor Z')
		#pl.plot(180/np.pi*self.MotorPosition,self.ymotor, '*', color='green',label='Motor Y')
		pl.ylabel('Beam Pointing Vector')
		pl.xlabel('Motor Angle') 			
		
			
		#pl.legend(loc = 'best',shadow = True)
		fig0.suptitle(filenameroot, fontsize=5)				    
		pl.show(block=False)
		figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
		fig0.savefig(figfilename)    


		fignum=2101
		fig0=pl.figure(fignum)
		title='Beam Pointing Vector Vs Motor Position ' + self.RadiometricSubset
		pl.title(title)		
		ax = fig0.add_subplot(111)    
		pl.plot(self.BeamNadirAngle,self.AntennaTemperature[0], '.', color='blue',  label='Antenna Temperature')
		pl.plot(self.BeamNadirAngle[0],self.AntennaTemperature[0][0], 'o', color='red',  label='First SampleTrue Course Antenna Temperature')
		pl.plot(self.BeamNadirAngle[self.nadirIndex],self.AntennaTemperature[0][self.nadirIndex], 'o', color='black',  label='NADIR')	
		pl.grid(True)
		pl.ylabel('Beam Pointing Vector')
		pl.xlabel('Motor Angle') 			
		fig0.suptitle(filenameroot, fontsize=5)				    
		pl.show(block=False)
		figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
		fig0.savefig(figfilename)  



		fignum=2102
		fig0=pl.figure(fignum)
		title='Beam Pointing Vector Vs Motor Position ' + self.RadiometricSubset
		pl.title(title)		
		ax = fig0.add_subplot(111)    
		pl.plot(self.MotorPosition,self.AntennaTemperature[0], '.', color='blue',  label='Antenna Temperature')
		pl.plot(self.MotorPosition[0],self.AntennaTemperature[0][0], 'o', color='red',  label='First SampleTrue Course Antenna Temperature')
		pl.plot(self.MotorPosition[self.nadirIndex],self.AntennaTemperature[0][self.nadirIndex], 'o', color='black',  label='NADIR')	
		pl.grid(True)
		pl.ylabel('Beam Pointing Vector')
		pl.xlabel('Motor Angle') 			
		fig0.suptitle(filenameroot, fontsize=5)				    
		pl.show(block=False)
		figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
		fig0.savefig(figfilename)  

		fignum=210
		fig0=pl.figure(fignum)
		ax = fig0.add_subplot(111)    
		pl.plot(180/np.pi*self.MotorPosition, '.', label='Motor Position')    	    
		pl.ylabel('Motor Position')
		pl.xlabel('Motor Angle') 			
		title='Motor Position ' + self.RadiometricSubset
		pl.title(title)
		pl.grid(True)		
		pl.legend(loc = 'best',shadow = True)
		fig0.suptitle(filenameroot, fontsize=5)				    
		pl.show(block=False)
		figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
		fig0.savefig(figfilename)   


		fignum=201
		fig0=pl.figure(fignum)
		ax = fig0.add_subplot(111)    
		pl.plot(self.Longitude,self.Latitude)
		pl.legend(loc = 'best',shadow = True)
		title='LatLon trajectory '
		pl.ylabel('Latitude')
		pl.xlabel('Longitude') 	    
		pl.title(title)
		fig0.suptitle(self.filenameroot, fontsize=5)
		pl.grid()
		pl.axis('equal')
		locs,labels = pl.xticks()
		pl.xticks(locs, map(lambda x: "%g" % x, locs-min(locs)))
		pl.text(0.92, -0.07, "Offset: %g" % min(locs), fontsize=10, transform = gca().transAxes)				    	    
		pl.show(block=False)
		figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
		fig0.savefig(figfilename)	    


		fignum=202
		fig0=pl.figure(fignum)
		ax = fig0.add_subplot(111)
		pl.plot(self.Pitch, label='Pitch', color='k')
		pl.plot(self.Roll, label='Roll', color='g')   
		pl.plot(self.Yaw, label='Yaw', color='r', marker='.')
		Yaw=1*self.Yaw
		Yaw[np.where(self.Yaw<0)]=Yaw[np.where(self.Yaw<0)]+360
		self.Yaw=Yaw
		pl.plot(self.Yaw, label='compensated Yaw', color='g')	    
		pl.legend(loc = 'best',shadow = True)
		title='Aircraft Attitude '
		pl.title(title)
		pl.ylabel('Degrees')		
		pl.xlabel('Time [s]') 		
		fig0.suptitle(self.filenameroot, fontsize=5)
		pl.grid()		    
		pl.show(block=False)
		figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
		fig0.savefig(figfilename)   

		fignum=203
		fig0=pl.figure(fignum)
		ax = fig0.add_subplot(111)    
		pl.plot(self.Altitude)
		pl.legend(loc = 'best',shadow = True)
		title='Altitude'
		pl.ylabel('Altitude [m]')
		pl.xlabel('Time [s]') 	    
		pl.title(title)
		fig0.suptitle(self.filenameroot, fontsize=5)
		pl.grid()		    	    
		pl.show(block=False)
		figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
		fig0.savefig(figfilename)	

		fignum=204
		fig0=pl.figure(fignum)
		ax = fig0.add_subplot(111)    
		pl.plot(self.MotorPosition, self.BeamNadirAngle,'.', label='Beam Angle')
		pl.plot(self.MotorPosition[self.SceneIndex], self.BeamNadirAngle[self.SceneIndex],'r.', label='Scene Beam Angle')
		pl.legend(loc = 'best',shadow = True)
		title='Motor Position Vs Beam Angle '+ self.RadiometricSubset
		pl.ylabel('Beam Angle ')
		pl.xlabel('Motor Position') 	    
		pl.title(title)
		fig0.suptitle(self.filenameroot, fontsize=5)
		pl.grid()		    	    
		pl.show(block=False)
		figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png')
		fig0.savefig(figfilename)
		matplotlib.pyplot.close("all")

		return None
    def createLatLonImage(self,fignum,LonM, LatM, MAP_AT_LatLon,  z_min, z_max, keepMatrix=False, title='Trajectory LatLon for ', DisplayFileName=False):

		fig0=pl.figure(fignum)
		ax = fig0.add_subplot(111)
		y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)


		masked_array=np.ma.masked_where(MAP_AT_LatLon<=0, MAP_AT_LatLon)
		cmap = matplotlib.cm.jet
		cmap.set_bad('w',1.)
		#if keepMatrix==True:
		#	self.masked_array=masked_array
		#	self.keepAntennaTemperatureMatrix()

		p = ax.pcolor(LonM, LatM, masked_array, vmin=z_min, vmax=z_max, cmap=cmap)    
		pl.xlabel('Lon')
		pl.ylabel('Lat')

		cb = fig0.colorbar(p, ax=ax, label='Kelvin')
		title2=title + self.Channel.replace("p", "+").replace("m", "-").replace('MMW', 'Millimeter-wave').replace("MW", 'Microwave').replace('SND', 'Sounder').replace('_', ' ')

		figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+self.Channel+'.png')
		pl.title(title2)  
		pl.axis('equal')
		locs,labels = pl.xticks()
		pl.xticks(locs, map(lambda x: "%g" % x, locs-min(locs)))
		pl.text(0.92, -0.07, "Offset: %g" % min(locs), fontsize=10, transform = gca().transAxes)
		if DisplayFileName :
			fig0.suptitle(self.filenameroot, fontsize=5)
		pl.axis('equal')		
		pl.show(block=False)
		fig0.savefig(figfilename, transparent=True) 	

    def createUTMImage(self,fignum,X, Y, MAP_AT_UTM,  z_min, z_max, title='Antenna Temperature for ', DisplayFileName=False, Legend='Kelvin'):	
		import matplotlib.ticker as ticker
		fig0=pl.figure(fignum)
		ax = fig0.add_subplot(111)
		y_formatter = matplotlib.ticker.ScalarFormatter(useOffset=False)

		masked_array=np.ma.masked_where(MAP_AT_UTM<=0, MAP_AT_UTM)
		cmap = matplotlib.cm.jet
		cmap.set_bad('w',1.)

		p = ax.pcolor(X, Y, masked_array, vmin=z_min, vmax=z_max, cmap=cmap)
		pl.xlabel(u'Km East of Longitude 126\N{DEGREE SIGN} W')
		pl.ylabel(u'Km North of Latitude 0\N{DEGREE SIGN} N')

		cb = fig0.colorbar(p, ax=ax, label=Legend)
		title2=title + self.Channel.replace("p", "+").replace("m", "-").replace('MMW', 'Millimeter-wave').replace("MW", 'Microwave').replace('SND', 'Sounder').replace('_', ' ')
		figfilename =os.path.join(self.pathfordata,str(fignum)+' '+title+self.Channel+'.png')
		pl.title(title2)
		pl.axis('equal')
		################################################################
		#################################################################		


		start, end = ax.get_ylim()
		ax.yaxis.set_ticks(np.arange(start, end, 2000))
		ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%g'))		
		locs,labels = pl.yticks()
		pl.yticks(locs, map(lambda x: "%g" % x, locs/1000))	

		start, end = ax.get_xlim()
		ax.xaxis.set_ticks(np.arange(start, end, 2000))
		ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%g'))
		locs,labels = pl.xticks()
		pl.xticks(locs, map(lambda x: "%g" % x, locs/1000))		
			
		pl.text(0.92, -0.07, "UTM Zone: %g%s" % (self.UTMZoneNumber, self.UTMZoneLetter), fontsize=9, transform = gca().transAxes)
		################################################################
		#################################################################		
		if DisplayFileName :
			fig0.suptitle(self.filenameroot, fontsize=5)
		pl.axis('equal')				
		pl.show(block=False)
		fig0.savefig(figfilename, transparent=True) 	



    def createKMLfile(self,fignum,X, Y, MAP_AT_UTM,z_min,z_max, title= 'No Axes LatLon Antenna Temperature for '):

	    KMLfileAux=fileKML()
	    fig0, ax=KMLfileAux.gearth_fig(self.llcrnrlon, self.llcrnrlat, self.urcrnrlon, self.urcrnrlat, pixels=1024)
	    
	    #fig0=pl.figure(fignum) 	    
	    #ax = plt.Axes(fig0, [0., 0., 1., 1.])
	    fig0.add_axes(ax)
	    #ax.set_autoscale_on(False)
	    masked_array=np.ma.masked_where(MAP_AT_UTM==0, MAP_AT_UTM)

	    cmap = matplotlib.cm.jet
	    cmap.set_bad('w',1.)
	    p = ax.pcolor(X, Y, masked_array, vmin=z_min, vmax=z_max, cmap=cmap)
	    ax.set_axis_off()
	    pl.show( block=False)
	    title=title + self.Channel
	    filenameOverlay = os.path.join(self.pathfordata, str(fignum)+'_'+title.replace(" ", "_")+'.png')
	    fig0.savefig(filenameOverlay, transparent=True, pad_inches = 0)      	    
	    

  	    fig = plt.figure(figsize=(1.0, 4.0), facecolor=None, frameon=False)
	    ax = fig.add_axes([0.0, 0.05, 0.2, 0.9])
	    ax.set_axis_off()
	    cb = fig.colorbar(p, ax=ax)
	    cb.set_label('Antenna Temperature [K]', rotation=-90, color='k', labelpad=20)
	    filenameLegend = os.path.join(self.pathfordata, str(fignum)+'_'+title.replace(" ", "_")+'legend.png')
	    fig.savefig(filenameLegend, transparent=False, format='png')



	    #pl.axis('off')	   
	    #p.axes.get_xaxis().set_visible(False)
	    #p.axes.get_yaxis().set_visible(False)
	    #extent = ax.get_window_extent().transformed(pl.gcf().dpi_scale_trans.inverted())
	    #pl.axis('equal') 	
	    # bbox_inches=extent,     	    
	    
    	    #

	    ############################################################################
	    title='Antenna Temperature for '+ self.Channel
	    kmlfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_"))
	    #figfilename =str(fignum)+'_'+title.replace(" ", "_")+'.png'
	    #figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png') 
	    #kmloverlay=KMLfileAux.createFile(figfilename, self.urcrnrlat, self.llcrnrlat, self.urcrnrlon, self.llcrnrlon, kmlfilename, FolderName=self.filenameroot,  verbose=False)
		
	    KMLfileAux.make_kml(llcrnrlon=self.llcrnrlon, llcrnrlat=self.llcrnrlat, urcrnrlon=self.urcrnrlon, urcrnrlat=self.urcrnrlat, figs=[filenameOverlay],colorbar=filenameLegend, kmzfile=kmlfilename+'.kmz',name='MeanDynamicTopographyandvelocity')
	    return 	

def main():
    print 'Hi, this is a class not an script'
    return


if __name__ == "__main__":
    main()
