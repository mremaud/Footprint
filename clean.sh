#!/bin/ksh
#Lancer les adjoints pour calculer les fonctions de reponse
#Modifier les coordonnees des stations dans stationlev
#stationa: station de surface echantillonnee
#yeara, mona,daya: date de l'ajoint, fenetre de 8 jour a partir de cette date
# Nombre  d annee de retro propagation

export dirmonit="/home/users/mremaud/PYTHON/COS/MONITOR/Monitor/"
export dirpyvar='/home/users/mremaud/DISPERSIONnp2/examples/FOOTPRINT'
export ypropag=2

for stationa in $(ls /${dirmonit}/)
do
 for yya in 2018
 do
  export endyy=${yya} 
  deby=`expr $yya - $ypropag`
  for mona in {1..12}
  do
   begmm=`expr $mona + 1`
   if [[ mona == 12 ]]; then 
    let endyy = $yya + 1
    export begmm=1
   fi
   typeset -Z2 begmm=$begmm
   typeset -Z2 mona=$mona
   for daya in  01 09 25 17
   do
#     find * -name "*${yya}*${mona}*${daya}*"
     cp ${dirpyvar}/config_adjoint.yml ${dirpyvar}/config_${stationa}_${yya}${mona}${daya}.yml
     export DIRSTOK=${stationa}_${yya}${mona}${daya} 
     print ${DIRSTOK}
rm -rf /home/satellites15/mremaud/${stationa}_${yya}${mona}${daya}/*
if [[ ! -d /home/satellites15/mremaud/ADJOINTS/${stationa}_${yya}${mona}${daya} ]]
then
  qsub -l nodes=1:ppn=10 -q longp   ${stationa}_${yya}${mona}${daya}
fi

  done
 done
done
done
