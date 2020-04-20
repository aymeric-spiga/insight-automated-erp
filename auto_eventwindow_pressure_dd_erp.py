#!/usr/bin/env python2.7
'''
Created on 10 oct. 2014

@author: rgarcia
'''

# call line:
# single file data 
# INCLUDE THE CODE OF AYMERIC
# new call line
# python ./auto_eventwindow_pressure_dd_erp.py
# must kill the ISAE proxy (command killprox on r.garcia laptop) to ensure that the data can be obtained online ('"pds" option)

from getopt import getopt
from scipy import signal
from scipy import stats
from numpy import loadtxt, savetxt
import numpy
import math
import numpy as np
import apss_lib

#import matplotlib.pyplot as plt
import sys

#from matplotlib import mlab
from getopt import getopt
from operator import sub
import os
from math import log, ceil
import obspy.signal.detrend as detrend
import event_detection_module as edm
from datetime import datetime, date, time, timedelta
import numpy as np
import obspy

# default parameters
sol1 = 443
sol2 = 443
mindrop=0.3
# inserted to avoid repeat of previous ERPs sent by C. Perrin
maxdrop=100.0
ws=180
param_file="./param_pres_dd.txt"
PRODGROUP="APSS"

# parameters in command line (1rst priority)
if __name__ == '__main__':
    optlist, args = getopt(sys.argv[1:], "", ["outfile=", "signal=", "sol1=", "sol2=", "mindrop=", "maxdrop=", "ws=","paramFile="])
    print("Options : " + str(optlist))
    for opt, arg in optlist:
        if opt == "--signal":
            inputfile = arg
        elif opt == "--outfile":
            outfile = arg
        elif opt == "--sol1":
            sol1 = int(arg)
        elif opt == "--sol2":
            sol2 = int(arg)
        elif opt == "--mindrop":
            mindrop = float(arg)
        elif opt == "--maxdrop":
            maxdrop = float(arg)
        elif opt == "--ws":
            ws = float(arg)
        elif opt == "--paramFile":
            param_file = arg

# parameters from config file name (2nd priority)
# This reading is removed in order to allow to script the command in a bash
#    print(os.path.isfile(param_file))
#    if os.path.isfile(param_file):
#      f=open(param_file,"r")
#      lines = f.readlines()
#      for command in lines:
#         print(command)
#         exec(command)

    print("Call Aymeric routines (former dd_create.py)")
    recalculate = True # recalculate everything included in soltab (could be very long)
    window = 1000 # optimum
    datatype = "pds" # read directly in PDS format
#    datatype = "mws" # read directly in PDS format
    soltab = range(sol1,sol2+1)
    print soltab
    utc,dropamp=apss_lib.analyze_pressure(soltab=soltab,recalculate=recalculate,datatype=datatype,window=window)
#    print utc

    dropamp = np.squeeze(dropamp)
    print dropamp

    ndrop=len(utc)
    print('Number of Drops detected')
    print ndrop
    utcsel=[]
    dropampsel=[]
    utcdt=[]
    utcdt1=[]
    utcdt2=[]
    for i in range(0,ndrop):
      if (np.abs(dropamp[i])>mindrop) & (np.abs(dropamp[i])<maxdrop):
        utcsel.append(utc[i])
        dropampsel.append(dropamp[i])
	_dt = obspy.UTCDateTime(utc[i])
        utcdt.append(obspy.UTCDateTime(utc[i]).datetime)
        _start = _dt-float(ws)
	_end = _dt+float(ws)
	utcdt1.append(_start.datetime)        
	utcdt2.append(_end.datetime)

# test condition on datetime format
#    _end=_end-float('600')
#    if _start<_end:
#      print('proper order')
#      print(_start)
#      print(_end)

#    if np.array(_start)<np.array(_end):
#      print('proper np.array(datetime)')
#      print(np.array(_start))
#      print(np.array(_end))

    
    event1=[utcdt1, utcdt2]
    event1=np.transpose(np.array(event1))
    print('Number of drops selected')
    print(len(event1))
    print('EVENT1')
    print(event1)
    eventmix=event1
    nevmix=0
    for i in range(0,len(utcdt1)):
      inflag=0
      for k in range(i,len(utcdt1)):
          if (event1[k,0] > event1[i,0]) & (event1[k,0] < event1[i,1]):
             inflag=1
             event1[k,0]=event1[i,0]
          if (event1[k,1] > event1[i,0]) & (event1[k,1] < event1[i,1]):
             inflag=1
             event1[k,1]=event1[i,1]
      if inflag == 0:
         nevmix=nevmix+1
         eventmix[nevmix-1,:]=event1[i,:]

    eventsel=eventmix[0:nevmix,:]
    print('Number of Windows for ERPs')
    print(nevmix)
    print(eventsel)

    
# write ERP files
#    channels=['BD0','BKI']
#    locations=['02','02']
    channels=['PRESSURE_1','SP_1_VEL','SP_2_VEL','SP_3_VEL','MAG_1','MAG_2','MAG_3']
    rate=[20, 100, 100, 100, 20, 20, 20]
    ratemin=[20, 100, 100, 100, 20, 20, 20]
    event_type='DUST DEVIL'
    bbid='_BB_PRES_DD_'
    PRODGROUP="APSS"
    erp_filenames=edm.write_erp_function_dd(eventsel,channels,rate,ratemin,event_type,bbid,PRODGROUP)
#    print(erp_filenames)


