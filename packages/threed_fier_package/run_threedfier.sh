#!/bin/sh

## parameters
## $1 is the function that is to be executed
## $2 is the output file name in the OBJ format
## $3 is the output format in the CityJSON format
## $4 .... in cityGML

python3 main.py -f $1   --OBJ $2 --CityJSON $3 --CityGML $4