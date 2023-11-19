import pytest
from subprocess import check_call
import zipfile
import os
import w3storage
import sys

sys.path.append(os.path.join(os.getcwd(), "../packages"))

from packages.georender.src.georender import run_georender_pipeline_point, run_georender_pipeline_polygon, generate_pdal_pipeline

import argparse
from unittest.mock import patch

URL_LIDARHD = "https://diffusion-lidarhd-brut.ign.fr/download/lidar/shp"
#url_tiles = "https://storage.sbg.cloud.ovh.net/v1/AUTH_63234f509d6048bca3c9fd7928720ca1/ppk-lidar/JE/LHD_FXX_0616_6867_PTS_C_LAMB93_IGN69.copc.laz"

from dotenv import load_dotenv


template_details = ""
filename_template = ""
cid_cropped_files_point = ""
cid_cropped_files_polygon=""
user = "test"
    ## for single point  cropping 
XCoord = "43.8349" 
YCoord = "4.3596"
    ## for the cropping of the given polygon region
X = ["43.8", "42.1"]
Y = ["4.35",  "3.1"]    

user = "test_demo"
load_dotenv(path="../.env")

storage: w3storage.API = w3storage.API(token=os.getenv("WEB3_API"))

ipfs_pipeline = "bafybeibbtseqjgu72lmehn2y2b772wvr36othnc4rpzu6z3v2gfsjy3ew4" 
## hosted on the web3.storage froml datas/pipeline_template.json file
ipfs_shapefile = "bafybeiczrlkcxv2qgomqk72eudi3zw4htz7c24y7yq6urx4bbb4z2jvvci"
## hosted on the web3.storage from the datas/*.shp file 
def test_host_las_storage():
    """
    fetches the input parameter used for testing the pipeline reconstruction
    """
    ""
    if not os.path.exists("./datas"):
        os.mkdir("./datas")
    os.chdir("./datas")
    try:
        check_call(["curl" , URL_LIDARHD , "-o grille-lidarHD" ])
        if os.path.exists("grille-lidarHD.zip"):
            shpFiles= zipfile.ZipFile(mode="r") 
            shpFiles.open("grille-lidarHD")  
        ipfs_shapefile = storage.post_upload("./grille-lidarHD/")
        
    
    ## also get the pipeline template along with the other information
    ## determining that the file are downloaded correctly
    except Exception as e:
        print("Error",e)
    assert os.listdir(".") is not None     
    assert ipfs_shapefile is not None
    storage.post_upload("./grille-lidarHD")
    
    os.chdir("../")  

    
def test_run_cropping_algorithm_point():
    """
    gets the cropped point cloud in compressed format and stores on the web3.storage
    """       
    cliargs = [ XCoord, YCoord, ipfs_shapefile, ipfs_pipeline, user]
    
    with patch.object(sys, 'argv', cliargs):
        cid_cropped_files_point = run_georender_pipeline_point(cliargs=cliargs)
        assert cid_cropped_files_point is not None
    
    


def test_run_cropping_algorithm_polygon():
     """
     gets the cropped point cloud in compressed format and stores on the web3.storage
     """   
     ipfs_pipeline = ""
     cliargs = [ X[0], X[1], Y[0], Y[1], ipfs_shapefile, ipfs_pipeline, user]
     
     with patch.object(sys, 'argv', cliargs):
        cid_cropped_files_polygon = run_georender_pipeline_polygon(cliargs=cliargs)
        assert cid_cropped_files_polygon is not None
    
def surface_reconstruction_point_command():
    """
    passing the cropped file from the georender output to generate the polygon files
    """
    algorithm_choice = 1
    os.chdir(os.path.join('..', 'datas'))
    check_call(['curl',  cid_cropped_files_point + '.ipfs'])
    output_cropped_file = os.lsdir
    try:
        check_call(["docker run -d surface_reconstruction   " + algorithm_choice + " "  + output_cropped_file ])
    except Exception as e:
        print(e)
    

    
    