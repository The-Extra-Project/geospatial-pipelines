#!/bin/bash

# reading the parameters from the file 

params = ()
i = 0
for user in "$@"; do
    params+="$user"
done 

if [$params[0] = 0]
# a point based description of the data.
    echo "run the script with X=$params[1] Y=$params[2] username=$params[3], file_cid = $params[4], filename=$params[5]"
    POS="$params[0] $params[1] $params[2] $params[3] $params[4] $params[5]"

elif [$params[1] = 1]
    ## taking certain region defined by polygon region.
    echo "running the algorithm with polygon boundation between lattitude($params[1] to $params[2]) and  longitude ($params[3] to $params[4] ) username=$params[5], file_cid = $params[6], filename=$params[7])"
    POS="$params[0] $params[1] $params[2] $params[3] $params[4] $params[5] $params[6] $params[7] "


python /usr/src/app/georender/src/main.py $POS
