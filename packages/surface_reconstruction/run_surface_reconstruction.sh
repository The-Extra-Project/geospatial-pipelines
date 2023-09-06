#!/bin/bash
# $1 is the CID of the las file that is to be passed as the parameter 
# $2 is the name of the file that is stored


w3_installed = $(dpkg-query -W -f='${Status}' w3 2>/dev/null | grep -c "install ok installed")

if [ "$w3_installed" -eq 1 ]; then
    echo "web3_storage is installed"
fi

## downloading the laz file from IPFS network
w3 get ${1} -o './datas/input_surface_reconstruction.las'


if ["$2" = "0" ]; then
    output_file = "out_poisson.ply"

elif ["$2" = "1"]; then
    output_file = "out_advancing.off"

## now executing the file on the ipfs network
/bin/app/cgal/build/normal_and_reconstruction ./datas/input_surface_reconstruction.las  $2 && w3 put $output_file 