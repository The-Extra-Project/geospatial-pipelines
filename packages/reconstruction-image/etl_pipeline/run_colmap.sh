#!/bin/sh

DATASET_PATH_ETH="./dataset/courtyard/"

colmap feature_extractor \
    --database_path=$DATASET_PATH_ETH/database.db \
    --image_path=${1}/images/dslr_images_undistorted \
    --ImageReader.camera_model=SIMPLE_RADIAL \
    --ImageReader.single_camera=true \
    --SiftExtraction.use_gpu=true \
    --SiftExtraction.num_threads=32

