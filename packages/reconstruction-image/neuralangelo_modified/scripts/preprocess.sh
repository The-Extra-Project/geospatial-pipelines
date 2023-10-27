#!/bin/sh
## $1 is the ETH-3D dataset path  (by default in ../datas/courtyard), 
## but for bacalhau computation will be given by storagespec
## SiftExtraction.use_gpu is set false in case you want to test the preprocessing stage on non gpu instance.
colmap feature_extractor \
    --database_path=`${1}/dataset.db` \ 
    --image_path=`${1}/images/dslr_images_undistorted` \
    --ImageReader.camera_model=SIMPLE_RADIAL \
    --ImageReader.single_camera=true \
    --SiftExtraction.use_gpu=false \
    --SiftExtraction.num_threads=32

colmap sequential_matcher \
    --SiftMatching.use_gpu=false

mkdir -p ${1}/sparse
colmap mapper \
    --database_path=${1}/database.db \
    --image_path=${1}/images_raw \
    --output_path=${1}/sparse
