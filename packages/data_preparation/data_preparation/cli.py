import tyro
import sys
sys.path.append("../")
from data_preparation.data_preparation.photogrammetry.utils import ColmapDataParsing, NerfStudioCameraUtils
from data_preparation.data_preparation.pdal import PDAL_template_manual, PDAL_json_generation_template
from data_preparation.data_preparation.photogrammetry import colmap
from data_preparation.data_preparation.rasterisation import RasterDataTransformation
from data_preparation.cropping import CroppingUtilsLas, CroppingUtilsSHP
from data_preparation.threed_pointcloud import PointCloud3D
import dataclasses

@dataclasses.dataclass
class ColmapData:
    filename: str
    output_dir: str
    downsampling_rate: int = 2


parameter: any
def select_pipeline(choice: str, args:ColmapData) -> None:
    if choice == "camera_preprocessing_colmap":      
        parameter = ColmapDataParsing(args.filename, args.output_dir)
        parameter.convert_video_to_photo(args.downsampling_rate)
        
    


