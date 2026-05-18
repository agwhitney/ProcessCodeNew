# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 16:22:15 2014

@author: xbosch
"""
from Reader.Core.PL1a import P_L1a


def process(channelset: str, trec_filename: str, seconds_to_analyze: int = 300, batch_filename: str = 'all'):
    #######################
    ## Flags for display 
    ##
    PlotAngularImage = True
    PlotTipingCurve = True
    DisplayAuxData = True
    ExtendedData = True
    FlagsL1a = {
        "ExtendedData": ExtendedData,
        "PlotAngularImage": PlotAngularImage,
        "PlotTipingCurve": PlotTipingCurve,
        "DisplayAuxData": DisplayAuxData
    }
    #######################

    ##############################################################################
    ##############################################################################
    ChannelSetToAnalyzeVector = [channelset]  # ['MW','SND','MMW']
    CalibrationFilesNames = {channelset: trec_filename}
    # Radiometer data set to be used. TODO: We could use all of them with a loop.  
    TotalSecondsToAnalyzeVector = [seconds_to_analyze]  # Time for calibration and data processing files, respectevily. 
    AngularAverageDegrees = 1  # Mimimum resolution 0.0225, one motor sample per sample.
    sixtyHertzFilter = [True] # The 60 Hz filter for the calibration and the data files, respectevil. Only has effect for the SND channels. -- **Recomendation: Do not change it** .
    #######################
    ##############################################################################
    ##############################################################################

    test = batch_filename
    ##############################################################################
    CVSAnalyzeVector=[test]

    for CVSfilenamebatch in CVSAnalyzeVector:
        L1a = P_L1a(
            CVSfilenamebatch,
            TotalSecondsToAnalyzeVector,
            AngularAverageDegrees,
            CalibrationFilesNames,
            ChannelSetToAnalyzeVector,
            sixtyHertzFilter,
            FlagsL1a
        )
        L1a.run()
    print('FINISHED!')


if __name__ == '__main__':
    process(
        channelset = 'mw',
        trec_filename = '',
        seconds_to_analyze = 300,
        batch_filename = 'all',
    )