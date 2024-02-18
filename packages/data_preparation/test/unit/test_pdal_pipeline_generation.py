import sys
sys.path.append("../../")
from data_preparation.pdal.pipeline_generation import PDAL_template_manual
from packages.data_preparation.data_preparation.cropping import CroppingUtilsLas
from subprocess import check_call
from shapely.geometry import  Point
from pyproj import Transformer
import os


data_file = os.path.join('../../','datas')

if not os.path.exists(data_file):
    os.mkdir(data_file)
    check_call( ["wget", "--user-agent=Mozilla/5.0",  "https://bafybeic7vjtoffchve57v2j3p32v3nuflhtey37bii3v4j6mwzyfowfc7e.ipfs.w3s.link/07ED4844.las" ])
    check_call(["mv", "07ED4844.las", data_file])
    check_call( ["wget", "--user-agent=Mozilla/5.0",  "https://bafybeic7vjtoffchve57v2j3p32v3nuflhtey37bii3v4j6mwzyfowfc7e.ipfs.w3s.link/07ED4924.las" ])
    check_call(["mv", "07ED4924.las", data_file])


pipeline_template = PDAL_template_manual()
las_file = os.path.join(data_file,"07ED4844.las")
las_values = CroppingUtilsLas(las_file)

distance = 5

headers = las_values.fetch_header_parameters(las_file)
Points1 = Point(float(37.124), float(136.54), float(1.0))
X1_scaled, Y1_scaled, Z1_scaled = las_values.scaled_dimensions(Points1.x, Points1.y, Points1.z, headers)

transformer = Transformer.from_crs('EPSG:4326','EPSG:6685')

X1,Y1,Z1 = transformer.transform(X1_scaled, Y1_scaled, Z1_scaled)
    

def test_generate_cropping_template():
    output_json_file = las_file.generate_cropping_template(las_file, f"POINT({X1,Y1,Z1})", distance, "cropped_file.las" ) 
    assert output_json_file['pipeline'][0][0] == las_file  
    assert output_json_file['pipeline'][0][1]['type'] == "filters.crop"
    
    
def test_execute_pipeline():
    output_json_file = las_file.generate_cropping_template(las_file, f"POINT({X1,Y1,Z1})", distance, "cropped_file.las" ) 
    pipeline_template.run_pipeline(output_json_file)
    
def test_merge_pointclouds():
    las_one = os.path.join(data_file,"07ED4844.las")
    las_two = os.path.join(data_file,"07ED4924.las")
    
    generate_result = pipeline_template.merge_pointclouds([las_one,las_two], "merged_file.las") 
    
    header_details_merged = las_values.fetch_header_parameters("merged_file.las")
    header_details_one = las_values.fetch_header_parameters(las_one)
    header_details_two = las_values.fetch_header_parameters(las_two)
    assert header_details_one
      





