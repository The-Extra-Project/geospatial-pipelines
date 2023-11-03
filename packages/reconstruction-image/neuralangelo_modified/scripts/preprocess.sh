#!/bin/sh

## $1 is the  URL path of the hosted 3D dataset that the container wants to process
## but for bacalhau computation will be given by storagespec
## SiftExtraction.use_gpu is set false in case you want to test the preprocessing stage on non gpu instance.



wget ${1} -O ./app/neuralangelo_modified/dataset

cd ./app/neuralangelo_modified/ && 7z x dataset


colmap feature_extractor --database_path=./app/neuralangelo_modified/database.db \
    --image_path=${1}/images/dlsr_images \
    --ImageReader.camera_model=SIMPLE_RADIAL \
    --ImageReader.single_camera=true \
    --SiftExtraction.use_gpu=true \
    --SiftExtraction.num_threads=32 \
    --debug

colmap sequential_matcher \
    --SiftMatching.use_gpu=false

mkdir -p ${1}/sparse
colmap mapper \
    --database_path=${1}/database.db \
    --image_path=${1}/images_raw \
    --output_path=${1}/sparse