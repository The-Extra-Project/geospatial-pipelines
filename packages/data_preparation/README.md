## @geospatial-pipelines/data_preparation:

This package provides the tools and utils for the first stage of the operation after fetching data: allowing users to do operations of the current raw dataset of pointcloud (.las, .laz, .pcd) for operations like: 
    - Cropping (2D/3D cropping)
    - conversion of the coordinates 
    - combination of point clouds
    - conversion across various formats.

## installation and setup:
- Install from the pip directory: `pip install pointcloud_extraction_toolkit`.
- Or via the source by cloning the whole [geospatial-pipeline]() and then installing the file via the `pip install -r requirements.txt`.

## Various packages:

| package_file | remarks |
| ------------- | ------------- |
| data_prepatation.cameras.utils | consist of methods to use the API across colmap / neuralangelo for photogrammetry |
| data_prepatation.pdal.pipeline_generation | scripts to generate the pipeline for PDAL to do necessary transformations |
| data_prepatation.cropping | Script to crop the given portion that you want to fetch. |
| data_prepatation.threed_pointcloud | script that integrates the [open3D](https://www.open3d.org) for 3D data cropping at microlevel | 


## API's :


There are colab tutorials in `test/` folder that explain the various usecase, but now try to fetch the 

1. Import the cameras package for the photogrammetry pipeline processing to fetch the pointcloud
> Important: You need to setup colmap before this package in order to work.
```python

from pointcloud_extraction_toolkit.cameras.utils import ColmapDataParsing
import os
colmap_progressing = ColmapDataParsing(filepath="demo.mp4", output_dir="./demo_output")

colmap_progressing.convert_photo_to_video(downsampling_rate=5)


## also fetch the image metadata for the algorithm / reviewer in order to showcase the details.


## now fetching the image metadata from the given details in order to later on do the required transformation on the specific frame <> pose basis if needed.
files = './output/imgs'

data_info = {}

for filename in os.listdir(files):
    full_path = os.path.join(files, filename)
    imagemetadata = colmap_progressing.get_image_metadata(full_path)
    data_info[filename].append(imagemetadata)

## and finally the colmap transformation

await colmap_processing.colmap_transformation()

## in the results you seem to see some of the outputs are not compatible with the alignment then run the following method to fix and rerun colmap_transformation().
## analyze_colmap_images(self,camera_bin_path, transform_file, camera_depth, coordinates_adjust = ["0", "0", "0", "1"] )


colmap_processing.analyze_colmap_images(camera_bin_path= files + "stereo/camera.bin" , transform_file= files + "transforms.json", camera_depth = "", coordinates_adjust = [] )


```

2. Tutorial for 3D data processing directly:


