"""
Marine Remaud
Creation de fichiers monitor pour les footprints mensuels

"""


from scipy.io import netcdf
import sys
import string
import numpy
import calendar
import os
import pandas as pd
import datetime
from copy import *
sys.path.insert(0, '/home/users/mremaud/CIF/')
import pycif
from pycif.utils.datastores import empty
from pycif.utils.datastores.dump import dump_datastore

###############
#PARAMETERS TO CHANGE
begy=2017  
endy=2017

# details of the LMDz grid
ficgr='/home/isomet/bousquet/FOOTPRINT/PYVAR/grid_LMDZ96_96.txt'
# Coordinates of the stations (to be created beforehand)
ficniv='/home/surface1/mremaud/COS/SURFACE/stations_CO2_footprint.txt'

# period for obs averaging - 12:00-17:00 (in the afternoon most of the time)
hmin=12
hmax=17
####################

fn=open(ficniv,'r')
lniv=fn.readlines()
fn.close()

list_stat=[]
list_lat=[]
list_lon=[]
list_alt=[]
list_typ=[]
list_niv=[]
for l in lniv[1:]:
  s=l.split()
  list_stat.append(s[0])
  list_lat.append(float(s[2])) ### change number of column
  list_lon.append(float(s[1])) ### change number of column
  list_niv.append(float(s[3])) ### change number of column
  list_alt.append(float(s[4]))  #Altitude
##################

# loop over stations
#for stat in list_stat:
for stat in ['GIF']:
  # get coordinates and attribute grid cell
  if (stat == "MLO_afternoon"):
    stat2="MLO"
  elif (stat == "NWR_afternoon"):
    stat2="NWR"
  else:
    stat2=stat

  lon=list_lon[list_stat.index(stat2)]
  lat=list_lat[list_stat.index(stat2)]
  niv=list_niv[list_stat.index(stat2)]
  alt=list_alt[list_stat.index(stat2)]
  if (alt >= 1000)&(stat=="NWR_afternoon") :
   hmin=12 ;hmax=17
  elif (alt >= 1000)&(stat=="MLO_afternoon") :
   hmin=12 ;hmax=17
  elif (alt >= 1000): 
   print("alt")
   hmin=0 ; hmax=4 
  else:
   hmin=12 ;hmax=17
  if lon>180.: lon=-360.+lon # lon between -180 and 180 in PYVAR
 # altmolec = str(nummolec + niv / 100.)
  # create directory for monitors if it does not exist:
 #print 'aaa', os.path.isdir('Monitor/'+stat)
  if os.path.isdir('Monitor/'+stat) == False:
     os.mkdir('Monitor/'+stat)
  # loop over months and days
  # = for each month,each period of about 8 days, hourly value between 12:00 and 17:00
  for year in range(begy,endy+1):
    #Verify that the stations has observations during the year
    obs=pd.read_pickle('/home/surface1/mremaud/CO2/SURFACE/Obs'+str(year)+'.pkl')
    if (stat[:3] == "POC") | (stat[:3]=="DRP"):
     #Moyenner sur des bins de 5 degre
     LON=numpy.arange(-180,180,20)
     LAT=numpy.arange(-90,90,5)
     obs.loc[obs["stat"]=="POC","lon"]=obs.loc[obs["stat"]=="POC"].apply(lambda row: LON[numpy.abs(LON-row['lon']).argmin()], axis=1)
     obs.loc[obs["stat"]=="POC","lat"]=obs.loc[obs["stat"]=="POC"].apply(lambda row: LAT[numpy.abs(LAT-row['lat']).argmin()], axis=1)
     obs.loc[obs["stat"]=="DRP","lon"]=obs.loc[obs["stat"]=="DRP"].apply(lambda row: LON[numpy.abs(LON-row['lon']).argmin()], axis=1)
     obs.loc[obs["stat"]=="DRP","lat"]=obs.loc[obs["stat"]=="DRP"].apply(lambda row: LAT[numpy.abs(LAT-row['lat']).argmin()], axis=1)
     for ii in range(len(LON)):
      for jj in range(len(LAT)):
       namestat= (LON[ii]<0) and "POC"+str(abs(LON[ii]))+"W" or "POC"+str(abs(LON[ii]))+"E"
       namestat= (LAT[jj]<0) and namestat+str(abs(LAT[jj]))+"S" or namestat+str(abs(LAT[jj]))+"N"
       masque=(obs["lon"]==LON[ii]) & (obs["lat"]==LAT[jj]) & (obs["stat"]=="POC")
       obs.loc[masque,"stat"]=namestat
       namestat= (LON[ii]<0) and "DRP"+str(abs(LON[ii]))+"W" or "DRP"+str(abs(LON[ii]))+"E"
       namestat= (LAT[jj]<0) and namestat+str(abs(LAT[jj]))+"S" or "DRP"+str(abs(LAT[jj]))+"N"
       masque=(obs["lon"]==LON[ii]) & (obs["lat"]==LAT[jj]) & (obs["stat"]=='DRP')
       obs.loc[masque,"stat"]=namestat

    hdeb=copy(hmin) # local time
    hfin=copy(hmax)
    hd=int((hdeb-lon/360.*24))%24 # UTC time
    for mm in range(12):
     date=str(year)+"%02i"%(mm+1)
     monthdays=calendar.monthrange(year,mm+1)
     
     # create one monitor per stations per month
     themonit='Monitor/'+stat+'/monitor_'+stat+'_'+str(year)+'_'+"%02i"%(mm+1)+'-ref.nc'
     output={'date':[],'station':[],'network':[],'parameter':[],'lon':[],'lat':[],'alt':[],'obs':[],'obserror':[],'duration':[]}
     ndays=copy(monthdays[1])
     for day in range(ndays):
         theday=day+1
         utchour=hd
         for hour in range(hdeb,hfin+1):
           utchour=int((hour-lon/360.*24))%24 # UTC time
           thedate=datetime.datetime(copy(year),copy(mm)+1,copy(theday),copy(utchour),0,0)
           output['obserror'].append(0.3)
           output['date'].append(thedate)
           output['station'].append(stat)
           output['lon'].append(lon)
           output['lat'].append(lat)
           output['alt'].append(alt)
           output['obs'].append(1)
           output['duration'].append(1.0)
           output['network'].append('esrl')
           output['parameter'].append('co2')
     output=pd.DataFrame(output)
     output.sort_values("date", inplace = True) 
     output.set_index("date",inplace=True)
     os.system("rm -f "+themonit)
     dump_datastore(output, file_monit=themonit)
