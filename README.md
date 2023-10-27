# Pipeline-point-cloud-recostruction

**E2E pipeline for reconstructing the given 3D area using neuralangelo in distributed way (i.e by aligning the combination of the various users in the overall viewpoint of the user)** 
<p align="left">
    <a href="https://github.com/https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction.git/LICENSE.md" alt="License">
        <img src="https://img.shields.io/badge/license-MIT-green" />
    </a>
    <a href="https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction/releases/" alt="Release">
        <img src="https://img.shields.io/github/v/release/The-Extra-Project/pipeline-point-cloud-recostruction?display_name=tag" />
    </a>
    <a href="https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction/actions/workflows/build.yml" alt="Tests">
        <img src="https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction/actions/workflows/build.yml/badge.svg" />
    </a>
    <a href="https://extralabs.xyz/">
        <img alt="extralabs website" src="https://img.shields.io/badge/website-extralabs.xyz-green">
    </a>
</p>

## packages / components involved: 
- [reconstruction-image](./packages/reconstruction-image/):
    this implements the modified version of neuralangelo which is run on top of bacalhau node for every image dataset. its implemented in 3 steps 
    - Data_preprocessing step: this will run colmap's image preprocesisng pipeline in order to take the images from a dataset (or eventually from the given dataset of the ) 
        - The dataset to be evaluated for the training purposes are stored at neuralangelo_modified/dataset/
        - Define the path as a parameter to the image repository in order to run the preprocessing pipeline.
    - Model Training: then the resulting reconstruced image point cloud from colmap is passed to the model in order to train and regenerate the isometric generation.

    - Isosurface extaction: This stage the trained transformer model then generates the 3D representation based on the learned description during training on the colmap MVS parsed images.



## Build instruction: 


1. download the image dataset of which you want to generate the 3D reconstruction. for reference we use the [eth-3D](https://www.eth3d.net/datasets) dataset and we download and store the dataset in `reconstruction-image/dataset/courtyard/` directory

2. create the build of  all the dockerfiles 
```
docker compose build  up -d
```
3. run the preprocessing stage by following command:
```
docker compose run data_preprocessing `app/neuralangelo_modified/datasets/<<your dataset_file>>`
``


4. after successful resulting undistorted image, we then get the training pipeline by running 

```bash
docker compose run neuralangelo_training 
## or you can provide the additional parameters (checkpoint, name and training model by setting them in docker compose file)
```

5. And finally generating the neural reconstruction of the model by running the surface_extraction pipeline 

```bash
docker compose run neuralangelo_extraction
```

## Credits:
1. NVIDIA's implementation of 
    - [neuralangelo](https://github.com/NVlabs/neuralangelo).
    
2. datasets used for training the model:
    - [eth 3D]().
    