# Pipeline-point-cloud-to-CityGML-reconstruction

**E2E pipeline to generate the CityGML file and visualization corresponding to the processed pointcloud/Mesh file** 

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

## Packages / components involved: 

- [threed_fier_module]: it gets the general cropped mesh file from the pipeline pointcloud,  and then it generates the LoD1 version of the cityGML format.

## Run instructions: 
1. Fenerate the input elevation datasets from the result from the georender cropping pipeline.
2. fetch the corresponding sql format dataset used for populating the relevation elevation fields of the given region of reconstruction.



## Build instruction: 


