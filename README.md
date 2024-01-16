# Footprint

Python scripts used to generate the LMDz footprints 

Features:
 - For surface stations only
 - Standard LMDz grid: 96x95x39
 - Passive atmospheric tracers (e.g., CO2) with no chemical reactions in the atmosphere
 - Interface CIF (Berchet et al., 2020)

Steps to follow:
 - Create a txt file describing the station coordinates with create-stationlev_FOOTPRINT.py
 - Create the monthly (climatological) and weekly monitor files (txt files) that are necessary to run the CIF with make_monitor_fp_weekly_1stat.py and make_monitor_fp_weekly_1stat.py
 - Install LMDz with the CIF and choose the footprint mode 
 - Run the CIF with the bash scripts: launch_adjoin.sh and launch_adjoinref.sh

ListDamagedFiles.py: script to detect the netcdf files containing damaged footprints
   
