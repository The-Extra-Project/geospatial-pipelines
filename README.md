# Geospatial-pipeline reconstruction

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

Comprehensive framework for end 2 end management of the point cloud data collection, transformation and visualization process.


## packages / components involved: 


## Build instruction: 

1. For Python application: 
    - You need to run the streamlit file from [visualisation-package](./packages/viz/vizualization-py/) dockerfile .
    - setup an account on the gateway providers (web3.storage or lighthouse are supported at the moment) and then provide the parameters in order to login with 2FA.
    - Setting up the enviornment variables as defined in the folder.
        - For the Mysql. 
        - For web3 package variables. 

## Credits:
1. Research article on the creation of pointcloud pipeline for [nimes](https://github.com/bertt/nimes).
2. PDAL framework.
3. Florent-Poux's articles about point-cloud processing.