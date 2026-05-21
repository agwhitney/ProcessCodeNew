# -*- coding: utf-8 -*-
"""
Created on Tue Jul 15 14:24:12 2014

@author: xbosch
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure



class GPSIMU:
    def __init__(self, h5file, verbose=True):
        print("INFO: new instance of GPS-IMU data")
        data = h5file.root.GPS_IMUData.GPSIMU_DATA

        self.GPS_EulerAngles = np.array([x['EulerAngles'] for x in data.iterrows()])
        self.GPS_Timestamp = np.array([x['Timestamp'] for x in data.iterrows()]).flatten()
        self.GPS_GPSTime = np.array([x['GPSTime'] for x in data.iterrows()]).flatten()
        self.GPS_Position = np.array([x['Position'] for x in data.iterrows()])
        self.GPS_Packagenumber = np.array([x['Packagenumber'] for x in data.iterrows()]).flatten()
        self.length = len(self.GPS_Packagenumber)
    

    def printEulerAngles(self, title="") -> Figure:
         fig=plt.figure(8001) 
         plt.plot(self.GPS_Timestamp-self.GPS_Timestamp[0], self.GPS_EulerAngles[:,0]*180/np.pi,  color='green', label="Roll")
         plt.plot(self.GPS_Timestamp-self.GPS_Timestamp[0], self.GPS_EulerAngles[:,1]*180/np.pi,  color='black', label="Pitch")
         plt.plot(self.GPS_Timestamp-self.GPS_Timestamp[0], self.GPS_EulerAngles[:,2]*180/np.pi,  color='red', marker='.', label="Yaw")
         plt.ylabel("Angle [Degree]")
         plt.xlabel("Seconds")
         plt.title('Attitude ' +title, fontsize=12)
         plt.legend(loc = 'best',shadow = True)
         plt.grid(True)
         plt.show(block=False)
         return fig
        

    def printAltitude(self, title="") -> Figure:
         fig=plt.figure(8002) 
         plt.plot(self.GPS_Timestamp-self.GPS_Timestamp[0],self.GPS_Position[:,2],  color = '#a2a7ff', label="MSL")
         plt.ylabel("Altitude [m]")
         plt.xlabel("Seconds")
         plt.title('Altitude ' +title, fontsize=12)
         plt.legend(loc = 'best',shadow = True)
         plt.grid(True)
         plt.show(block=False)
         return fig
         

    def printTrajectory(self, title="") -> Figure:
         fig=plt.figure(8003) 
         plt.rc('xtick', labelsize=16) 
         plt.rc('ytick', labelsize=16)
         font = {'size': 14}
         plt.rc('font', **font)
         plt.plot(self.GPS_Position[:,1],self.GPS_Position[:,0],  color = 'black', label="Trajectory")
         plt.plot(self.GPS_Position[0,1],self.GPS_Position[0,0],  color = 'red',  marker='o',label="Start point")
         plt.plot(self.GPS_Position[self.length-1,1],self.GPS_Position[self.length-1,0],  color = 'green',  marker='o',label="End point")
         plt.ylabel("Lat[deg]")
         plt.xlabel("Lon[deg]")
         plt.title('Trajectory ' +title, fontsize=12)
         plt.legend(loc = 'best',shadow = True)
         plt.ticklabel_format(style='plain', axis='x', useOffset=False)
         plt.grid(True)
         plt.show(block=False)
         print("GPS Coordinates Starting point Lat:", self.GPS_Position[0,0], "- Lon:",self.GPS_Position[0,1])
         print("GPS Coordinates Ending point Lat:", self.GPS_Position[self.length-1,0], "- Lon:",self.GPS_Position[self.length-1,1])
         print("------------------------------"          )
         return fig
         

    def printTimeDelay(self) -> Figure:
         fig=plt.figure(8004) 
         plt.plot(self.GPS_Timestamp,self.GPS_GPSTime-self.GPS_Timestamp,  color = 'black', label="Computer Delay Respect GPS time")
         plt.ylabel("GPS Time")
         plt.xlabel("Linux Time Error")
         plt.title('Time Delay')
         plt.legend(loc = 'best',shadow = True)
         plt.grid(True)
         plt.show(block=False)
         return fig


# def main():
#     import tables as tb
#     import os
#     import sys
#     configfile='..\..\GeneralPaths.py'
#     sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
#     from GeneralPaths import H5_DATA_BASE_PATH

#     print("\n\n###This is a Class, not to be run as a SCRIPT##")
#     filenameroot='2014_11_07__10_35_39__2of30_WCFC_Day4_GoingToCrescentCity'


#     plt.rc('xtick', labelsize=18) 
#     plt.rc('ytick', labelsize=18)
#     font = {'size': 14}
#     plt.rc('font', **font)

#     filename=filenameroot+'.h5'
#     print("WARNING: %s is provided with the repository for debugin purposes only"%filename)
#     if not os.path.isabs(filename):
#         filenameh5 = os.path.join(H5_DATA_BASE_PATH, filename)
        
#     h5file=tb.open_file(filenameh5, mode = "r")
#     print("-----------------------------------------")
#     for group in h5file.walkGroups("/"):
#         print("--", group)
#     print("-----------------------------------------")
#     GPSIMU_Instance=GPSIMU(h5file)
#     GPSIMU_Instance.printEulerAngles()
#     GPSIMU_Instance.printAltitude()
#     GPSIMU_Instance.printTrajectory()
#     GPSIMU_Instance.printTimeDelay()


# if __name__ == "__main__":
#     main()