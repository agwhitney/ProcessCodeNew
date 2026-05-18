#!/usr/bin/env python
from subprocess import Popen, PIPE
import time
import os
import sys
import scipy.io as sio
## To run it as a script uncoment this line
#configfile='..\..\GeneralPaths.py'
## To run it as a class uncoment this line
configfile='..\GeneralPaths.py'
sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
from GeneralPaths import L1b_DATA_PROCESSED_PATH, CALVERSION

class RunMatlabCode:
	def __init__(self, MatlabFunction, MatFileName, DataToProcessFileName):
		matfilename =os.path.join(L1b_DATA_PROCESSED_PATH, MatFileName+'.mat')
		matcontent={'name': DataToProcessFileName}
		sio.savemat(matfilename, matcontent)
		self.command='matlab -nojvm -nodesktop -nosplash -wait -r "' + MatlabFunction + ' \"' + matfilename +'\";quit"'
		print "Running the command: ", self.command, " for ",  DataToProcessFileName

	def run(self):
		os.chdir(L1b_DATA_PROCESSED_PATH)
		self.processes=[] 
		t1=time.time()
		self.processes.append(Popen(self.command, stdin=None, stdout=None, stderr=None, shell=True))
		print "MATLAB process started, Pid:", self.processes[0].pid,
		# Waiting the CLIENT instances to finish
		self.processes[0].wait()
		elapsedtime=time.time()-t1
		print "MATLAB process finished."
		print "Total MATLAB elapsed time: "+ str(elapsedtime) + " seconds"            
		print "------------------------------"

def main():
	import pylab as pl
	import numpy as np
	print "-------------------------------------------------------------------"
	print 'Hi, this is a class not a script'
	DataToProcessFileName='HAMMR_L1b_v002_2014_11_07__11_05_51__8of30_WCFC_Day4_GoingToCrescentCity'
	MatlabFunction='HAMMR_retrieval_alg_XBmodified_V002'
	MatFileName='Filename2process'
	RMC=RunMatlabCode(MatlabFunction, MatFileName, DataToProcessFileName)
	RMC.run()
	os.chdir(L1b_DATA_PROCESSED_PATH)
	DataFromMatlab=sio.loadmat(DataToProcessFileName+'.mat')
	#print 
	PDret=DataFromMatlab['PDret'][0]
	CLWg=DataFromMatlab['CLWg']
	WSg=DataFromMatlab['WSg']
	# Display results
	pl.figure()
	pl.plot(PDret,'.' )
	pl.title('PDret')
	pl.figure()
	pl.plot(CLWg,'.' )
	pl.title('CLWg')
	pl.figure()
	pl.plot(WSg,'.' )
	pl.title('WSg')		
	pl.show()
	return


if __name__ == "__main__":
    main()