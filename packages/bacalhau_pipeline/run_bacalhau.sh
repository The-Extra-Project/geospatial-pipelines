#!/bin/sh
## reference from stackoverflow, in order to only reference the changes in the run pipeline for the changes in shell.

# ECR registry of the current verion of the pipeline.
georender_pipeline=devextralabs/georender
surface_reconstruction=devextralabs/surface_reconstruction
threeDtiles=devextralabs/py3dtiles

## params : $1 => jobId of the previous bacalhau executed.

parsingOutput() {

jid=${1}

## finding the first octet of the job id:
octets=$(echo "${jid}" | tr "-" " " | cut -b 1-8)

output_folder="job_""${octets}" # 

## now passing the output generated to the surface reconstruction pipeline: 
bacalhau generate "$jid"

## fetching the output resulting  las file with pipeline , now then you pass the  unzipped las file to surface reconstruction.
cd  "datas/""${output_folder}""/out/"

if [ $? -eq 0 ];
then
    echo "bacalhau is installed"
else
    echo "bacalhau is not installed"
    exit 1
fi

filename="$(ls -a)"

## then passing the given parameter for the surface reconstruction file
echo "now storing the result" 

cid_cropped_file="w3 put ${filename}"

return "$cid_cropped_file"

}

## parameters:
## point coordinates (X/Y) for the specific job that you want to run.
## IPFS CID of the given shape file that you want to run.
## IPFS CID of the pipeline template that you want to generate
## filename of the template
## username of the person running the job
##  category of reconstruction algorithm you want to implement (0 for advance and 1 for poisson template)
# Xcoord="43.2946"
# Ycoord="5.3695"
# Username="test"
# ipfs_shp_file="bafkreicxd6u4avrcytevtvehaaimqbsqe5qerohji2nikcbfrh6ccb3lgu"
# ipfs_template_file=""
# filename="pipeline_template.json"
# algorithm_surface_reconstruction="0" #(poisson)


pattern_jobID='s/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/p'

bacalhau docker run $georender_pipeline  -- ${1} ${2} ${3} ${4} ${5} ${6}


if [ $? -eq 0 ];
then
echo "the execution was successful"
fi


jobId= $(echo $(echo $param | sed -n $pattern_jobID))

echo $jobId

cid_georender=parsingOutput jobId

bacalhau docker run  $surface_reconstruction --  "$(cid_georender)"  ${6}  | sed -n  $pattern_jobID > jobId

echo "Now finally conversion of the reconstructed ply format to the 3D tiles for rendering"

## $(pwd)/data:/usr/src/app/3DTilesRendererJS/data
bacalhau docker run $threeDtiles -i  -- "passingOutput $(jobId)"


#$(pwd)/data:/usr/src/app/3DTilesRendererJS/data

if [ $? -neq 0 ];
then
    echo "error running the pipeline"
    exit 1
fi

cid_threeD=parsingOutput jobId

echo "the 3Dtile generated is on"  + "passingOutput $(cid_threeD)"
