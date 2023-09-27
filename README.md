# pipeline-point-cloud-recostruction

**E2E pipeline to analyze the raw lidar 3D point cloud data and then convert to finished polygon file for visualization** 
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

Running geospatial algorithms pipeline on the raw shape file in order to generate the corresponding reconstructed 3D polygon mesh of the given region given the coordinates by the user. It runs the pipeline service on the cloud that  runs series of computation algorithms on the pipeline (as defined in the [packages](./packages/) section) which are executed on bacalhau.


## packages / components involved: 
- [georender](./packages/georender/): is the first step in reconstruction. it takes user input for the given region to be reconstructed, and then crops the specific region from the raw lidar point in order to generate the lidar.


-  [surface-construction](./packages/surface_reconstruction/): this job takes the result from georender, and then passes the raw point cloud to the various surface normalization and reconstruction algorithms that user can choose based on their requirements as follows:
    - [poisson reconstruction (by CGAL)](): 
    - [advanced reconstruction algorithm (on CGAL)]()
    - [multisolver poissonRecon adapted version from the algorithm]()

- [py3dtile](./packages/py3dtiles/): this job converts the given ply file into 3dtile specification, which is then parsed by any visualization software in order to get the result.

- [3dtilerendererJS](./packages/3DTilesRendererJS/): finally this is the visualization package that runs the 3dtile specification and then visualizes the result.

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

6. Now the user has to deploy the '3DTilerenderJS' package and then pass the value of CID identifier for rendered tiles.

7. run the E2E testing pipeline by running the deployment pipeline from [e2e](./e2e/) folder.

## Credits:
1. Research article on the creation of pointcloud pipeline for [nimes](https://github.com/bertt/nimes).