# -*- coding: utf-8 -*-
"""
Created on Fri Aug 01 15:11:50 2014

@author: xbosch
"""
import os
from os import listdir
from os.path import isfile, join
import csv
##############
mypath=os.getcwd()  # This is from where Python is called in terminal, not where the file is.
onlyfiles = sorted([ f for f in listdir(mypath) if isfile(join(mypath,f)) ])
##############
csv_out = open('test.csv', 'w')  # ADAM: Changed 'wb' (bytes) to 'w' (str)
mywriter = csv.writer(csv_out)
for row in zip(onlyfiles):
    mywriter.writerow(row)
csv_out.close()
##############