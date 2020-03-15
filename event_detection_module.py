# Module gathering the routines that will used 
# in SISMOC BBOX, and in SEISDataViewer

def kurtosis_eventwindow_function(data, ws = 20, thrON = 5.0, thrOFF = 3.0):

# function computing kurtosis of the data channel
# data =[times values], with times in seconds
# ws is the window size in seconds
# thrON and thrOFF are the trigger values for kurtosis
# on output kurtosis=[times kurtosis]
# on output events=[event_start_time event_end_time SNR=max_kurtosis/3.0]

  from getopt import getopt
  from scipy import signal
  from scipy import stats
  import numpy
  
  from matplotlib import mlab
  from operator import sub
  import os
  from math import log, ceil
  
  import obspy.signal.trigger as trigger


# start function computations
  kurtosis = numpy.zeros(data.shape)
  waves = data[:,1]    
  times = data[:,0]
  dt = times[2] - times[1]
  dt = float(dt)
  fs = 1 / dt

#  print("Calculating kurtosis...")
  kurt = 0.0 * times
  nws = ws / dt
  nt = len(times)
  nws = int(nws)
  nws2 = nws // 2
#  n1 = nws2
#  n2 = nt - nws // 2
  n1 = 0
  n2 = nt-nws
#  n1 = nws
#  n2 = nt
  for n in range(n1,n2) :
#      wtemp=waves[n-nws2:n+nws2+1]
      wtemp=waves[n:n+nws+1]
      kurt[n+nws] = stats.kurtosis(wtemp, axis=0, fisher=False, bias=False)

  eventlist=trigger.trigger_onset(kurt, thrON, thrOFF, max_len=9e+99, max_len_delete=False)
  nev=len(eventlist)
  if nev > 0:
     eventtimes=(eventlist)*dt + times[0]
     events=numpy.zeros((nev,3))
     events[:,0:2:1]=eventtimes[:,0:2:1]

     for n in range(0,nev) :
        n1=eventlist[n,0]
        n2=eventlist[n,1]
        events[n,2] = numpy.amax(kurt[n1:n2+1:1]) / 3.0
  else:
     events=numpy.zeros((nev,3))

  kurtosis[:,0]=times
  kurtosis[:,1]=kurt

  return kurtosis, events ;

def stalta_eventwindow_function(data, f1 = 0, f2 = 0,  wsta = 10, wlta = 60, thrON = 3.0, thrOFF = 2.0):

# function computing STA/LTA of the data channel
# data =[times values], with times in seconds
# f1, f2 corner frequencies of the bandpass signal
# if f2 = 0 assume a high pass
# if f1 = 0 assume a low pass
# wsta is the STA window size in seconds
# wlta is the LTA window size in seconds
# thrON and thrOFF are the trigger values for STA/LTA
# on output stalta=[times stalta]
# on output events=[event_start_time event_end_time SNR=max_stalta/1.0]

  from getopt import getopt
  from scipy import signal
  from numpy import loadtxt, savetxt
  import numpy
  import scipy


  import matplotlib.pyplot as plt
  import sys

  import obspy.signal.filter as obspy_filter

  from obspy.signal import trigger
  #from obspy.signal import filter

# start function computations
  stalta = numpy.zeros(data.shape)
  wavesor = data[:,1]    
  times = data[:,0]
  dt = times[2] - times[1]
  dt = float(dt)
  fs = 1 / dt
  nsta= int( wsta / dt )
  nlta= int( wlta / dt )

  waves = numpy.zeros(wavesor.shape)
  waves[:]=wavesor[:]
# filtering
  if (f1 > 0)  & (f2 > 0):
     waves = obspy_filter.bandpass(wavesor, f1, f2, fs, corners=4, zerophase=True)
  elif (f1 > 0) & (f2 <= 0):
     waves = obspy_filter.highpass(wavesor, f1, fs, corners=4, zerophase=True)
  elif (f1 <= 0) & (f2 > 0):
     waves = obspy_filter.lowpass(wavesor, f2, fs, corners=4, zerophase=True)

#  print("Calculating STA/LTA...")
  stalta_comp = trigger.classic_sta_lta(waves, nsta, nlta)
  eventlist = trigger.trigger_onset(stalta_comp, thrON, thrOFF, max_len=9e+99, max_len_delete=False)
  nev=len(eventlist)
  if nev > 0:
     eventtimes=(eventlist)*dt + times[0]
     events=numpy.zeros((nev,3))
     events[:,0:2:1]=eventtimes[:,0:2:1]

     for n in range(0,nev) :
        n1=eventlist[n,0]
        n2=eventlist[n,1]
        events[n,2] = numpy.amax(stalta_comp[n1:n2+1:1]) / 1.0

  else:
     events=numpy.zeros((nev,3))


  stalta[:,0]=times
  stalta[:,1]=stalta_comp

  return stalta, events ;



def stalta_esta_eventwindow_function(data,  wsta = 1, wlta = 40, thrON = 3.9, thrOFF = 1.0):

# function computing STA/LTA of the data channel
# data =[times values], with times in seconds
# f1, f2 corner frequencies of the bandpass signal
# wsta is the STA window size in seconds
# wlta is the LTA window size in seconds
# thrON and thrOFF are the trigger values for STA/LTA
# on output stalta=[times stalta]
# on output events=[event_start_time event_end_time SNR=max_stalta/1.0]

  from getopt import getopt
  from scipy import signal
  from numpy import loadtxt, savetxt
  import numpy
  import scipy

  import matplotlib.pyplot as plt
  import sys

  from obspy.signal import trigger

# start function computations
  stalta = numpy.zeros(data.shape)
  wavesor = data[:,1]    
  times = data[:,0]
  dt = times[2] - times[1]
  dt = float(dt)
  fs = 1 / dt
  nsta= int( wsta / dt )
  nlta= int( wlta / dt )
  lenesta=len(data)

  stalta_comp = numpy.zeros(len(wavesor))

#  print("Calculating STA/LTA...")
  for i in range(nlta,lenesta) :
      lta_val = numpy.mean(wavesor[i-nlta:i])
      sta_val = numpy.mean(wavesor[i-nsta:i]) 
      stalta_comp[i] = sta_val / lta_val

  eventlist=trigger.trigger_onset(stalta_comp, thrON, thrOFF, max_len=9e+99, max_len_delete=False)
  nev=len(eventlist)
  if nev > 0:
     eventtimes=(eventlist)*dt + times[0]
     events=numpy.zeros((nev,3))
     events[:,0:2:1]=eventtimes[:,0:2:1]

     for n in range(0,nev) :
        n1=eventlist[n,0]
        n2=eventlist[n,1]
        events[n,2] = numpy.amax(stalta_comp[n1:n2+1:1]) / 1.0

  else:
     events=numpy.zeros((nev,3))


  stalta[:,0]=times
  stalta[:,1]=stalta_comp

  return stalta, events ;


def SK_eventwindow_function(data, f1 = 0, f2 = 0,  wsta = 10, wlta = 60, thrSON = 3.0, thrSOFF = 2.0, ws = 20, thrKON = 5.0, thrKOFF = 3.0) :

# function computing STA/LTA and kurtosis of the data channel
# and related event windows
# output stalta, events_stalta
# output kurtosis, events_kurtosis

  import event_detection_module as edm

  [stalta,events_stalta]=edm.stalta_eventwindow_function(data,f1,f2,wsta,wlta,thrSON,thrSOFF)
  [kurtosis,events_kurtosis]=edm.kurtosis_eventwindow_function(data,ws,thrKON,thrKOFF)

  return stalta,events_stalta,kurtosis,events_kurtosis;

def SKmix_eventwindow_function(data, f1 = 0, f2 = 0,  wsta = 10, wlta = 100, thrSON = 3.0, thrSOFF = 1.0, ws = 20, thrKON = 4.0, thrKOFF = 3.0) :

# function computing STA/LTA and kurtosis of the data channel
# and related event windows
# output stalta, kurtosis
# output events_mix
# ws = wlta is preferred

  import numpy
  import scipy

  from obspy.signal import trigger
  import event_detection_module as edm

  [stalta,events_stalta]=edm.stalta_eventwindow_function(data,f1,f2,wsta,wlta,thrSON,thrSOFF)
  [kurtosis,events_kurtosis]=edm.kurtosis_eventwindow_function(data,ws,thrKON,thrKOFF)


  Snev=len(events_stalta)
  Knev=len(events_kurtosis)
  print("number of STA/LTA events :")
  print(Snev)
  print("number of kurtosis events :")
  print(Knev)
#  print(events_kurtosis)

  ndat=len(stalta)
  S=numpy.zeros(ndat)
  K=numpy.zeros(ndat)
  SKadd=numpy.zeros(ndat)
  SKmul=numpy.zeros(ndat)
  times=numpy.zeros(ndat)
  times=stalta[:,0]
  dt = times[2] - times[1]
  dt = float(dt)


# construct 0/1 tables for event detections
  for n in range(0,ndat):
      for i in range(0,Snev):
          if (times[n] >= events_stalta[i,0]) & (times[n] <= events_stalta[i,1]):
             S[n]=stalta[n,1]
      for i in range(0,Knev):
          if (times[n] >= events_kurtosis[i,0]) & (times[n] <= events_kurtosis[i,1]):
             K[n]=kurtosis[n,1]

# detect overlapping windows 
  SKadd[:]=(S[:]/1.0+K[:]/3.0)/2.0
  SKmul=S*K

  eventadd=trigger.trigger_onset(SKadd, 0.001, 0.001, max_len=9e+99, max_len_delete=False)
  nevadd=len(eventadd)
  eventmul=trigger.trigger_onset(SKmul, 0.001, 0.001, max_len=9e+99, max_len_delete=False)
  nevmul=len(eventmul)
  print(nevmul)

  eventmix1=numpy.zeros((nevmul,2))

  nevmix=0
  for i in range(0,nevadd):
      inflag=0
      for k in range(0,nevmul):
          if (eventmul[k,0] >= eventadd[i,0]) & (eventmul[k,0] <= eventadd[i,1]):
             inflag=1
          if (eventmul[k,1] >= eventadd[i,0]) & (eventmul[k,1] <= eventadd[i,1]):
             inflag=1
      if inflag > 0:
         nevmix=nevmix+1
         eventmix1[nevmix-1,:]=eventadd[i,:]

  if nevmix > 0:
     eventtimes=(eventmix1[0:nevmix,0:2:1])*dt + times[0]
     events_mix=numpy.zeros((nevmix,3))
     events_mix[:,0:2:1]=eventtimes[:,0:2:1]

     for n in range(0,nevmix) :
        n1=int(eventmix1[n,0])
        n2=int(eventmix1[n,1])
        events_mix[n,2] = numpy.amax(SKadd[n1:n2+1:1])

  else:
     events_mix=numpy.zeros((nevmix,3))
   

  return stalta,kurtosis,events_mix;

def SKmix_3axis_eventwindow_function(data1, data2, data3, f1 = 0, f2 = 0,  wsta = 10, wlta = 100, thrSON = 3.0, thrSOFF = 1.0, ws = 20, thrKON = 4.0, thrKOFF = 3.0) :

# function computing STA/LTA and kurtosis of the data channel
# and related event windows
# output stalta[i], kurtosis[i]
# output events_mix
# ws = wlta is preferred

  import numpy
  import scipy

  from obspy.signal import trigger
  import event_detection_module as edm

  [out_stalta1,out_kurtosis1,events_mix1]=edm.SKmix_eventwindow_function(data1,f1,f2,wsta,wlta,thrSON,thrSOFF,ws,thrKON,thrKOFF)
  [out_stalta2,out_kurtosis2,events_mix2]=edm.SKmix_eventwindow_function(data2,f1,f2,wsta,wlta,thrSON,thrSOFF,ws,thrKON,thrKOFF)
  [out_stalta3,out_kurtosis3,events_mix3]=edm.SKmix_eventwindow_function(data3,f1,f2,wsta,wlta,thrSON,thrSOFF,ws,thrKON,thrKOFF)

  ndat=len(out_stalta1)
  E1=numpy.zeros(ndat)
  E2=numpy.zeros(ndat)
  E3=numpy.zeros(ndat)
  SKadd=numpy.zeros(ndat)
  SKmul=numpy.zeros(ndat)
  times=numpy.zeros(ndat)
  times=out_stalta1[:,0]
  dt = times[2] - times[1]
  dt = float(dt)

  E1nev=len(events_mix1)
  E2nev=len(events_mix2)
  E3nev=len(events_mix3)

# construct 0/1 tables for event detections
  for n in range(0,ndat):
      for i in range(0,E1nev):
          if (times[n] >= events_mix1[i,0]) & (times[n] <= events_mix1[i,1]):
             E1[n]=events_mix1[i,2]
      for i in range(0,E2nev):
          if (times[n] >= events_mix2[i,0]) & (times[n] <= events_mix2[i,1]):
             E2[n]=events_mix2[i,2]
      for i in range(0,E3nev):
          if (times[n] >= events_mix3[i,0]) & (times[n] <= events_mix3[i,1]):
             E3[n]=events_mix3[i,2]

# detect overlapping windows 
  SKadd[:]=(E1[:]+E2[:]+E3[:])/3.0
  SKmul=(E1*E2)*E3

  eventadd=trigger.trigger_onset(SKadd, 0.001, 0.001, max_len=9e+99, max_len_delete=False)
  nevadd=len(eventadd)
  eventmul=trigger.trigger_onset(SKadd, 0.001, 0.001, max_len=9e+99, max_len_delete=False)
  nevmul=len(eventmul)
 
  if nevadd > 0:
     eventtimes=(eventadd[0:nevadd,0:2:1])*dt + times[0]
     events_mix_3axis=numpy.zeros((nevadd,3))
     events_mix_3axis[:,0:2:1]=eventtimes[:,0:2:1]
     for n in range(0,nevadd) :
        n1=int(eventadd[n,0])
        n2=int(eventadd[n,1])
        events_mix_3axis[n,2] = numpy.amax(SKadd[n1:n2+1:1])

  else:
     events_mix_3axis=numpy.zeros((nevadd,3))

  if nevmul > 0:
     eventtimes=(eventmul[0:nevmul,0:2:1])*dt + times[0]
     events_mul_3axis=numpy.zeros((nevmul,3))
     events_mul_3axis[:,0:2:1]=eventtimes[:,0:2:1]
     for n in range(0,nevmul) :
        n1=int(eventmul[n,0])
        n2=int(eventmul[n,1])
        events_mul_3axis[n,2] = numpy.amax(SKmul[n1:n2+1:1])

  else:
     events_mul_3axis=numpy.zeros((nevmul,3))

  return out_stalta1,out_stalta2,out_stalta3,out_kurtosis1,out_kurtosis2,out_kurtosis3,events_mix_3axis,events_mul_3axis;



def write_timeseries_1channel(timein,data_in,filename):
  import obspy
  from datetime import datetime, date, time, timedelta
  import numpy as np
  from math import log, ceil

# define the file name (to be unique)
  datenow=datetime.utcnow()
  datenow_string=datenow.strftime("%Y-%m-%dT%H_%M_%S.%f")
  filename = filename + str(datenow_string) + '.0.tsf.txt'

# define the header of the obspy 'trace' component
  print(filename)
  timetab = np.int_(timein * 1000.0)
  ndat=len(timetab)
  fobj=open(filename,'w')
  for i in range(0,ndat):
    caracstring= str(timetab[i]) + ' ' + str(data_in[i])
    fobj.write('%s\n' % caracstring )

  return


def write_miniseed_1channel(timein,data_in,filename):
  import obspy
  from datetime import datetime, date, time, timedelta
  import numpy as np

# define the header of the obspy 'trace' component
  print(filename)
  head=obspy.core.trace.Stats()
  head.network=filename[0:2]
  head.station=filename[3:8]
  head.location=filename[9:11]
  head.channel=filename[12:15]
  head.delta=timein[1]-timein[0]
  head.npts=int(len(timein))

# Manage time
# assume time information is in seconds relative to 1970-01-01 
  secstart=np.array(timein[0] // 1,dtype=np.int64)
  datestart=obspy.core.utcdatetime.UTCDateTime(secstart)
  datestartstring=str(datestart)
  datename=datetime.strptime(datestartstring[0:19],'%Y-%m-%dT%H:%M:%S')
  tt=datename.timetuple()
  ydaystring=str(int('%d%03d' % (1, tt.tm_yday)))

  head.starttime=obspy.core.utcdatetime.UTCDateTime(tt.tm_year,tt.tm_mon,tt.tm_mday,tt.tm_hour,tt.tm_min,tt.tm_sec)

  filename = filename + str(tt.tm_year) + '.' + ydaystring[1:4] + '.0.mseed'

# write miniseed file
  datatrace=obspy.core.trace.Trace(data_in,head)
  print(datatrace.stats)
  datatrace.write(filename,format='MSEED')

  return



def write_erp_function(events,channels,rate,ratemin,event_type,bbid,PRODGROUP):
  import obspy
  from datetime import datetime, date, time, timedelta
  import numpy as np

  nev=len(events)
  nchan=len(channels)
  erp_filenames = []
  for i in range(0,nev):
# define ERP filename
    datenow=datetime.utcnow()
    datenow_string=datenow.strftime("%Y-%m-%dT%H:%M:%S.%f")
    datenow_string=datenow_string[0:21:1] + 'Z'
    eventid='ID' + bbid + datenow.strftime("%Y%m%d%H%M%S%f")
# assume event information is in seconds relative to 1970-01-01
    secstart= np.array(events[i,0] // 1,dtype=np.int64) - 5
    datestart=obspy.core.utcdatetime.UTCDateTime(secstart)
#    datestartstring=datetime(str(datestart)).strftime("%Y-%m-%dT%H:%M:%S.%f")
    datestartstring=str(datestart)
    datestartstring=datestartstring[0:21:1] + 'Z'
    print(datestartstring)
#    erp_filenames.append('ERP_SEISMIC_SISMOC_' + str(datestart.year) + '_' + str(datestart.julday) + '_' + str(datename.strftime('%H%M%S')) + '.xml')
    erp_filenames.append('ERP.SISMOC.' + str(datestart.year) + str(datestart.month).zfill(2) + str(datestart.day).zfill(2) + '-' + str(datestart.strftime('%H%M%S')) + '.xml')
    print(erp_filenames[i])
    secend= np.array(events[i,1] // 1,dtype=np.int64) + 10
    dateend=obspy.core.utcdatetime.UTCDateTime(secend)
    dateendstring=str(dateend)
    dateendstring=dateendstring[0:21:1] + 'Z'
#    dateendstring=dateend.strftime("%Y-%m-%dT%H:%M:%S.%f")
# write ERP file
    fobj=open(erp_filenames[i],'w')
    fobj.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    fobj.write('<EVENT_REQUEST_PROPOSAL>\n')
    metadatastring='  <META_DATA productionTime="' + datenow_string + '" eventInternalID="' + eventid + '" producer="SISMOC" schemaName="INS-SI-GRDS-2297-CNES.XSD" schemaVersion="1.6">'
    fobj.write('%s\n' % metadatastring)
    fobj.write('    <FIRST_PRODUCER producerGroup="'+PRODGROUP+'" institution="LMD" userName="A. Spiga" userEmail="aymeric.spiga@lmd.jussieu.fr"/>\n')
    fobj.write('  </META_DATA>\n')
    erp_def_string='  <ERP_DEFINITION requestType="' + event_type + '">'
    fobj.write('%s\n' % erp_def_string)
    for j in range(0,nchan):
      requeststring='    <REQUESTED_CHANNEL sensor="' + str(channels[j]) + '" startTime="' + datestartstring + '" endTime="' + dateendstring +  '" requestedDwnSamplRate="' + str(rate[j]) + '" minDwnSamplRate="' + str(ratemin[j]) + '" />'
      fobj.write('%s\n' % requeststring)

    fobj.write('  </ERP_DEFINITION>\n')
    characstring='  <EVENT_ESTIMATED_CHARACTERIZATION snrVerticalAxis="' + str(events[i,2]) + '" snrHorizontalAxis="1.0" distance="1.0" magnitude="1.0">'
    fobj.write('%s\n' % characstring)
    fobj.write('  </EVENT_ESTIMATED_CHARACTERIZATION>\n')
    fobj.write('</EVENT_REQUEST_PROPOSAL>\n')


  return erp_filenames

def write_erp_function_dd(events,channels,rate,ratemin,event_type,bbid,PRODGROUP):
  import obspy
  from datetime import datetime, date, time, timedelta
  import numpy as np

  nev=len(events)
  nchan=len(channels)
  erp_filenames = []
  for i in range(0,nev):
# define ERP filename
    datenow=datetime.utcnow()
    datestart=events[i,0]
    datenow_string=datenow.strftime("%Y-%m-%dT%H:%M:%S.%f")
    datenow_string=datenow_string[0:21:1] + 'Z'
    eventid='ID' + bbid + datenow.strftime("%Y%m%d%H%M%S%f")
    datestartstring=events[i,0].strftime("%Y-%m-%dT%H:%M:%S.%f")
    datestartstring=datestartstring[0:21:1] + 'Z'
    print(datestartstring)
#    erp_filenames.append('ERP.SISMOC.' + str(datestart.year) + str(datestart.month).zfill(2) + str(datestart.day).zfill(2) + '-' + str(datestart.strftime('%H%M%S')) + '.xml')
    erp_filenames.append('ERP.SEIS_DATA_PORTAL.' + str(datestart.year) + str(datestart.month).zfill(2) + str(datestart.day).zfill(2) + '-' + str(datestart.strftime('%H%M%S')) + '.xml')
    print(erp_filenames[i])
    dateendstring=events[i,1].strftime("%Y-%m-%dT%H:%M:%S.%f")
    dateendstring=dateendstring[0:21:1] + 'Z'

# write ERP file
    fobj=open(erp_filenames[i],'w')
    fobj.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    fobj.write('<EVENT_REQUEST_PROPOSAL>\n')
    metadatastring='  <META_DATA productionTime="' + datenow_string + '" eventInternalID="' + eventid + '" producer="SEIS Data Portal" schemaName="INS-SI-GRDS-2297-CNES.XSD" schemaVersion="1.6">'
    fobj.write('%s\n' % metadatastring)
    fobj.write('    <FIRST_PRODUCER producerGroup="'+PRODGROUP+'" institution="LMD" userName="A. Spiga" userEmail="aymeric.spiga@lmd.jussieu.fr"/>\n')
    fobj.write('  </META_DATA>\n')
    erp_def_string='  <ERP_DEFINITION requestType="' + event_type + '">'
    fobj.write('%s\n' % erp_def_string)
    for j in range(0,nchan):
      requeststring='    <REQUESTED_CHANNEL sensor="' + str(channels[j]) + '" startTime="' + datestartstring + '" endTime="' + dateendstring +  '" requestedDwnSamplRate="' + str(rate[j]) + '" minDwnSamplRate="' + str(ratemin[j]) + '" />'
      fobj.write('%s\n' % requeststring)

    fobj.write('  </ERP_DEFINITION>\n')
    characstring='  <EVENT_ESTIMATED_CHARACTERIZATION snrVerticalAxis="' + '10' + '" snrHorizontalAxis="1.0" distance="1.0" magnitude="1.0">'
    fobj.write('%s\n' % characstring)
    fobj.write('  </EVENT_ESTIMATED_CHARACTERIZATION>\n')
    fobj.write('</EVENT_REQUEST_PROPOSAL>\n')


  return erp_filenames


