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
    this implements the modified version of neuralangelo which is run on top of bacalhau node for every image dataset.


## Build instruction: 


1. clone including the submodules : `git clone --recurse-submodules -j8 https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction.git`


2. Run the  preprocessing script in order to create the initial reconstruction pipeline 
```
docker compose build reconstruction
```

## Credits:
1. NVIDIA's implementation of 
    - [neuralangelo](https://github.com/NVlabs/neuralangelo).
    - [instant-ngp]().

2. datasets used for training the model:
    - [eth 3D]().
    - [eth SLAM]().