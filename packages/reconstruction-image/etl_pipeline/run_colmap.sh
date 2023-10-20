#!/bin/sh

DATASET_PATH_ETH="./dataset/courtyard/"

colmap feature_extractor \
    --database_path=$DATASET_PATH_ETH/database.db \
    --image_path=$DATASET_PATH_ETH/images/dslr_images_undistorted \
    --ImageReader.camera_model=SIMPLE_RADIAL \
    --ImageReader.single_camera=true \
    --SiftExtraction.use_gpu=true \
    --SiftExtraction.num_threads=32
 

echo "now extracting the sparse representation of the point cloud by matching the images"

colmap sequential_matcher \
    --database_path=$DATASET_PATH_ETH/database.db \
    --SiftMatching.use_gpu=true

echo "And then setting up the sequential matcher"