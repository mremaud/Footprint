
"""

 Marine Remaud
 Script pour creer le fichier stations_CO2_footprint2.txt a definir par les scripts (parametre ficniv dans make_monitor..py) 
 stations_CO2_footprint2.txt contient les coordonnees de chaque station

"""

#!/usr/bin/env python
#Lecture des fichiers texte osc
import string
import pandas as pd
import numpy as np
from netCDF4 import Dataset
import time
import datetime 
import os
from calendar import isleap
import datetime


#Fichier de sortie
DIRSTOK='/home/surface1/mremaud/COS/SURFACE/stations_CO2_footprint2.txt'

def defheight(clon,clat,alt,h,hsol):
        #h: niveaux z modele
        # hsol: niveau sol
        #alt elevation obs
        #4 mois d'avril
        hh=np.squeeze(h[4,:,clat,clon])
        hhsol=np.squeeze(hsol[4,clat,clon])
        altf=max(alt,hhsol)
        altf=(np.abs(hh-altf)).argmin()
        return altf


#Pour trouver les hauteurs###############################################
f = Dataset('/home/surface1/mremaud/CO2/LMDZREF/height96-L39-2006.nc', 'r')
lonlmdz=f.variables["lon"][:]
latlmdz=f.variables["lat"][:]
h=f.variables["geop"][:]/9.81
hsol=f.variables["phis"][:]/9.81
f.close()

obs=pd.read_pickle('/home/surface1/mremaud/CO2/SURFACE/Obs2000.pkl')
for yy in range(2001,2019):
  obs=obs.append(pd.read_pickle('/home/surface1/mremaud/CO2/SURFACE/Obs'+str(yy)+'.pkl'))
#Regrepouper par station,longitude,latitude
obs=obs.groupby(['stat','lon','lat','hauteur']).count()
obs.reset_index(inplace=True)
del obs['month'],obs['meas'],obs['flacon']

#Moyenne des localisations spatiales des stations qui ont bouge dans le temps
obs.loc[obs['stat']=='WLG','hauteur']=obs[obs['stat']=="WLG"]['hauteur'].mean()
obs.loc[obs['stat']=='SPO','hauteur']=obs[obs['stat']=="SPO"]['hauteur'].mean()
obs.loc[obs['stat']=='SPO','lon']    =obs[obs['stat']=="SPO"]['lon'].mean()
obs.loc[obs['stat']=='WIS','hauteur']=obs[obs['stat']=="WIS"]['hauteur'].mean()
obs.loc[obs['stat']=='WIS','lon']    =obs[obs['stat']=="WIS"]['lon'].mean()
obs.loc[obs['stat']=='WIS','lat']    =obs[obs['stat']=="WIS"]['lat'].mean()
obs.loc[obs['stat']=='NAT','hauteur']=obs[obs['stat']=="NAT"]['hauteur'].mean()
obs.loc[obs['stat']=='NAT','lon']    =obs[obs['stat']=="NAT"]['lon'].mean()
obs.loc[obs['stat']=='NAT','lat']    =obs[obs['stat']=="NAT"]['lat'].mean()
obs.loc[obs['stat']=='KZD','hauteur']=obs[obs['stat']=="KZD"]['hauteur'].mean()
obs.loc[obs['stat']=='HPB','hauteur']=obs[obs['stat']=="HPB"]['hauteur'].mean()
obs.loc[obs['stat']=='BAL','hauteur']=obs[obs['stat']=="BAL"]['hauteur'].mean()
obs.loc[obs['stat']=='BAL','lat']    =obs[obs['stat']=="BAL"]['lat'].mean()
obs.loc[obs['stat']=='BAL','lon']    =obs[obs['stat']=="BAL"]['lon'].mean()
obs.loc[obs['stat']=='EST','hauteur']=obs[obs['stat']=="EST"]['hauteur'].mean()
obs.loc[obs['stat']=='CPS','hauteur']=obs[obs['stat']=="CPS"]['hauteur'].mean()
obs.loc[obs['stat']=='POC','hauteur']=obs[obs['stat']=="POC"]['hauteur'].mean()
obs.loc[obs['stat']=='DRP','hauteur']=obs[obs['stat']=="DRP"]['hauteur'].mean()

#Suppression des mesures "bizarre"
a=obs[(obs['stat']=="AMS")&(obs["lat"]!=-37.79830)].index
obs.drop(a,inplace=True)
a=obs[(obs['stat']=="BGU")&(obs["lon"]==0.00)].index
obs.drop(a,inplace=True)
a=obs[(obs['stat']=="TR3")&(obs["lat"]==2.11)].index
obs.drop(a,inplace=True)
a=obs[(obs['stat']=="HLE")&(obs["lat"]==12.01)].index
obs.drop(a,inplace=True)
a=obs[(obs['stat']=="HLE")&(obs["lon"]==32.77)].index
obs.drop(a,inplace=True)
a=obs[obs['stat']=="MHD"][obs["lat"]!=53.326100].index
obs.drop(a,inplace=True)

#Moyenner sur des bins de 5 degre
LON=np.arange(-180,180,20)
LAT=np.arange(-90,90,5)

obs.loc[obs["stat"]=="POC","lon"]=obs.loc[obs["stat"]=="POC"].apply(lambda row: LON[np.abs(LON-row['lon']).argmin()], axis=1)
obs.loc[obs["stat"]=="POC","lat"]=obs.loc[obs["stat"]=="POC"].apply(lambda row: LAT[np.abs(LAT-row['lat']).argmin()], axis=1)
obs.loc[obs["stat"]=="DRP","lon"]=obs.loc[obs["stat"]=="DRP"].apply(lambda row: LON[np.abs(LON-row['lon']).argmin()], axis=1)
obs.loc[obs["stat"]=="DRP","lat"]=obs.loc[obs["stat"]=="DRP"].apply(lambda row: LAT[np.abs(LAT-row['lat']).argmin()], axis=1)

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


obs=obs.groupby(['stat','lon','lat','hauteur']).count()
obs.reset_index(inplace=True)

for stat in obs['stat'].unique():
    tmp=obs[obs['stat']==stat].copy(deep=True)
    if (tmp['lon'].max() - tmp['lon'].min() >1.5): print(stat,tmp['lon'].max(),tmp['lon'].min())
    if (tmp['lat'].max() - tmp['lat'].min() >1 ): print(stat,tmp['lat'].max(),tmp['lat'].min())
    if (tmp['hauteur'].max() - tmp['hauteur'].min()>60 ) : print(stat,tmp)

#Renomer des colonnes
obs.rename(columns={'stat': '#STAT'}, inplace=True)
obs.rename(columns={'lon': 'LON'}, inplace=True)
obs.rename(columns={'lat': 'LAT'}, inplace=True)
obs.rename(columns={'hauteur': 'alt(m)'}, inplace=True)

del obs['tstep']

obs['clon']=obs.apply(lambda row: np.abs(lonlmdz-row['LON']).argmin(), axis=1)
obs['clat']=obs.apply(lambda row: np.abs(latlmdz-row['LAT']).argmin(), axis=1)
obs['lmdzLEV']=obs.apply(lambda row: defheight(row['clon'],row['clat'],row['alt(m)'],h,hsol)+1, axis=1)
obs=obs.groupby(['#STAT','clon','clat','lmdzLEV']).mean()
obs.reset_index(inplace=True)

obs['LON']=obs.apply(lambda row: round(row["LON"],2), axis=1)
obs['LAT']=obs.apply(lambda row: round(row["LAT"],2), axis=1)
obs['alt(m)']=obs.apply(lambda row: round(row["alt(m)"],2), axis=1)



for stat in obs['#STAT'].unique():
    tmp=obs[obs['#STAT']==stat].copy(deep=True)
    if (tmp['clon'].max() - tmp['clon'].min() !=0): print(stat,tmp)
    if (tmp['clat'].max() - tmp['clat'].min() !=0 ): print(stat,tmp)
    if (tmp['lmdzLEV'].max() - tmp['lmdzLEV'].min()!=0 ) : print(stat,tmp)

####Add Japanese measurements   
Japan=pd.read_pickle("/home/surface1/mremaud/COS/SURFACE/Japan.pkl")
Japan.rename(columns={'station': '#STAT'}, inplace=True)
Japan.rename(columns={'lon': 'LON'}, inplace=True)
Japan.rename(columns={'lat': 'LAT'}, inplace=True)
Japan.rename(columns={'alt': 'alt(m)'}, inplace=True)
Japan['#STAT']=Japan.apply(lambda row: row["#STAT"][:3].upper(),axis=1)
Japan['clon']=Japan.apply(lambda row: np.abs(lonlmdz-row['LON']).argmin(), axis=1)
Japan['clat']=Japan.apply(lambda row: np.abs(latlmdz-row['LAT']).argmin(), axis=1)
Japan['lmdzLEV']=Japan.apply(lambda row: defheight(row['clon'],row['clat'],row['alt(m)'],h,hsol)+1, axis=1)
Japan=Japan.groupby(['#STAT','clon','clat','lmdzLEV']).mean()
Japan.reset_index(inplace=True)
Japan['LON']=Japan.apply(lambda row: round(row["LON"],2), axis=1)
Japan['LAT']=Japan.apply(lambda row: round(row["LAT"],2), axis=1)
Japan['alt(m)']=Japan.apply(lambda row: round(row["alt(m)"],2), axis=1)

####Add HIPPO and ATOM #################################################
#Moyenner sur des latitudes de 10 degre
LAT=np.arange(-90,90,10)
LON=np.arange(-180,180,20)

Air=pd.read_pickle("/home/surface1/mremaud/COS/AIRCRAFT/Atoms.pkl").dropna()
Air["lat"]=Air.apply(lambda row: LAT[np.abs(LAT-row['lat']).argmin()], axis=1)
Air["lon"]=Air.apply(lambda row: LON[np.abs(LON-row['lon']).argmin()], axis=1)
Air=Air.groupby(["lat","lon","calt","date"]).mean().reset_index()
Air["#STAT"]="ATOM"
for jj in range(len(LAT)):
 for ii in range(len(LON)):
  for kk in range(39):
    masque=(Air["lat"]==LAT[jj])&(Air["lon"]==LON[ii])&(Air["calt"]==kk)
    if Air[masque].empty: continue
    namestat= "ATOM"+str(LAT[jj])+str(LON[ii])+"-"+str(kk)
    Air.loc[masque,"#STAT"]=namestat
Air["calt"]+=1
Air.rename(columns={'lon': 'LON'}, inplace=True)
Air.rename(columns={'lat': 'LAT'}, inplace=True)
Air.rename(columns={'calt': 'lmdzLEV'}, inplace=True)
Air.rename(columns={'alt': 'alt(m)'}, inplace=True)
Air['alt(m)']=Air.apply(lambda row: round(row["alt(m)"],2), axis=1)
del Air["z_ref"],Air["cos"],Air["co2"]
Air=Air.groupby(['#STAT','clon','clat','lmdzLEV']).mean().reset_index()

Air2=pd.read_pickle("/home/surface1/mremaud/COS/AIRCRAFT/hippo.pkl").dropna()
Air2["lat"]=Air2.apply(lambda row: LAT[np.abs(LAT-row['lat']).argmin()], axis=1)
Air2["lon"]=Air2.apply(lambda row: LON[np.abs(LON-row['lon']).argmin()], axis=1)
Air2=Air2.groupby(["lat","lon","calt","date"]).mean().reset_index()
Air2["#STAT"]="HIPPO"
for jj in range(len(LAT)):
 for ii in range(len(LON)):
  for kk in range(39):
    masque=(Air2["lat"]==LAT[jj])&(Air2["lon"]==LON[ii])&(Air2["calt"]==kk)
    if Air2[masque].empty: continue
    namestat= "HIPPO"+str(LAT[jj])+str(LON[ii])+"-"+str(kk)
    Air2.loc[masque,"#STAT"]=namestat
Air2["calt"]+=1
Air2.rename(columns={'lon': 'LON'}, inplace=True)
Air2.rename(columns={'lat': 'LAT'}, inplace=True)
Air2.rename(columns={'calt': 'lmdzLEV'}, inplace=True)
Air2.rename(columns={'alt': 'alt(m)'}, inplace=True)
Air2['alt(m)']=Air2.apply(lambda row: round(row["alt(m)"],2), axis=1)
del Air2["zref"],Air2["COS"],Air2["CO2"]

Air=Air.groupby(['#STAT','clon','clat','lmdzLEV']).mean().reset_index()
Air2=Air2.groupby(['#STAT','clon','clat','lmdzLEV']).mean().reset_index()



obs=obs.groupby(['#STAT','clon','clat','lmdzLEV']).mean()
obs.reset_index(inplace=True)
obs=obs.append(Japan)
obs=obs.append(Air2)
obs=obs.append(Air)

obs.to_csv(DIRSTOK,header=True,columns=['#STAT','LON','LAT','lmdzLEV','alt(m)'],index=False,sep=" ")





