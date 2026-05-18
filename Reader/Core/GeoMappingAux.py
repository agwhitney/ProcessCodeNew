import numpy as np
import os
import sys
import pylab as pl
import matplotlib as mpl
import geomag
from pylab import *
import tables as tb
import utm as utm
import time
from scipy import linalg
#from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.ticker as ticker
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import matplotlib.pyplot as plt
configfile='..\..\GeneralPaths.py'
#configfile='..\GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import L1a_DATA_PROCESSED_PATH
from KMLfileAux import fileKML
from L1bFileAux import CreateGeoReferencedAntennaTempeartureFile

class datamapping:

    def __init__(self, Channel, filenameroot, pathfordata):

    	self.Channel=Channel
    	self.filenameroot=filenameroot
    	self.pathfordata=pathfordata
    	self.llcrnrlat=0
    	self.llcrnrlon=0
    	self.urcrnrlon=0
    	self.urcrnrlat=0    	
    	self.UTMZoneNumber=0
    	self.UTMZoneLetter='a'
    	return

    def SetCoordinates(self, urcrnrlat, llcrnrlat, urcrnrlon, llcrnrlon, SpatialResolutionX=10, SpatialResolutionY=10, SpatialResolutionlon=0.0001,  SpatialResolutionlat= 0.0001):
		####################################################################
		self.urcrnrlat=urcrnrlat
		self.llcrnrlat=llcrnrlat
		self.urcrnrlon=urcrnrlon
		self.llcrnrlon=llcrnrlon
		####################################################################
		self.SpatialResolutionX=SpatialResolutionX
		self.SpatialResolutionY=SpatialResolutionY
		self.SpatialResolutionlon=SpatialResolutionlon
		self.SpatialResolutionlat=SpatialResolutionlat
		####################################################################		
		llcUTMconversion=utm.from_latlon(llcrnrlat, llcrnrlon)
		urcUTMconversion=utm.from_latlon(urcrnrlat, urcrnrlon)
		# X, Y are the nadir position in UTM
		# X_, Y_ are the projected center of the ellipse in UTM
		Xllc=llcUTMconversion[0] 
		Yllc=llcUTMconversion[1]
		Xurc=urcUTMconversion[0] 
		Yurc=urcUTMconversion[1] 
		#print Xurc, Xllc, Xurc-Xllc, type(Xurc)
		#print Yurc, Yllc, Yurc-Yllc    
		ImagesizeXinMeters=np.abs(Xurc-Xllc)
		ImagesizeYinMeters=np.abs(Yurc-Yllc)    
		DeltaXMeters=np.round(ImagesizeXinMeters/SpatialResolutionX)
		DeltaYMeters=np.round(ImagesizeYinMeters/SpatialResolutionY)
		print "---> Map dimensions in meters X:", ImagesizeXinMeters, '  Y:', ImagesizeYinMeters
		self.Ym, self.Xm =np.meshgrid(np.linspace(np.min([Yllc, Yurc]),np.max([Yllc, Yurc]), DeltaYMeters),np.linspace(np.min([Xllc, Xurc]), np.max([Xllc, Xurc]),DeltaXMeters)) 

		Imagesizelon=np.abs(llcrnrlon-urcrnrlon)
		Imagesizelat=np.abs(llcrnrlat-urcrnrlat)    
		DeltaLon=np.round(Imagesizelon/SpatialResolutionlon)
		DeltaLat=np.round(Imagesizelat/SpatialResolutionlat)
		print "---> Map dimensions in Lon:", Imagesizelon, 'Degrees. Lat:', Imagesizelat, 'Degrees'
		self.LatM, self.LonM=np.meshgrid(np.linspace(np.min([llcrnrlat, urcrnrlat]),np.max([llcrnrlat, urcrnrlat]), DeltaLat),np.linspace(np.min([llcrnrlon, urcrnrlon]),np.max([llcrnrlon, urcrnrlon]) ,DeltaLon)) 
		return

    def SpatialAverager(self, ValueOfInterestVector, radius, threshold, element, XVector, YVector):
		# Calcular distanica del punt a tota la resta
		# Buscar tots els punt a una distancia menor que X i que els valors tinguin sentit
		# assignar a MAP
		distances=np.sqrt(np.square(XVector-XVector[element]) +np.square(YVector-YVector[element]))
		#radius =0.04
		ClosePointsIndex=np.where(distances<radius)[0]
		print len(ClosePointsIndex)
		if len(ClosePointsIndex)>0:
			return np.NaN
		else:
			correctClosePointsIndex=np.where(ValueOfInterestVector[ClosePointsIndex]<threshold)[0]
			return np.mean(ValueOfInterestVector[correctClosePointsIndex])
		return

    def MapAssigment(self, XVector, YVector, SpatialResolutionX, SpatialResolutionY, Xm, Ym, ValueOfInterestVector):
    	##############################################
    	# This function maps a vector paired ground X-Y and Tant into a X-Y grid matrix with SpatialResolutionX and SpatialResolutionY resolution.
    	# The ouptut is an image. This function implements a basic mapping algorithm from a vector to matrix. 
		##############################################
		SpatialAverager=True
		threshold=30
		radius=0.0004 #in lat-lon
		# Getting the shape of the grid 
		a=Xm.shape[0]
		b=Xm.shape[1]
		MAP=np.empty(Xm.shape)
		
		####
		start_time = time.time()

		print len(ValueOfInterestVector), len (XVector)
		# starting the maping itself. 		
		for element in  range(0,len(XVector)): 
		    
		    # Only if the antenna temperature is bigger than 0. This is to prevent mapping values marked as missing (-9999). 
		    if ValueOfInterestVector[element]>0:			
			    indexX = np.floor((XVector[element] - Xm[0,0])/SpatialResolutionX)
			    indexY = np.floor((YVector[element] - Ym[0,0])/SpatialResolutionY)
			    index = int(Xm.shape[0]*(indexY-1) + indexX)
			    x=np.mod(index,a)
			    y=index/int(a)

			    # Making sure that the calculated position fits into the matrix, otherwise rise a WARNING. 
			    if x<=a-1 and y<=b-1:
			    	# Assign the Ta to the right position 
			    	#MAP[x,y]=ValueOfInterestVector[element]

			    	### Spatial averager
			    	
			    	#if SpatialAverager==True:
			    	#	MAP[x,y]=self.SpatialAverager(ValueOfInterestVector, radius, threshold, element, XVector, YVector)
			    	#else: 
			    	MAP[x,y]=ValueOfInterestVector[element]	

			    else:
			    	print "----> WARNING:: Image out of spatial range. This is not normal, most probably you set some parameters wrong."
		
		elapsed_time = time.time() - start_time
		print "Elapsed time: " + str(elapsed_time) #+ "Variable SpatialAverager=", SpatialAverager
		return MAP

    def TriangularInterpolation(self,x,y,z):
			import matplotlib.pyplot as plt
			from matplotlib.tri import Triangulation, TriAnalyzer, UniformTriRefiner
			import matplotlib.tri as mtri
			
			triang = mtri.Triangulation(x, y)

			# Some invalid data are masked out
			min_circle_ratio = .01
			mask = TriAnalyzer(triang).get_flat_tri_mask(min_circle_ratio)
			refiner = UniformTriRefiner(triang)
			subdiv = 3  
			triang_refi, z_test_refi = refiner.refine_field(z, subdiv=subdiv)
			triang.set_mask(mask)


	
			#print x.shape, y.shape, z.shape
			#triang = mtri.Triangulation(x,y)		
			#xmid = x[triang.triangles].mean(axis=1)
			#ymid = y[triang.triangles].mean(axis=1)
			#mask = np.where(xmid*xmid + ymid*ymid < min_radius*min_radius, 1, 0)
			#triang.set_mask(mask)

			#print np.min(x), np.max(x), np.max(x)-np.min(x), np.round((np.max(x)-np.min(x))/self.SpatialResolutionX)
			px=np.linspace(np.min(x), np.max(x),np.round((np.max(x)-np.min(x))/self.SpatialResolutionX))
			py=np.linspace(np.min(y), np.max(y), np.round((np.max(y)-np.min(y))/self.SpatialResolutionY))
			#print py.shape
			xi, yi = np.meshgrid(px,py)
			#print xi.shape, yi.shape, px.shape, py.shape
			interp_lin = mtri.LinearTriInterpolator(triang_refi, z_test_refi)


			#interp_lin = mtri.CubicTriInterpolator(triang, z, kind=u'min_E')
			zi_lin = interp_lin(xi, yi)
			return xi, yi, zi_lin


    def createKMLfile(self, fignum, X, Y, MAP_AT_UTM, z_min, z_max, title= 'No Axes LatLon Antenna Temperature for '):

	    KMLfileAux=fileKML()
	    fig0, ax=KMLfileAux.gearth_fig(self.llcrnrlon, self.llcrnrlat, self.urcrnrlon, self.urcrnrlat, pixels=1024)
	    
	    #from scipy import ndimage
	    #MAP_AT_UTMb[np.where(MAP_AT_UTMb==0)[0]]=np.nan
	   # MAP_AT_UTM = MAP_AT_UTMb  #ndimage.gaussian_filter(MAP_AT_UTMb, 0.0000003)
	    
	    #import scipy.io as sio
	    #sio.savemat('test.mat', {'vect':MAP_AT_UTM, 'X':X, 'Y':Y})


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
	    

  	    fig = plt.figure(figsize=(2.0, 3.0), facecolor=None, frameon=False)
	    ax = fig.add_axes([0.0, 0.05, 0.2, 0.9])
	    ax.set_axis_off()
	    cb = fig.colorbar(p, ax=ax)
	    cb.set_label('Antenna Temperature [K]', rotation=-90, color='k', labelpad=20)
	    filenameLegend = os.path.join(self.pathfordata, str(fignum)+'_'+title.replace(" ", "_")+'legend.png')
	    fig.savefig(filenameLegend, transparent=False, format='png')


	    ############################################################################
	    title='Antenna Temperature for '+ self.Channel
	    kmlfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_"))
	    #figfilename =str(fignum)+'_'+title.replace(" ", "_")+'.png'
	    #figfilename =os.path.join(self.pathfordata,str(fignum)+'_'+title.replace(" ", "_")+'.png') 
	    #kmloverlay=KMLfileAux.createFile(figfilename, self.urcrnrlat, self.llcrnrlat, self.urcrnrlon, self.llcrnrlon, kmlfilename, FolderName=self.filenameroot,  verbose=False)
		
	    KMLfileAux.make_kml(llcrnrlon=self.llcrnrlon, llcrnrlat=self.llcrnrlat, urcrnrlon=self.urcrnrlon, urcrnrlat=self.urcrnrlat, figs=[filenameOverlay],colorbar=filenameLegend, kmzfile=kmlfilename+'.kmz',name='MeanDynamicTopographyandvelocity')
	    return 	

    def createLatLonImage(self,fignum, LonM, LatM, MAP_AT_LatLon,  z_min, z_max, keepMatrix=False, title='Trajectory LatLon for ', DisplayFileName=False, Legend='Kelvin'):

		fig0=pl.figure(fignum)
		ax = fig0.add_subplot(111)
		y_formatter = ticker.ScalarFormatter(useOffset=False)


		masked_array=np.ma.masked_where(MAP_AT_LatLon<=0, MAP_AT_LatLon)
		cmap = matplotlib.cm.jet
		cmap.set_bad('w',1.)
		#if keepMatrix==True:
		#	self.masked_array=masked_array
		#	self.keepAntennaTemperatureMatrix()

		p = ax.pcolor(LonM, LatM, masked_array, vmin=z_min, vmax=z_max, cmap=cmap)    
		pl.xlabel('Lon')
		pl.ylabel('Lat')

		cb = fig0.colorbar(p, ax=ax, label=Legend)
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
		return 	

    def createUTMImage(self,fignum,X, Y, MAP_AT_UTM,  z_min, z_max, title='Antenna Temperature for ', DisplayFileName=False, Legend='Kelvin'):	
		
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
		return


def main():
    print 'Hi, this is a class not an script'
    return


if __name__ == "__main__":
    main()
