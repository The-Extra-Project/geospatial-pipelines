#!/bin/sh
## reference from stackoverflow, in order to only reference the changes in the run pipeline for the changes in shell.

# ECR registry of the current verion of the pipeline.

threedtiles=devextralabs/threedtiles

fn parsingOutput() {

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
    echo "output is generated"
else
    echo "output is not generated, check the job status"
    exit 1
fi

filename="$(ls -a)"

## then passing the given parameter for the surface reconstruction file
echo "now storing the result" 

cid_cropped_file="w3 put ${filename}"

return "$cid_cropped_file"

}

## parameters:
## point coordinates (X/Y) for the specific job that you want to run (for now within the netherlands region)
## IPFS CID of the given shape file that you want to run.
## IPFS CID of the datasets that you want to use for generation.
## filename of the template

pattern_jobID='s/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/p'

bacalhau docker run $threedtiles  -- ${1} ${2} ${3} ${4} ${5} ${6}


if [ $? -eq 0 ];
then
echo "the execution was successful"
fi


jobId= $(echo $(echo $param | sed -n $pattern_jobID))

echo $jobId

cid_georender=parsingOutput jobId

echo "the 3Dtile generated is on"  + "passingOutput $(cid_threeD)"
