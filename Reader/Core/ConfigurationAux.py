import numpy as np
import json


class configread:
    
    def __init__(self, h5file, Verbose=True):
       
        RadId=['mw', 'mmw', 'snd']      
        TwoPow=[16,8,4,2,1]
        
        datasource='h5file.root.Information.Server_INFO'
        data =eval(datasource)
        if Verbose==True: print( "INFO: new instance for the configuration from ", datasource    )   
        ## Reading the Conf file 
        a=[x['General'] for x in data.iterrows()]
        #print a[0], type(a[0])
        self.ConfigInfoContent = json.loads(a[0])         
        numInstruments=len(self.ConfigInfoContent)
        if Verbose==True: print( 'Instrumetns found:', numInstruments)
        for Instrument, cfg in self.ConfigInfoContent.items():
            if Verbose==True: print( '\n', Instrument, "is")
            if cfg['active']==True:
                if Verbose==True: print( "active")
                ## Radiometer is active, read the configuration values
                if Instrument == 'radiometer':
                                        
                    self.RadActivated={}
                    self.RadIntegrationTime={}
                    self.RadSequence={}
                    self.Sequence={}
                    self.RadSequenceLength={}
                    self.StartingPAttern={}
                    
                    for RadiometerSet in range(0,len(RadId)):
                        ##
                        id=RadId[RadiometerSet]
                        ##
                        self.StartingPAttern[id]={}
                        self.StartingPAttern[id]['ReferenceSequence']=0
                        self.StartingPAttern[id]['NOT_ReferenceSequence']=0
                        ##
                        self.RadActivated[id]=cfg['characteristics'][id]['active']
                        self.RadIntegrationTime[id]=cfg['characteristics'][id]['integration_time_ms']
                        self.RadSequence[id]=cfg['characteristics'][id]['sequence']
                        self.RadSequenceLength[id]=self.RadSequence[id]['length']
                        self.Sequence[id]={}
                        #print self.RadSequence
                        if Verbose==True: print( '\n--->Channel set', id , 'is', self.RadActivated[id], 'Tint:', self.RadIntegrationTime[id], 'ms sequence length', self.RadSequenceLength[id])
                        if Verbose==True: print( "---> sequence:",  )                          
                        ## reading the radiometer sequence
                        for x in range(0,self.RadSequenceLength[id]):
                            slt='slot'+str(x)
                            self.Sequence[id][slt]={}
                            #print id, slt, '/', self.RadSequenceLength[id], 
                            self.Sequence[id][slt]['bitvalues']=self.RadSequence[id][slt]['value']
                            self.Sequence[id][slt]['value']=sum(p*q for p,q in zip(self.RadSequence[id][slt]['value'], TwoPow))
                            self.Sequence[id][slt]['length']=self.RadSequence[id][slt]['length']
                            self.Sequence[id][slt]['meaning']=self.RadSequence[id][slt]['meaning']
                            if Verbose==True: print( self.Sequence[id][slt]['meaning'],)
                            ## REFERENCE SEQUENCE, Dicke Load for the ACT channels
                            if id=='mmw' and self.Sequence[id][slt]['value']==2 and self.StartingPAttern[id]['ReferenceSequence']==0:
                                self.StartingPAttern[id]['ReferenceSequence']=self.Sequence[id][slt]['length']-2
                            elif id=='mmw':
                                self.StartingPAttern[id]['NOT_ReferenceSequence']=self.StartingPAttern[id]['NOT_ReferenceSequence']+self.Sequence[id][slt]['length']
                            ## REFERENCE SEQUENCE, Dicke Load for the MW channels
                            if id=='mw' and self.Sequence[id][slt]['value']==0 and self.StartingPAttern[id]['ReferenceSequence']==0:
                                self.StartingPAttern[id]['ReferenceSequence']=self.Sequence[id][slt]['length']-2
                                if Verbose==True: print(self.Sequence[id][slt]['length']-2)
                            elif id=='mw':
                                self.StartingPAttern[id]['NOT_ReferenceSequence']=self.StartingPAttern[id]['NOT_ReferenceSequence']+self.Sequence[id][slt]['length']
                            
                                        
                        self.StartingPAttern[id]['Pattern']=np.append(np.ones(self.StartingPAttern[id]['ReferenceSequence'], 'int'), int(self.StartingPAttern[id]['NOT_ReferenceSequence']+2)).tolist()
                        #print self.StartingPAttern[id]['ReferenceSequence'], self.StartingPAttern[id]['NOT_ReferenceSequence']
                        #print self.StartingPAttern[id]['Pattern']

                ## Thermistors are active, read the configuration values                                               
                if Instrument == 'thermistors':
                    self.TheAddresses=cfg['characteristics']['addresses']
                    self.TheIntegrationTime=cfg['characteristics']['polling_interval']

                ## GPS-IMU are active, read the configuration values   
                if Instrument == 'gpsimu':
                    self.GPSAFrequency = cfg['characteristics']['update_frequency']
            
            else:
                if Verbose==True: print("inactive")
    


def main():     
    import tables as tb
    import os
    import sys
    configfile='..\..\GeneralPaths.py'
    sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
    from GeneralPaths import H5_DATA_BASE_PATH
    
    print( "\n\n###This is a Class, not to be run as a SCRIPT##")
    #filenameroot='2014_03_05__16_43_54__1of1_nonametest'
    filenameroot='2014_06_30__16_39_11__1of1_SND_test_LAB'
    filename=filenameroot+'.h5'
    print( "-->WARNING: %s is provided with the repository for debugin purposes only"%filename)
    if not os.path.isabs(filename):
        filenameh5 = os.path.join(H5_DATA_BASE_PATH, filename)
        
    h5file=tb.open_file(filenameh5, mode="r")
    print("-----------------------------------------")
    for group in h5file.walkGroups("/"):
        print( "--", group)
    print( "-----------------------------------------" )  
    Conf=configread(h5file)
    h5file.close()
    print( "-+++------------------------------------+++-" )
    print( Conf.RadIntegrationTime)
    print( "-++--------------------------------------++-"  ) 
    print( Conf.Sequence)
    print( "-+----------------------------------------+-")
    print( Conf.StartingPAttern['MMW']['Pattern'])
    print( Conf.StartingPAttern['MW']['Pattern'])
    
if __name__ == "__main__":
    main()