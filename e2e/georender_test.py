import pytest
from subprocess import check_call
import zipfile
import os
import w3storage
WEB3_STORAGE_URL=""
URL_LIDARHD = "https://diffusion-lidarhd-brut.ign.fr/download/lidar/shp"
from dotenv import load_dotenv
ipfs_shapefile = ""
ipfs_pipeline = ""
storage: w3storage.API = w3storage.API(token="<KEY>")

params = load_dotenv("")

def test_get_input_parameters():
    """
    fetches the input parameter used for testing the pipeline reconstruction
    """
    check_call(["w3 authorize malikdhruv1994@gmail.com"])
    if not os.path.exists("./datas"):
        os.mkdir("./datas")
    os.chdir("./datas")
    #status = get(URL_LIDARHD)
    # downloading the package with the shapefile
    try:
        check_call(["curl" , URL_LIDARHD , "-o grille-lidarHD" ])
        # if os.path.exists("grille-lidarHD.zip"):
        #     shpFiles= zipfile.ZipFile(mode="r") 
        #     shpFiles.extractall("grille-lidarHD")  
        check_call(["w3 up ./grille-lidarHD.zip" ])
        
        
    ## determining that the file are downloaded correctly
    except Exception as e:
        print("Error",e)
    assert os.listdir(".") is not None 
    
    storage.post_upload("./grille-lidarHD")
    
    os.chdir("../")  
    
    
    
    
def test_run_cropping_algorithm():
    """
    
    
    
    """   

    
    