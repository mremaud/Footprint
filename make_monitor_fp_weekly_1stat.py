"""

Marine Remaud
Creation de fichiers monitor pour les footprints hebdomadaires

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

###############PARAMETERS TO CHANGE
begy=2014
endy=2020

# grid
homedir='/home/users/mremaud/PYTHON/COS/MONITOR/'

# Text file with the coordinates of the stations
ficgr='/home/isomet/bousquet/FOOTPRINT/PYVAR/grid_LMDZ96_96.txt'

# niveaux verticaux
ficniv='/home/surface1/mremaud/COS/SURFACE/stations_CO2_footprint.txt'

# period for obs averaging - 12:00-17:00
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
  list_alt.append(float(s[4])-1)  #Altitude
##################

debdays=[1,9,17,25] # period of 8 days as for fluxes in PYVARLMDZ
# loop over stations
for stat in   ["WIS"]: #"HFM","CGO","SMO","PSA","KUM","SPO","SUM","ALT","BRW","WIS","MHD","THD","GIF","LEF"]:
  stat2="NWR" if (stat == "NWR_afternoon") else stat
  stat2="MLO" if stat == "MLO_afternoon" else stat
 # if (stat2=="NWR_afternoon")|(stat2=="MLO_afternoon"): continue
  # get coordinates and attribute grid cell
  lon=list_lon[list_stat.index(stat2)]
  lat=list_lat[list_stat.index(stat2)]
  niv=list_niv[list_stat.index(stat2)]
  alt=list_alt[list_stat.index(stat2)]
  print(alt)
  if (alt >= 1000)&(stat!="NWR_afternoon")&(stat!="MLO_afternoon") : 
    hmin=0 ; hmax=4 
  else:
    print(stat2)
    hmin=12 ;hmax=17

  if lon>180.: lon=-360.+lon # lon between -180 and 180 in PYVAR
 # altmolec = str(nummolec + niv / 100.)
  # create directory for monitors if it does not exist:
 #print 'aaa', os.path.isdir('Monitor/'+stat)
  if os.path.isdir(homedir+'Monitor/'+stat) == False:
     os.mkdir(homedir+'Monitor/'+stat)
  # loop over months and days
  # = for each month,each period of about 8 days, hourly value between 12:00 and 17:00
  for year in range(begy,endy+1):
    #Verify that the stations has observations during the year
    if os.path.exists('/home/surface1/mremaud/CO2/SURFACE/STATION/'+stat2+'.pkl'):
       obs=pd.read_pickle('/home/surface1/mremaud/CO2/SURFACE/STATION/'+stat2+'.pkl')
       obs=obs[obs['date'].dt.year==year]
    else:
       obs=pd.DataFrame()
    #import cos observations (not exactly the same location)
    if os.path.exists('/home/surface1/mremaud/COS/SURFACE/STATION/'+stat+'.pkl'):
       #print 'OCS stat:',stat
       cos_o=pd.read_pickle('/home/surface1/mremaud/COS/SURFACE/STATION/'+stat+'.pkl')
       cos_o=cos_o[cos_o['date'].dt.year==year]
    else:
       cos_o=pd.DataFrame()
    #if (stat[:3] == "POC") | (stat[:3]=="DRP"):
    # #Moyenner sur des bins de 5 degre
    # LON=numpy.arange(-180,180,20)
    # LAT=numpy.arange(-90,90,5)
    # obs.loc[obs["stat"]=="POC","lon"]=obs.loc[obs["stat"]=="POC"].apply(lambda row: LON[numpy.abs(LON-row['lon']).argmin()], axis=1)
    # obs.loc[obs["stat"]=="POC","lat"]=obs.loc[obs["stat"]=="POC"].apply(lambda row: LAT[numpy.abs(LAT-row['lat']).argmin()], axis=1)
    # obs.loc[obs["stat"]=="DRP","lon"]=obs.loc[obs["stat"]=="DRP"].apply(lambda row: LON[numpy.abs(LON-row['lon']).argmin()], axis=1)
    # obs.loc[obs["stat"]=="DRP","lat"]=obs.loc[obs["stat"]=="DRP"].apply(lambda row: LAT[numpy.abs(LAT-row['lat']).argmin()], axis=1)
    # for ii in range(len(LON)):
    #  for jj in range(len(LAT)):
    #   namestat= (LON[ii]<0) and "POC"+str(abs(LON[ii]))+"W" or "POC"+str(abs(LON[ii]))+"E"
    #   namestat= (LAT[jj]<0) and namestat+str(abs(LAT[jj]))+"S" or namestat+str(abs(LAT[jj]))+"N"
    #   masque=(obs["lon"]==LON[ii]) & (obs["lat"]==LAT[jj]) & (obs["stat"]=="POC")
    #   obs.loc[masque,"stat"]=namestat
    #   namestat= (LON[ii]<0) and "DRP"+str(abs(LON[ii]))+"W" or "DRP"+str(abs(LON[ii]))+"E"
    #   namestat= (LAT[jj]<0) and namestat+str(abs(LAT[jj]))+"S" or "DRP"+str(abs(LAT[jj]))+"N"
    #   masque=(obs["lon"]==LON[ii]) & (obs["lat"]==LAT[jj]) & (obs["stat"]=='DRP')
    #   obs.loc[masque,"stat"]=namestat
    if (obs.empty)&(cos_o.empty) : continue
    #print stat
    hdeb=copy(hmin) # local time
    hfin=copy(hmax)
    hd=int((hdeb-lon/360.*24))%24 # UTC time
    for mm in range(12):
     date=str(year)+"%02i"%(mm+1)
     monthdays=calendar.monthrange(year,mm+1)
     for ip in range(4):
       #if not obs.empty:
       # mask=(obs['date'].dt.month == (mm+1)) & (obs['date'].dt.day >= int(debdays[ip]) ) &(obs['date'].dt.day < int(debdays[ip])+8 )
       #if not cos_o.empty:
       # mask_cos=(cos_o['date'].dt.month == (mm+1)) & (cos_o['date'].dt.day >= int(debdays[ip]) ) &(cos_o['date'].dt.day < int(debdays[ip])+8 )
       # if not obs.empty:
       #  if  (obs[mask].empty)&(cos_o[mask_cos].empty) : continue
       #else:           
       #  if  (obs[mask].empty) : continue

       # create one monitor per stations per week
       themonit=homedir+'Monitor/'+stat+'/monitor_'+stat+'_'+str(year)+'_'+"%02i"%(mm+1)+'_'+"%02i"%(debdays[ip])+'.nc'
      # themonit='Monitor/'+stat+'/monitor_'+stat+'_'+str(year)+'_'+str(mm+1)+'_'+"%02i"%(debdays[ip])+'.txt'
       output={'date':[],'station':[],'network':[],'parameter':[],'lon':[],'lat':[],'alt':[],'obs':[],'obserror':[],'duration':[]}
       if ip < 3:
        ndays=8
       else:
        ndays=monthdays[1]-25+1
       for day in range(ndays):
         theday=day+debdays[ip]
         utchour=hd
         for hour in range(hdeb,hfin+1):
           utchour=int((hour-lon/360.*24))%24 # UTC time
           thedate=datetime.datetime(copy(year),copy(mm)+1,copy(theday),copy(utchour),0,0)
           output['obserror'].append(0.3)
           output['date'].append(thedate)
           #print lon, hdeb, hd, utchour
           output['station'].append(stat)
           output['lon'].append(lon)
           output['lat'].append(lat)
           output['alt'].append(alt)
           output['obs'].append(1.)
           output['duration'].append(1.)
           output['network'].append('esrl')
           output['parameter'].append('co2')
       output=pd.DataFrame(output)
       output.sort_values("date", inplace = True) 
       output.set_index("date",inplace=True)
       print(output)
       os.system("rm -f "+themonit)
       dump_datastore(output, file_monit=themonit)
       #output.to_csv(themonit,header=True,columns=['date','station','network','parameter','lon','lat','alt','i','j','level','obs','obserror','sim','tstep','dtstep','period'],index=False)  
