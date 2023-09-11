#!/bin/sh

# dockedrhub name of the current version of the deployed pipeline.
georender_pipeline=devextralabs/georender
surface_reconstruction=devextralabs/surface_reconstruction
threeDtiles=devextralabs/py3dtiles

## params : $1 => jobId of the previous bacalhau executed.

parsingOutput() {

jid=${1}

## checking if the job id is valid:

bacalhau describe $jid 

## finding the first octet of the job id:
octets=$(echo $jid | tr "-" " " | cut -b 1-8)

suffix= job_ + ${octets} # 

## now passing the output generated to the surface reconstruction pipeline: 
bacalhau generate $jid

## fetching the output resulting  las file with pipeline , now then you pass the  unzipped las file to surface reconstruction.
cd  datas/${suffix}/out/

filename = ${ls -a}

## then passing the given parameter for the surface reconstruction file
echo "now storing the result" 

cid_cropped_file = `w3 put ${filename}` 

return $cid_cropped_file
}




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
algorithm_surface_reconstruction="0" #(poisson)


# :coordinateX: lattitude coordinate 
#     :coordinateY: longitude coordinate 
#     username: username of the user profile
#     ipfs_cid:  ipfs addresses of the files that you need to run the operation, its the list of the following parameters
#     - pipeline template file address
#     - shp files address that you want to process


echo `$(bacalhau version)`

if [ $? -neq 0]:
then
    echo "bacalhau is installed"
else
    echo "bacalhau is not installed"
fi


#pattern_jobID="^\{?[A-F0-9a-f]{8}-[A-F0-9a-f]{4}-[A-F0-9a-f]{4}-[A-F0-9a-f]{4}-[A-F0-9a-f]{12}\}?$"
bacalhau docker run  $georender_pipeline -i src="https://${ipfs_shp_file}.ipfs.w3s.link/"   dst="./${username}/datas/"     -- $Xcoord $Ycoord  $username $ipfs_cid $filename

if [[$? -eq 0]];
then
echo "the execution was successful"
fi

cid_georender = parsingOutput $param

bacalhau docker run  $surface_reconstruction -i src="./datas/" dst="./${username}/datas/"  --  ${cid_georender}  $algorithm_surface_reconstruction    | sed  '^\{?[A-F0-9a-f]{8}-[A-F0-9a-f]{4}-[A-F0-9a-f]{4}-[A-F0-9a-f]{4}-[A-F0-9a-f]{12}\}?$' > jobId


cid_surface = passingOutput(`echo jobId`)

echo "Now finally conversion of the reconstructed ply format to the 3D tiles for rendering"

## $(pwd)/data:/usr/src/app/3DTilesRendererJS/data
bacalhau docker run $threeDtiles -i src="./data" dst="/usr/src/app/3DTilesRendererJS/data"  -- ${cid_surface}  


#$(pwd)/data:/usr/src/app/3DTilesRendererJS/data

if [ $? -eq 0 ]
then
    echo "error running the pipeline"
    exit 1
fi

cid_threeD = parsingOutput(`echo jobId`)

echo "the 3Dtile generated is on"  + ${cid_threeD}