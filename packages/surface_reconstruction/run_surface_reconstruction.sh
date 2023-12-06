#!/bin/bash
# $1 is the username corresponding to which the function call is being executed
# $2 is the category of the algorithm to be applied for the parameter.
## 0 -> for the poisson surface_reconstruction
## 1 -> advance surface_reconstruction
## 2 ->  for multisolver poisson SR.

if [ "${1}" = "0" ]; then
    output_file="out_poisson.ply"

elif [ "${1}" = "1" ]; then
    output_file="out_advancing.off"

elif [ "${1}" = "2" ]; then 
    true
    ## depth and pointWeight parameter to be defined to be fixed based on the user
    /bin/app/cgal/lib/PoissonRecon/PoissonRecon --in "$output_file" --out "$output_file" --depth 8 --pointWeight 0
    exit 1
fi


## now storing the resulting file on the ipfs network
/bin/app/cgal/build/normal_and_reconstruction  /usr/app/reconstruction/file-cropped-boundation-versailles-2.las ${1} ${3} && w3 put $output_file 