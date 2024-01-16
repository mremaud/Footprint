from dateutil.relativedelta import relativedelta
import datetime
import time
from sys import argv
import numpy as np
from netCDF4 import Dataset

def grid_lmdz(resolution):
  #Pour les stations de surface
  month_ref=4
  #Ouverture du fichier netcdf de la hauteur
  if resolution == "144-L79":
    f = Dataset('/home/surface1/mremaud/CO2/LMDZREF/height144-L79-2006.nc', 'r')
  elif resolution == "144-L39":
    f = Dataset('/home/surface1/mremaud/CO2/LMDZREF/height144-L39-2006.nc', 'r')
  else:
    f = Dataset('/home/surface1/mremaud/CO2/LMDZREF/height96-L39-2006.nc', 'r')
  lon=f.variables["lon"][:]
  lat=f.variables["lat"][:]
  hsol=f.variables["phis"][:]/9.81 ;  hsol=hsol[month_ref-1,:,:]
  h=f.variables["geop"][:]/9.81;    h=np.squeeze(h[month_ref-1,:,:,:])
  h=h-hsol
  return lon,lat,hsol,h


def change_date(yeara,mona,npropa):
   datei=datetime.datetime(int(yeara),int(mona),1)-relativedelta(months=int(npropa))
   datef=datetime.datetime(int(yeara),int(mona),1)+relativedelta(months=1)
   print(datei.strftime('%Y-%m-%d'), datef.strftime('%Y-%m-%d'))
   return

change_date(argv[1],argv[2],argv[3])
