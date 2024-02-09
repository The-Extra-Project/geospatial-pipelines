import sys
sys.path.append("../../")

from data_preparation.cameras.utils import ColmapDataParsing, NerfStudioCameraUtils

from subprocess import check_call
import os

async def setup_dataset():
    url = "https://storage.googleapis.com/t2-downloads/image_sets/Ignatius.zip"
    if not os.path.exists("./datas/Ignatius/"):
        try:
            os.chdir("datas/Ignatius")
            check_call(["wget", "--user-agent=Mozilla/5.0", url])
            check_call(["7z", "x", "Ignatius.zip"])
            check_call(["rm", "Ignatius.zip"])            
        except Exception as e:
            print("downlaod failed due to error:" + str(e))
    
    
    else:
        print("dataset already exists")
   
   
filepath = "./datas/Ignatius"
output_dir = "./datas/colmap_output_ignatius/"
colmap_parsing = ColmapDataParsing(filepath=filepath, output_dir=output_dir)

async def test_image_parsing():
    await setup_dataset()

    for files in os.listdir(filepath):
        metadata = colmap_parsing.get_image_metadata(files)    
        assert metadata is not None
    
    
async def test_colmap_transformation():
    await setup_dataset()
    
    colmap_parsing.colmap_transformation()
    assert os.path.exists(output_dir) is True
    assert  os.path.exists(output_dir + "bin/") is True
  

    

    
    
