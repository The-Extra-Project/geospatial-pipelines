#!/bin/sh

# dockedrhub name of the current version of the deployed pipeline.

georender_pipeline=devextralabs/georender
surface_reconstruction=devextralabs/surface_reconstruction
threeDtiles=devextralabs/vizualization

## parameters:
## point coordinates (X/Y) for the specific job that you want to run.
## IPFS CID of the given shape file that you want to run.
## filename of the template
## username of the person running the job
##  category of reconstruction algorithm you want to implement (0 for advance and 1 for poisson template)
Xcoord="43.2946"
Ycoord="5.3695"
username="test"
ipfs_shp_file="bafkreicxd6u4avrcytevtvehaaimqbsqe5qerohji2nikcbfrh6ccb3lgu"
filename="pipeline_template.json"

#params = 

whereis bacalhau

if [ $? -neq 0 ]
then
    echo "bacalhau is installed"
else
    echo "bacalhau is not installed"
    exit 1
fi

bacalhau docker run  $georender_pipeline -- $Xcoord $Ycoord $username $ipfs_shp_file $filename -i dst="./datas/" || sed  '^\{?[A-F0-9a-f]{8}-[A-F0-9a-f]{4}-[A-F0-9a-f]{4}-[A-F0-9a-f]{4}-[A-F0-9a-f]{12}\}?$' > jobId

if [ $? -eq 0 ]
then
    echo "error running the pipeline"
    exit 1
fi

jid=`cat jobId` # d317dc34-ddee-4332-a011-87ceda047036

## checking if the job id is valid:

bacalhau describe $jid > 


## finding the first octet of the job id:

octets=$(echo $jid | tr "-" " ")

suffix= job_ + ${octets[0]} # 

## now passing the output generated to the surface reconstruction pipeline: 
bacalhau generate $jid

cd  datas/${suffix}/out/ && ( w3 put ${ls } > output_jobFirst)

## then passing the given parameter for the surface reconstruction file
echo "now running the surface reconstruction job " 


bacalhau docker run  $surface_reconstruction -- 

