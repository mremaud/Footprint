#!/bin/ksh

"""
 Author : Marine Remaud
 Script unix de calcul des footprints hebdomadaires pour des stations de surface en deux étapes:
 1) Lancement de LMDz avec la CIF 
 2) Postprocessing des fichiers de sorties de LMDz (reshape_adjoint.py)

 Ces footprints serviront ensuite à calculer les fonctions de reponse.

 SETTINGS: 
 stationa    = station de surface
 yeara, mona,daya: date de l'ajoint, fenetre de 8 jour a partir de cette date 
 dirmonit    = repertoire dans lequel le détail des stations est prescrit
               Les coordonnees des stations sont prescrites dans le fichier stationlev
 diroutput   = repertoire ou sont stockees les  sorties de LMDz ou CIF
 npropag     = nombre  de mois de retro propagation
 dirpostproc = repertoire ou sont stockees les footprints hebdomadaires

"""

export diroutput=/home/satellites16/mremaud/ADJOINTS/
export dirpostproc=/home/satellites4/mremaud/FOOTPRINT
export dirmonit="/home/users/mremaud/PYTHON/COS/MONITOR/Monitor/"
export dirpyvar='/home/users/mremaud/CIF/examples/FOOTPRINT'
export npropag=8


for stationa in WIS NWR_afternoon MLO_afternoon     ALT BRW PSA   CGO  SUM  MHD BRW  HFM  SPO KUM LEF THD SMO 
 oombre  d annee de retro propagation
 #$(ls /${dirmonit}/)
do
 for yya in 2020 # {2014..2020} # {2010..2015} 
 do
  for mona in {1..12}
  do
   ALL_RESULTS=$(python /home/users/mremaud/CIF/FOOTPRINT/utils.py ${yya} ${mona} ${npropag})
   datei=${ALL_RESULTS:0:10}
   datef=${ALL_RESULTS:11:22}
   echo ${ALL_RESULTS}
   typeset -Z2 mona=$mona
   echo ${datei} ${datef}
   for daya in  01 09 17 25
   do 
     echo  ${dirmonit}${stationa}/monitor_${stationa}_${yya}_${mona}_${daya}.nc
     if [[ -f ${dirmonit}${stationa}/monitor_${stationa}_${yya}_${mona}_${daya}.nc ]]
     then 
        cp ${dirpyvar}/config_adjoint.yml ${dirpyvar}/config_${stationa}_${yya}${mona}${daya}.yml
        export DIRSTOK=$diroutput/${stationa}_${yya}${mona}${daya}
        print ${DIRSTOK}
        sed -i "s/stationa/${stationa}/g"            ${dirpyvar}/config_${stationa}_${yya}${mona}${daya}.yml
        sed -i "s/daya/${daya}/g"                    ${dirpyvar}/config_${stationa}_${yya}${mona}${daya}.yml
        sed -i "s/mona/${mona}/g"                    ${dirpyvar}/config_${stationa}_${yya}${mona}${daya}.yml
        sed -i "s/yeara/${yya}/g"                    ${dirpyvar}/config_${stationa}_${yya}${mona}${daya}.yml
        sed -i "s#output#${DIRSTOK}#g"               ${dirpyvar}/config_${stationa}_${yya}${mona}${daya}.yml
        sed -i "s/dateii/${datei}/g"                 ${dirpyvar}/config_${stationa}_${yya}${mona}${daya}.yml
        sed -i "s/dateff/${datef}/g"                 ${dirpyvar}/config_${stationa}_${yya}${mona}${daya}.yml

cat<<EOF > ${stationa}_${yya}${mona}${daya}
#QSUB -s /bin/tcsh
#PBS -q long
#PBS -l nodes=1:ppn=4
#Retropanache a la station ${stationa} pour la semaine ${yya}${mona}${daya}
module load python/3.6
rm -rf ${diroutput}${stationa}_${yya}${mona}${daya}/*
cd ${dirpyvar}/../../
python -m pycif ${dirpyvar}/config_${stationa}_${yya}${mona}${daya}.yml
python ${dirpyvar}/../../FOOTPRINT/reshape_adjoint.py ${diroutput} ${dirpostproc} ${stationa} ${yya} ${mona} ${daya} ${npropag} 0
EOF

export postproc=${dirpostproc}/${stationa}/${yya}/${stationa}_${yya}${mona}${daya}
if [[ ! -d ${postproc} ]]
then
  echo ${postproc}
qsub  ${stationa}_${yya}${mona}${daya}
fi
  fi
  done
 done
done
done
