#!/usr/bin/env python
import  xarray as xr
import numpy as np
import pandas as pd
from pandas import *
from numpy import *
import os
import copy
from dateutil.relativedelta import relativedelta
import datetime
import time
from useful import *

dir_footprint="/home/satellites4/mremaud/FOOTPRINT/"
list_stat=os.listdir(dir_footprint)
var_name='CO2'

def change_date(yeara,mona,npropa):
   datei=datetime.datetime(int(yeara),int(mona),1)-relativedelta(months=int(npropa))
   datef=datetime.datetime(int(yeara),int(mona),1)+relativedelta(months=1)
   return datei


#for stat in ["ALT","BRW","MLO_afternoon","WIS","NWR_afternoon","KUM","MHD","SUM","CGO","SPO","PSA","LEF","GIF","HFM"]:
for stat in list_stat:
# if stat=="ALT": continue
# if stat=="LEF": continue
 nomstata=copy.copy(stat) 
 for yy in range(2001,2020):
  #Flux equal to 1GtC
 # Flx=np.ones((96,96))/(10**(12)*86400.*Atot)
  yya=copy.copy(yy)
  if not os.path.exists(dir_footprint+"/"+stat+"/"+str(yya)): continue
  list_date=os.listdir(dir_footprint+"/"+stat+"/"+str(yya)+"/")
  for dd in list_date:
   if not os.path.isdir(dir_footprint+"/"+stat+"/"+str(yya)+"/"+dd): continue
   if dd[-3:]=="bis": continue
   mma=dd[len(stat)+1+4:len(stat)+1+6]
   mma=int(mma)
   if len(dd)==len(stat)+1+6: 
    ref=1
    npropag=24
    monitor="/home/users/mremaud/PYTHON/COS/MONITOR/Monitor/"+nomstata+"/monitor_"+nomstata+"_"+str(yya)+"_"+'%02d' %(mma)+"-ref.txt"
   else:
    ref=0
    npropag=9
    dda=copy.copy(int(dd[-2:]))
    monitor="/home/users/mremaud/PYTHON/COS/MONITOR/Monitor/"+nomstata+"/monitor_"+nomstata+"_"+str(yya)+"_"+'%02d' %(mma)+"_"+'%02d' %(dda)+".txt"
   monitor=pd.read_csv(monitor)
   list_file=os.listdir(dir_footprint+"/"+stat+"/"+str(yya)+"/"+dd)
   dir_file=dir_footprint+"/"+stat+"/"+str(yya)+"/"+dd+"/"
   #Test####################################################################"
   #test_array=xr.open_dataset(dir_file+"ad_"+str(yy)+"-"+'%02d' %(mma)+".nc",decode_times=False)
   #prod=np.multiply(test_array[stat].values,Flx[np.newaxis,:,:])
   #prod=np.sum(prod)
###########################################################################
   for ff in list_file:
    if ff[-2:]!="nc": continue
    creation_time=os.path.getmtime(dir_file+ff)
    creation_time=datetime.datetime.fromtimestamp(creation_time)
    if (creation_time)<datetime.datetime(2020,8,2): 
      print(dir_file+ff)
#      print(time.ctime(os.path.getctime(dir_file+ff)),datetime.datetime(2020,8,2))
      divide_number=copy.copy(len(monitor))
#    else:
#      divide_number=1.
#    print(dir_file+ff,len(monitor))
      data_array=xr.open_dataset(dir_file+ff,decode_times=False)
      data_array[stat.upper()].values/=divide_number
      data_array[stat.upper()].attrs["units"]='ppm/kg/m2/s'
      data_array['time'].attrs["calendar"]='gregorian'
      data_array['time'].attrs["units"]='days since '+str(yy)+'-'+'%02d' %(mma)+'-01 00:00:00'
      os.system("rm -f "+dir_file+ff)
      data_array.to_netcdf(dir_file+ff)

