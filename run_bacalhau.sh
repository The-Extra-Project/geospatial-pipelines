#!/bin/sh
## reference from stackoverflow, in order to only reference the changes in the run pipeline for the changes in shell.
# dockedrhub name of the current version of the deployed pipelines, change them to your corresponding parameters.

georender_pipeline=devextralabs/georender
surface_reconstruction=devextralabs/surface_reconstruction
threeDtiles=devextralabs/py3dtiles

## function that parses the output of the previously exeuted pipeline and then uploades the result along with retuning the jobid.
## params : $1 => jobId of the previous bacalhau executed.
parsingOutput() {
jid=${1}
## see the result
bacalhau describe "$jid" 
## finding the first octet of the job id, which will be used to construct the folder of the intermediate outputs
octets=$(echo "${jid}" | tr "-" " " | cut -b 1-8)

suffix="job_""${octets}" # 

## now passing the output generated to the surface reconstruction pipeline: 
bacalhau generate "$jid"


if [ -d "'datas/' + ${suffix} + '/out/'" ];
then
    echo "bacalhau is installed"
else
    echo "bacalhau is not installed"
    exit 1
fi
## fetching the output resulting  las file with pipeline , now then you pass the  unzipped las file to surface reconstruction.
cd "'datas/'${suffix}'/out/'"
filename="$(ls -a)"
## then passing the given parameter for the surface reconstruction file
echo "now storing the result on the IPFS for corresponding stages" 
cid_cropped_file="w3 put ${filename}"
return "$cid_cropped_file"

}

## parameters:
## point coordinates (X/Y) for the specific job that you want to run.
## IPFS CID of the given shape file that you want to run.
## filename of the template
## username of the person running the job
##  category of reconstruction algorithm you want to implement (0 for advance and 1 for poisson template)
# Xcoord="43.2946"
# Ycoord="5.3695"
# username="test"
# ipfs_shp_file="bafkreicxd6u4avrcytevtvehaaimqbsqe5qerohji2nikcbfrh6ccb3lgu"
# filename="pipeline_template.json"
# algorithm_surface_reconstruction="0" #(poisson)



val=$(bacalhau version)


if [ "$val" -eq 0 ];
then
    echo "bacalhau is installed"
else
    echo "bacalhau is not installed"
fi

pattern_jobID="^\{?[A-F0-9a-f]{8}-[A-F0-9a-f]{4}-[A-F0-9a-f]{4}-[A-F0-9a-f]{4}-[A-F0-9a-f]{12}\}?$"

jobId=bacalhau docker run  $georender_pipeline  -- ${1} ${2} ${3} ${4} ${5} | sed "$pattern_jobID"

if [ $? -eq 0 ];

then
echo "the execution was successful"
fi

cid_georender=parsingOutput $jobId

## now running the surface reconstruction and getting the result 

jobId="$(bacalhau docker run  $surface_reconstruction --  "$(cid_georender)"  "${6}"  | sed  "$pattern_jobID")"

echo "Now finally conversion of the reconstructed ply format to the 3D tiles for rendering"


cid_threeDTIles=passingOutput $jobId

## $(pwd)/data:/usr/src/app/3DTilesRendererJS/data
bacalhau docker run $threeDtiles -i  -- "$(cid_threeDTIles)"


#$(pwd)/data:/usr/src/app/3DTilesRendererJS/data

if [ $? -eq 1 ];
then
    echo "error running the pipeline"
    exit 1
fi

cid_threeD=parsingOutput "${jobId}"
echo "the 3Dtile generated is on"  + "passingOutput $(cid_threeD)"