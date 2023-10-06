# pipeline-point-cloud-recostruction

**E2E pipeline for reconstructing the given surface by using photogrammetry and the state of the art rendering terchniques [like 3D gaussian splatting] by implementing distributed way (i.e by aligning the combination of the various users in the overall viewpoint of the user)** 
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

-  [slam](./packages/surface_reconstruction/): 

## Build instruction: 


1. clone including the submodules : `git clone --recurse-submodules -j8 https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction.git`


4. Run the script in order to build local packages as containers 
```
docker compose up --build 
```

## Credits:
1. NVIDIA's implementation of 
    - [neuralangelo](https://github.com/NVlabs/neuralangelo).
    - [instant-ngp]().

2. datasets used for training the model:
    - [eth 3D]().
    - [eth SLAM]().