#!/bin/bash


## 
##nohup python / &
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
        params_point+=("${params_point[$item]}")
    done
    

POS="${params[*]}"

else [ "${params[0]}" = 1 ];
    ## taking certain region defined by polygon region.
    echo "running the algorithm with polygon boundation between lattitude(${params[1]} to ${params[2]} and  longitude ${params[3]} to ${params[4]}, username=${params[5]}, file_cid = ${params[6]}, filename=${params[7]}"

# defining array of 7 elements 

POS="$params"

fi

python /usr/src/app/georender/src/main.py "$POS"
