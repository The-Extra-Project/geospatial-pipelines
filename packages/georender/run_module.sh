#!/bin/bash


## 
# reading the parameters from the file 

params=()
for user in "$@"; do
    params+=("$user")
done 

if [ "${params[0]}" = 0 ];
then
# a point based description of the data.
    params_point=()
    echo "run the script with X=${params[0]} Y=${params[1]} username=${params[2]}, file_cid = ${params[3]}, filenameparams[4]}"

    for item in {1..5}; 
        do
            params_point+=("${params[$item]}")
        done

    POS="${params_point[*]}"
    

else [ "${params[0]}" = 1 ];
    ## taking certain region defined by polygon region.
    echo "running the algorithm with polygon boundation between lattitude(${params[1]} to ${params[2]} and  longitude ${params[3]} to ${params[4]}, username=${params[5]}, file_cid = ${params[6]}, filename=${params[7]}"

    # defining array of 7 elements 

    for item in {1..7}; 
        do
            params_point+=("${params[$item]}")
        done

    POS="${params_point[*]}"

fi

python /usr/src/app/georender/src/georender.py "$POS"
