import platform
import os
from pathlib import Path
#########################################
Verbose=True
# Using Xavi's computer
# ROOTPATH_Windows=r"D:\OneDrive - Colostate\Research - Radiometry\MiniMAC\HAMMR\HAMMR metadata"  # Change to point locally
# # ROOTPATH_Windows=r"C:\Users\adamgw\OneDrive - Colostate\Research - Radiometry\MiniMAC\HAMMR\HAMMR metadata"  # Change to point locally
# # Usign MSL Data Processor
# ROOTPATH_Linux='/home/msl/Documents'
# #ROOTPATH_Linux='/home/xavi'
# #########################################
# OperatingSystem=platform.system()
# #########################################
# if OperatingSystem=="Windows":
#    ROOTPATH=ROOTPATH_Windows
# else: 
#    ROOTPATH=ROOTPATH_Linux

#########################################
CollectedData='SystemOutput'; Data='Data'; h5files='Final_h5_files'; Logs='Logs'
Conf='Conf'; TMP='TMP'; Reader='Reader'; Results='Results'; CSVFiles='CSV batch files';
L1adata='L1adata'; L0bdata='L0bdata';L1bdata='L1bdata';L2adata='L2adata';L2bdata='L2bdata';CalCoefs='Calibration';
#########################################
BASE_PATH = Path(__file__).parent
# DATA_BASE_PATH=os.path.join(BASE_PATH, CollectedData, Data)
H5_DATA_BASE_PATH = BASE_PATH / 'L0bFiles'
# LOG_BASE_PATH = os.path.join(BASE_PATH, CollectedData, Logs)
# CONF_BASE_PATH=os.path.join(BASE_PATH, Conf) 
# CONF_BASE_PATH_TMP=os.path.join(CONF_BASE_PATH, TMP)
CVS_FILES_DATA_BASE_PATH=os.path.join(BASE_PATH, Reader, CSVFiles) 
L0b_DATA_PROCESSED_PATH=os.path.join(BASE_PATH, Reader, Results, L0bdata)
L1a_DATA_PROCESSED_PATH=os.path.join(BASE_PATH, Reader, Results, L1adata)
L1b_DATA_PROCESSED_PATH=os.path.join(BASE_PATH, Reader, Results, L1bdata)
L2a_DATA_PROCESSED_PATH=os.path.join(BASE_PATH, Reader, Results, L2adata)
L2b_DATA_PROCESSED_PATH=os.path.join(BASE_PATH, Reader, Results, L2bdata)
CALIBRATION_PATH=os.path.join(BASE_PATH, Reader, CalCoefs)
#########################################
#########################################
#CONTROL_SERVER_IP='127.0.0.1'
#CONTROL_SERVER_PORT=9083
#########################################
#########################################
In={"MW":0,"MMW":2,"SND":1} 
RadId={'MW', 'MMW', 'SND'}
bytesPerDatagram_ARM=22
bytesPerDatagram_ACT=14
bytesPerDatagram_SND=38
bytesPerDatagram=[bytesPerDatagram_ARM, bytesPerDatagram_SND, bytesPerDatagram_ACT]
#########################################
#########################################
CALVERSION=2
#########################################
#########################################
if Verbose==True:
    print('############################')
   #  print('Operating System:', OperatingSystem)
    # print( 'DATA_BASE_PATH:', DATA_BASE_PATH)
    print( 'H5_DATA_BASE_PATH:', H5_DATA_BASE_PATH)
    print( 'CVS_FILES_DATA_BASE_PATH:',CVS_FILES_DATA_BASE_PATH)
    # print( 'LOG_BASE_PATH:', LOG_BASE_PATH)
    # print( 'BASE_PATH:', BASE_PATH)
    # print( 'CONF_BASE_PATH:', CONF_BASE_PATH)
    # print( 'CONF_BASE_PATH_TMPCONF_BASE_PATH_TMP:', CONF_BASE_PATH_TMP)
    print( 'L0b_DATA_PROCESSED_PATH:', L0b_DATA_PROCESSED_PATH)
    print( 'L1a_DATA_PROCESSED_PATH:', L1a_DATA_PROCESSED_PATH)
    print( 'L1b_DATA_PROCESSED_PATH:', L1b_DATA_PROCESSED_PATH)
    print( 'CALIBRATION_PATH:', CALIBRATION_PATH)
    print( 'CALVERSION:', CALVERSION)
    print( '############################')
