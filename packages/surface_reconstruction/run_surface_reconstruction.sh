#!/bin/bash
# $1 is the CID of the las file that is to be passed as the parameter 
# $2 is the name of the file that is stored


w3 get ${1} -o /usr/app/cgal/input_processing.las


if ["${2}" = "0" ]; then
    output_file="out_poisson.ply"

elif ["${2}" = "1"]; then
    output_file="out_advancing.off"

## now storing the resulting file on the ipfs network
/bin/app/cgal/build/normal_and_reconstruction  /usr/app/reconstruction/input_processing.las ${1} && w3 put $output_file 

