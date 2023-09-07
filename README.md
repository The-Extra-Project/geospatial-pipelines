# pipeline-point-cloud-recostruction

**E2E pipeline to analyze the raw lidar 3D point cloud data and then convert to finished polygon file for visualization** 
<p align="left">
    <a href="https://github.com/https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction.git/LICENSE.md" alt="License">
        <img src="https://img.shields.io/badge/license-MIT-green" />
    </a>
    <a href="https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction/releases/" alt="Release">
        <img src="https://img.shields.io/github/v/release/The-Extra-Project/pipeline-point-cloud-recostruction?display_name=tag" />
    </a>
    <a href="https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction/actions/workflows/go.yml" alt="Tests">
        <img src="https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction/actions/workflows/go.yml/badge.svg" />
    </a>
    <a href="https://extralabs.xyz/">
        <img alt="extralabs website" src="https://img.shields.io/badge/website-extralabs.xyz-green">
    </a>
</p>

Running geospatial algorithms pipeline on the raw shape file in order to generate the corresponding reconstructed polygon file. it runs on [bacalhau]() with various docker containers running in parallel


## packages / components involved (in their working order): 
- [georender](./packages/georender/): is the first step in reconstruction. it takes user input for the given region to be reconstructed, and then crops the specific region from the raw lidar point in order to generate the lidar.
-  [surface-construction](./packages/surface_reconstruction/): this job takes the result from georender, and then passes the raw point cloud to the GDAL reconstruction function in order to generate the corresponding PLY file.

- [py3dtile](./packages/py3dtiles/): this job converts the given ply file into 3dtile specification, which is then parsed by any visualization software in order to get the result.

- [3dtilerendererJS](./packages/3DTilesRendererJS/): finally this is the visualization package that runs the 3dtile specification and then visualizes the result.

## Running the pipeline: 


first build the indivisual services 
```
docker compose up --build 

```
## Build instruction: 
1. clone including the submodules : `git clone --recurse-submodules https://github.com/The-Extra-Project/pipeline-point-cloud-recostruction.git`

2. Run the script in order to build local packages as containers 
```
docker compose up --build 
```

3. Run `./run_bacalhau.sh` with the parameters in cli (Xcoord, Ycoord, username, URI of shape file stored, filename of template, algorithm category of poisson reconstruction (0 for advanced and 1 for poisson surface reconstruction)) and then it'll generate the resulting CID of the 3D tiles for the given region.
