#!/bin/ksh

"""

 Author : Marine Remaud
 Script unix de calcul des footprints mensuels de reference (annee 2017) pour des stations de surface en deux étapes:
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
 dirpostproc = repertoire ou sont stockees les footprints mensuels (regarder yeara = 2017)

"""

export diroutput=/home/satellites16/mremaud/ADJOINTS/
export dirpostproc=/home/satellites4/mremaud/FOOTPRINT
export dirmonit="/home/users/mremaud/PYTHON/COS/MONITOR/Monitor/"
export dirpyvar='/home/users/mremaud/CIF/examples/FOOTPRINT'
export npropag=24


for stationa in GIF  #$(ls /${dirmonit}/)  #THD NWR #LEF #SPO CGO HFM MHD #KUM SMO  #MLO #$(ls /${dirmonit}/)
do
 for yya in 2017
 do
  for mona in {1..12}
  do
   ALL_RESULTS=$(python /home/users/mremaud/CIF/FOOTPRINT/utils.py ${yya} ${mona} ${npropag})
   datei=${ALL_RESULTS:0:10}
   datef=${ALL_RESULTS:11:22}
   typeset -Z2 mona=$mona
     if [[ -f ${dirmonit}${stationa}/monitor_${stationa}_${yya}_${mona}-ref.nc ]]
     then 
        cp ${dirpyvar}/config_adjointref.yml ${dirpyvar}/config_${stationa}_${yya}${mona}.yml
        export DIRSTOK=$diroutput/${stationa}_${yya}${mona}${daya}
        print ${DIRSTOK}
        sed -i "s/stationa/${stationa}/g"            ${dirpyvar}/config_${stationa}_${yya}${mona}.yml
        sed -i "s/mona/${mona}/g"                    ${dirpyvar}/config_${stationa}_${yya}${mona}.yml
        sed -i "s/yeara/${yya}/g"                    ${dirpyvar}/config_${stationa}_${yya}${mona}.yml
        sed -i "s#output#${DIRSTOK}#g"               ${dirpyvar}/config_${stationa}_${yya}${mona}.yml
        sed -i "s/dateii/${datei}/g"                 ${dirpyvar}/config_${stationa}_${yya}${mona}.yml
        sed -i "s/dateff/${datef}/g"                 ${dirpyvar}/config_${stationa}_${yya}${mona}.yml
cat<<EOF > ${stationa}_${yya}${mona}
#Retropanache a la station ${stationa} pour la semaine ${yya}${mona}
#QSUB -s /bin/tcsh
#PBS -q long
#PBS -l nodes=1:ppn=4
module load python/3.6
rm -rf ${diroutput}${stationa}_${yya}${mona}/*
cd ${dirpyvar}/../../
python -m pycif ${dirpyvar}/config_${stationa}_${yya}${mona}.yml
python ${dirpyvar}/../../FOOTPRINT/reshape_adjoint.py ${diroutput} ${dirpostproc} ${stationa} ${yya} ${mona} 01 ${npropag} 1
EOF

export postproc=${dirpostproc}/${stationa}/${yya}/${stationa}_${yya}${mona}
echo $postproc
if [[ ! -d ${postproc} ]]
then
  qsub   ${stationa}_${yya}${mona}
fi
  fi
  done
 done
done
