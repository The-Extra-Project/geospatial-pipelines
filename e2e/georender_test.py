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
from dotenv import load_dotenv

ipfs_shapefile = ""
ipfs_pipeline = ""
filename_template = ""

user = "test"
    ## for single point  cropping 
XCoord = "43.8349" 
YCoord = "4.3596"
    ## for the cropping of the given polygon region
X = ["43.8", "42.1"]
Y = ["4.35",  "3.1"]    



paramsPoint = argparse.ArgumentParser()
paramsPolygon = argparse.ArgumentParser()
user = ""
load_dotenv(path="../.env")

storage: w3storage.API = w3storage.API(token=os.getenv("WEB3_API"))



def test_get_input_parameters():
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
        cid_cropped_files = run_georender_pipeline_point()
        assert cid_cropped_files is not None
    
    


def test_run_cropping_algorithm_polygon():
     """
     gets the cropped point cloud in compressed format and stores on the web3.storage
     """   
     
     cliargs = [ X[0], X[1], Y[0], Y[1], ipfs_shapefile, ipfs_pipeline, user]
     
     with patch.object(sys, 'argv', cliargs):
        cid_cropped_files = run_georender_pipeline_polygon()
        assert cid_cropped_files is not None
    
    
    

    

    
    