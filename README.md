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


## Run instructions: 


this pipeline depends on the [pipeline-point-cloud-infrastructure]()

```
docker compose run bacalhau_pipeline. 

```

## Build instruction: 


1. clone including the submodules : `git clone --recurse-submodules -j8 https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction.git`

2. setup the enviornment variable (WEB3_STORAGE env variable) in both the docker-compose.yml and the run_bacalhau.sh script.


3. in the dockerfile.bacalhau, add your corresponding mail in order to validate the web3-storage cli access to the session.

4. Run the script in order to build local packages as containers 
```
docker compose up --build 
```

5. Run `./run_bacalhau.sh` with the parameters in cli (Xcoord, Ycoord, username, URI of shape file stored, filename of template, algorithm category of poisson reconstruction (0 for advanced and 1 for poisson surface reconstruction)) and then it'll generate:
    - The resulting CID of the 3D tiles for the given region.
    - Final reconstructed map in vector format.
    - 3D visualization of the reconstructed map.

