import rasterio
from rasterio.transform import from_origin
from rasterio.enums import Resampling
from rasterio.features import shapes
import numpy as np
from shapely.geometry import Polygon
"""
credits to the example jupyter tutorial implementation of the lidar: https://colab.research.google.com/drive/1X2dQZUesfm8Y7hUYjjGJH2KjN129jcY7#scrollTo=adb4d046-0d73-46dc-b0df-c09bdafd5e2c.
"""


class RasterDataTransformation():
    """
    class consisting of functions to rasterrise the data from laz file format in order to store the GeoTif file for vizualization.
    Coordinate_params: an array that  defines the max/min boundation for the coordinate_params for the DEM
    
    """

    pixel_size: int
    
    def __init__(self,_coordinate_array:any, _pixel_size: int ):
        assert _pixel_size !=0 and _pixel_size > 1
        self.minx, self.miny, self.maxx, self.maxy = _coordinate_array
        self.number_pixels_x = int((self.maxx - self.minx) / _pixel_size)
        self.number_pixels_y = int((self.maxy - self.miy)/ _pixel_size)
        
        
    def generate_tiff(self,x,y,z, resulting_tif_path, crs):
        """
        function to generate the GeoTiff file in order to generate the elevation points and general boundation for reconstruction step.
        xyz are the coordinates for the filtered dataset (generated using np.vstack),
        crs is the coordinate ref system standard (in EPSG format) for users in order to get result.
        
        
        
        """
        transform = from_origin(self.minx, self.maxy, self.pixel_size, self.pixel_size)
        dem_vectorization = np.zeros((self.number_pixels_x, self.number_pixels_y), dtype=np.float32)
        
        ## fetch the row and col indices n insure that they conform to the boundations
        col_indices = ((x - self.min_x) / self.pixel_size).astype(int)
        row_indices = ((self.max_y - y) / self.pixel_size).astype(int)

        # Mask to ensure indices are within bounds
        valid_indices = (0 <= row_indices) & (row_indices < self.num_pixels_y) & (0 <= col_indices) & (col_indices < self.num_pixels_x)
        # Populate the DEM array with elevation values from the point cloud
        dem_vectorization[row_indices[valid_indices], col_indices[valid_indices]] = z[valid_indices]
        
        with rasterio.open(resulting_tif_path, 'w', driver='GTiff', height=self.number_pixels_x, width=self.number_pixels_y, count=1, dtype=np.float32, crs=crs) as dst:
            dst.write(dem_vectorization, 1)
            
        
    def show_created_raster_file(tif_file):
        mask=None
        with rasterio.Env():
            with rasterio.open(tif_file) as src:
                image = src.read(1) # first band
                results = (
                {'properties': {'raster_val': v}, 'geometry': s}
                for i, (s, v)
                in enumerate(
                shapes(image.astype(np.float32), mask=mask, transform=src.transform))
                )

        return list(results)
    
                
        
        
            
        