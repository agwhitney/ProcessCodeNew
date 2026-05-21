import numpy as np
import json


class ConfigReader:
    def __init__(self, h5file, Verbose=True):
        RadId = ['mw', 'mmw', 'snd']
        
        datasource = 'h5file.root.Information.Server_INFO'
        data = h5file.root.Information.Server_INFO
        if Verbose:
            print("INFO: new instance for the configuration from", datasource)
        ## Reading the Conf file 
        a = [x['General'] for x in data.iterrows()]
        self.ConfigInfoContent = json.loads(a[0])
        numInstruments = len(self.ConfigInfoContent)
        if Verbose:
            print('Instruments found:', numInstruments)
        for Instrument, cfg in self.ConfigInfoContent.items():
            if Verbose:
                print('\n', Instrument, "active is", cfg['active'])
            
            if not cfg['active']:
                continue
            ## Radiometer is active, read the configuration values
            if Instrument == 'radiometer':
                self.RadActivated = {}
                self.RadIntegrationTime = {}
                self.RadSequence = {}
                self.Sequence = {}
                self.RadSequenceLength = {}
                self.StartingPAttern = {}
                
                for RadiometerSet in range(len(RadId)):
                    ##
                    key = RadId[RadiometerSet]
                    ##
                    self.StartingPAttern[key] = {}
                    self.StartingPAttern[key]['ReferenceSequence'] = 0
                    self.StartingPAttern[key]['NOT_ReferenceSequence'] = 0
                    ##
                    self.RadActivated[key] = cfg['characteristics'][key]['active']
                    self.RadIntegrationTime[key] = cfg['characteristics'][key]['integration_time_ms']
                    self.RadSequence[key] = cfg['characteristics'][key]['sequence']
                    self.RadSequenceLength[key] = self.RadSequence[key]['length']
                    self.Sequence[key] = {}
                    if Verbose:
                        print(f"\n--->Channel set {key} is {self.RadActivated[key]} Tint: {self.RadIntegrationTime[key]} ms sequence length {self.RadSequenceLength[key]}")
                    if Verbose:
                        print("---> sequence:",  self.Sequence[key])
                    ## reading the radiometer sequence
                    for x in range(self.RadSequenceLength[key]):
                        slt = 'slot' + str(x)
                        self.Sequence[key][slt] = {}
                        self.Sequence[key][slt]['bitvalues'] = self.RadSequence[key][slt]['value']
                        self.Sequence[key][slt]['value'] = sum(p*q for p,q in zip(self.RadSequence[key][slt]['value'], [16, 8, 4, 2, 1]))
                        self.Sequence[key][slt]['length'] = self.RadSequence[key][slt]['length']
                        self.Sequence[key][slt]['meaning'] = self.RadSequence[key][slt]['meaning']
                        if Verbose:
                            print(self.Sequence[key][slt]['meaning'],)
                        ## REFERENCE SEQUENCE, Dicke Load for the ACT channels
                        if key == 'mmw':
                            if self.Sequence[key][slt]['value'] == 2 and self.StartingPAttern[key]['ReferenceSequence'] == 0:
                                self.StartingPAttern[key]['ReferenceSequence'] = self.Sequence[key][slt]['length'] - 2
                            else:
                                self.StartingPAttern[key]['NOT_ReferenceSequence'] = self.StartingPAttern[key]['NOT_ReferenceSequence'] + self.Sequence[key][slt]['length']
                        ## REFERENCE SEQUENCE, Dicke Load for the MW channels
                        if key == 'mw':
                            if self.Sequence[key][slt]['value'] == 0 and self.StartingPAttern[key]['ReferenceSequence'] == 0:
                                self.StartingPAttern[key]['ReferenceSequence'] = self.Sequence[key][slt]['length'] - 2
                            if Verbose:
                                print(self.Sequence[key][slt]['length'] - 2)
                            else:
                                self.StartingPAttern[key]['NOT_ReferenceSequence'] = self.StartingPAttern[key]['NOT_ReferenceSequence'] + self.Sequence[key][slt]['length']
                                    
                    self.StartingPAttern[key]['Pattern'] = np.append(np.ones(self.StartingPAttern[key]['ReferenceSequence'], 'int'), int(self.StartingPAttern[key]['NOT_ReferenceSequence']+2)).tolist()

            ## Thermistors are active, read the configuration values                                               
            if Instrument == 'thermistors':
                self.TheAddresses = cfg['characteristics']['addresses']
                self.TheIntegrationTime = cfg['characteristics']['polling_interval']

            ## GPS-IMU are active, read the configuration values   
            if Instrument == 'gpsimu':
                self.GPSAFrequency = cfg['characteristics']['update_frequency']
    


# def main():
#     import tables as tb
#     import os
#     import sys
#     configfile='..\..\GeneralPaths.py'
#     sys.path.append(os.path.dirname(os.path.expanduser(configfile)))
#     from GeneralPaths import H5_DATA_BASE_PATH
    
#     print("\n\n###This is a Class, not to be run as a SCRIPT##")
#     #filenameroot='2014_03_05__16_43_54__1of1_nonametest'
#     filenameroot='2014_06_30__16_39_11__1of1_SND_test_LAB'
#     filename=filenameroot+'.h5'
#     print("-->WARNING: %s is provided with the repository for debugin purposes only"%filename)
#     if not os.path.isabs(filename):
#         filenameh5 = os.path.join(H5_DATA_BASE_PATH, filename)
        
#     h5file=tb.open_file(filenameh5, mode="r")
#     print("-----------------------------------------")
#     for group in h5file.walkGroups("/"):
#         print("--", group)
#     print("-----------------------------------------" )  
#     Conf=configread(h5file)
#     h5file.close()
#     print("-+++------------------------------------+++-" )
#     print(Conf.RadIntegrationTime)
#     print("-++--------------------------------------++-"  ) 
#     print(Conf.Sequence)
#     print("-+----------------------------------------+-")
#     print(Conf.StartingPAttern['MMW']['Pattern'])
#     print(Conf.StartingPAttern['MW']['Pattern'])
    
# if __name__ == "__main__":
#     main()