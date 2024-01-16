"""

author@RemaudMarine
Independant script to identify and suppress the corrupted files in the footprint database
if any corrupted files identified, need to relaunch the footprint to generate these files

"""

from netCDF4 import Dataset
import numpy as np
from numpy import *
import os
import shutil

dirnc='/home/surface1/mremaud/COS/FOOTPRINT/'
dir_store='/home/satellites4/mremaud/FOOTPRINT/'

list_stat=os.listdir(dir_store)
#list_stat=['CGO','THD','SPO','HFM','ALT','BRW','WIS','MLO','NWR','KUM','ICE','LEF','SMO']
for ii in range(2):
 for stat in list_stat:
  if not os.path.isdir(dir_store+"/"+stat): continue
  name_rep=dir_store+stat+'/'
  list_year=os.listdir(name_rep)
  for year in list_year:
   name_rep2=name_rep+year+'/'
   if not  os.path.isdir(name_rep2):continue
   list_date=os.listdir(name_rep2)
   for date in list_date:
    name_rep3=name_rep2+date+'/'
    if not  os.path.isdir(name_rep3):continue
    if 'ferret' in name_rep3: continue
    list_file=os.listdir(name_rep3)
    
    if len(list_file) == 0:  os.system('rmdir '+name_rep3); print(name_rep3,'empty')
    for ff in list_file:
     if (ff[-1]!='c'): continue
     name_file=name_rep3+ff
     try:
       # Open the netCDF file and read it.
       nc = Dataset(name_file,'r')
     except IOError:
       print(' failed in process ',name_file)
       os.system('rm -rf '+name_rep3+'*')


