#!/bin/bash


## 
# reading the parameters from the file 

params=()
for inputs in "$@"; do
    params+=("$inputs")
done 

if [ "${params[0]}" = 0 ];
then        
    echo   "toto" + ${params[*]}
    python3  ./src/georender.py --option "${params[1]}" --Xcoord ${params[2]} --Ycoord ${params[3]}  --username ${params[4]}  --ipfs_shp_files  ${params[5]} --ipfs_template_files  ${params[6]}  --filename_template  ${params[7]}
    exit 1
else [ "${params[0]}" = 1 ];
    ## taking certain region defined by polygon region.
    echo "running the algorithm with polygon boundation between lattitude(${params[1]} to ${params[2]} and  longitude ${params[3]} to ${params[4]}, username=${params[5]}, file_cid = ${params[6]}, filename=${params[7]}"

    # defining array of 7 elements 
   
    python3  ./src/georender.py  --longitude_range_polygon ${params[1]} --lattitude_range_param ${params[2]} --username ${params[3]}  --ipfs_shp_files  ${params[4]} --ipfs_template_files  ${params[5]}  --filename_template  ${params[6]}
    exit 1

fi



exit 1
