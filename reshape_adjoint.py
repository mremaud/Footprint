#!/usr/bin/env python
"""
Author: Marine Remaud
Python script to reshape the LMDz output to a final footprint file

"""

from netCDF4 import Dataset
import numpy as np
import pandas as pd
from numpy import *
import os
import copy
from dateutil.relativedelta import relativedelta
import datetime
import time
import sys
from scipy.io import netcdf
from sys import argv
from useful import *
sys.path.insert(0, '/home/users/mremaud/CIF/')
from pycif.utils.datastores import dump


dirnc=str(argv[2])
dirsimu=str(argv[1])
nomstata=argv[3]
yya=int(argv[4])
mma=int(argv[5])
dda=argv[6]
npropag=int(argv[7])
ref=int(argv[8])

def change_date(yeara,mona,npropa):
   datei=datetime.datetime(int(yeara),int(mona),1)-relativedelta(months=int(npropa))
   datef=datetime.datetime(int(yeara),int(mona),1)+relativedelta(months=1)
   return datei


lon,lat,hsol,h=grid_lmdz('96-L39')
lon=np.asarray(lon.data)
var_name='CO2'
nlon=len(lon)+1
nlat=len(lat)
if not os.path.exists(dirnc):   os.system('mkdir '+dirnc)
if not os.path.exists(dirnc+"/"+nomstata):  os.system('mkdir '+dirnc+"/"+nomstata)
begy=copy.copy(int(yya))-2
endy=copy.copy(int(yya))

if not os.path.exists(dirnc+"/"+nomstata+'/'+str(yya)):
   os.system('mkdir '+dirnc+"/"+nomstata+'/'+str(yya))
datef=change_date(yya,mma,npropag)
if ref: 
 simu="/"+nomstata+'_'+str(yya)+'%02d' %(mma)
else:
 simu="/"+nomstata+'_'+str(yya)+'%02d' %(mma)+dda
ficf=dirsimu+simu+"/obsoperator/adj_0000/"+str(datef.year)+"-"+'%02d' %(datef.month)+"-01_00-00/mod_fluxes_"+var_name+"_out.bin"

monitor=dirsimu+simu+"/obsoperator/tl_0000/monitor.nc"
monitor_data = dump.read_datastore(monitor)
nmonit=len(monitor_data)
if os.path.exists(monitor):
 if os.path.exists(ficf):
  for yy in range(begy,endy+1):
   for mm in range(12):
       fic=dirsimu+simu+"/obsoperator/adj_0000/"+str(yy)+"-"+'%02d' %(mm+1)+"-01_00-00/mod_fluxes_"+var_name+"_out.bin" 
       if not  os.path.exists(fic): continue
       with open(fic, 'rb') as f:
          data = np.fromfile(f, dtype=np.float)
          data = data.reshape((nlon, nlat, -1), order='F')\
                    .transpose((2, 1, 0))
       data=data[:,:,:-1]
       if ref:
        if not os.path.exists(dirnc+"/"+nomstata+'/'+str(yya)+'/'+nomstata+'_'+str(yya)+'%02d' %(mma)+"/"): 
         os.system('mkdir '+dirnc+"/"+nomstata+'/'+str(yya)+'/'+nomstata+'_'+str(yya)+'%02d' %(mma))
        resultfile=netcdf.netcdf_file(dirnc+"/"+nomstata+'/'+str(yya)+'/'+nomstata+'_'+str(yya)+'%02d' %(mma)+'/ad_'+str(yy)+'-'+'%02d' %(mm+1)+'.nc','w')
       else: 
        if not os.path.exists(dirnc+"/"+nomstata+'/'+str(yya)+'/'+nomstata+'_'+str(yya)+'%02d' %(mma)+dda+"/"):
         os.system('mkdir '+dirnc+"/"+nomstata+'/'+str(yya)+'/'+nomstata+'_'+str(yya)+'%02d' %(mma)+dda)
        resultfile=netcdf.netcdf_file(dirnc+"/"+nomstata+'/'+str(yya)+'/'+nomstata+'_'+str(yya)+'%02d' %(mma)+dda+'/ad_'+str(yy)+'-'+'%02d' %(mm+1)+'.nc','w')
       resultfile.createDimension('latitude',nlat)
       resultfile.createDimension('longitude',nlon-1)
       resultfile.createDimension('time',np.shape(data)[0])
       var1=resultfile.createVariable('latitude','d', ('latitude',) )
       var1[:]=lat
       setattr(var1,'units','degrees_north')
       var2=resultfile.createVariable('longitude','d', ('longitude',) )
       var2[:]=lon
       setattr(var2,'units','degrees_east')
       var4=resultfile.createVariable('time','d', ('time',) )
       ztime=[i for i in range(np.shape(data)[0])]
       var4[:]=ztime
       setattr(var4,'units','days since '+str(yy)+'-'+'%02d' %(mm+1)+'-01 00:00:00')
       setattr(var4,'calendar','gregorian')
       var_coord = ('time','latitude','longitude')
       v = resultfile.createVariable( nomstata.upper(), 'd', var_coord )
       v[:]=data[:,:,:]/nmonit
       setattr(v,'long_name','Adjoint output')
       setattr(v,'units','ppm/kg/m2/s)')
  os.system("rm -rdf "+dirsimu+simu) 
 else:
  print(ficf, "missing")
