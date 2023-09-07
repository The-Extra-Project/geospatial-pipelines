
"""georenderin contract."""
"""georender package script."""
import argparse
import geopandas as gpd
import json
from shapely.geometry import Polygon, Point
from shapely.ops import transform
from web3Storage import API
import os
from subprocess import run
import logging
from py3dtiles  import Tileset
import sys
from pathlib import Path
from dotenv import dotenv_values
import laspy




config = dotenv_values(dotenv_path='.env')

from pyproj import Transformer, Proj
from functools import partial

from subprocess import check_call
import shutil
from osgeo import gdal
## for handling the SHP files that are streamed / downloaded
gdal.SetConfigOption('SHAPE_RESTORE_SHX', 'YES')

## api to access the w3 storage.
w3 = API(os.getenv("W3_API_KEY"))


def fetch_shp_file(ipfs_cid, _filename, username) -> str:
    """
    gets the file that needs to be used for the rendering the resulting surface reconstruction of the given portion
    
    Parameters:

    
    :ipfs_cid: is the CID hash where the file is stored on IPFS
    :_filename: is the name of the file to be downloaded (with the extension)
    :username: is in which folder the given file is to be stored for maintaining the result separation.
    """
    
    # create a directory for the user for the first time.
    path_datas = os.path.join(os.getcwd() + "/datas")
    userdir = (path_datas + "/" + username)

    ## check if the given userdir is created first time
    if os.path.isdir(userdir) == False:
        os.mkdir(path=userdir)
    os.chdir(userdir)    
    
    print("Running with ipfs_cid={}, filename={}".format( ipfs_cid,_filename ) )
    url = 'https://' + ipfs_cid + '.ipfs.w3s.link/' + _filename 
    out_file = run(['wget', '-U Mozilla/5.0', url , '-O', _filename])
        
    print("output status" + str(out_file.returncode))
    if out_file.returncode!= 0:
        print("error in downloading the file")

    else:
        print("file downloaded in {}{}".format(os.getcwd() + '/' +"datas/",_filename))
    
    return (os.getcwd() + "/datas" +_filename)
  
def create_bounding_box(latitude_max: int, lattitude_min: int, longitude_max: int, longitude_min: int):
    """
    Create a bounding box which the user selects to fetch the parameters for the given file parameters
    """
    return Polygon([(longitude_min, lattitude_min), (longitude_max, lattitude_min), (longitude_max, latitude_max), (longitude_min, latitude_max), (longitude_min, lattitude_min)])



def get_tile_details_polygon(pointargs: list(str), ipfs_cid: str, username: str, filename: str, epsg_standard: list(str) = ['EPSG:4326', 'EPSG:2154']):
    """
    utility function for generating the tile standard based on the specific boundation defined by the user on the given shp file
    :pointargs: list of inputs in the format (lattitude_max, lattitude_min, longitude_max, longitude_min)
    :ipfs_cid: cid of the corresponding shp file to be presented.
    :username: identifier for the given shp file that is storing the file.
    
    :epsg_standard: defines the coordinate standards for which the given given coordinate values are to be transformed
        - by default the coordinates will be taken for french standard, but can be defined based on specific regions.
    Returns:
    
    laz file url which is to be downloaded
    fname: corresponding file that is to be downloaded
    dirname: resulting access path to the directory in the given container envionment
    """
    print( "Running tiling with the parameters lat_max={}, lat_min={}, long_max={}, long_min={}, for the user={}".format( pointargs[0], pointargs[1], pointargs[2], pointargs[3], username))

    # this is the docker path of file, will be changed to the w3storagea
    print("reading the shp file")
    
    path = fetch_shp_file(ipfs_cid, filename, username)
    data = gpd.read_file(path)
    
    
    polygonRegion = create_bounding_box(pointargs[0], pointargs[1], pointargs[2], pointargs[3])

    # transformer = Transformer.from_crs( epsg_standard )
    # coordX, coordY = transformer.transform( coordX, coordY )

    projection = partial(
        transform, Proj(epsg_standard[0]), Proj(epsg_standard[1])
    )
    
    polygonTransform = transform(projection, polygonRegion)
    
    out = data.intersects(polygonTransform)
    res = data.loc[out]
   
    laz_path = res["url_telech"].to_numpy()[0]
    dirname = res["nom_pkk"].to_numpy()[0]
   
    fname = dirname + ".7z"

    print("returning the cooridnates of given polygon boundation{}:{}{}{}".append(pointargs,laz_path, dirname,dirname))

    return laz_path, fname, dirname


def get_tile_details_point(coordX, coordY,username, filename, ipfsCid, epsg_standards: list(str) = ['EPSG:4326', 'EPSG:2154'] ):
    """
    utility function to get the tile information for the given boundation
    :coordX: X coordinate of the given region
    :coordY: Y coordinate of the given region
    :username: username of the user profile
    :ipfsCid: reference of the CID file that is already stored in the IPFS network.
    :filename: name of the given SHP file format that you want to read. 
    :epsg_standards: coordinate standard defined as [input cooridnate standard to destination]
        - normally set for the input as EPSG:4326 (WGS) and destination as EPSG:2154 (french standard).
    """
    print( "Running with X={}, Y={}".format( coordX, coordY ) )

    ## function  to download file from ipfs to given path in the docker.
    fp = fetch_shp_file(ipfs_cid=ipfsCid, _filename= filename, username= username)
    
    data = gpd.read_file(fp)

    # todo : how to avoid rewriting too much code between bounding box mode and center mode ?
    # todo : Document input format and pyproj conversion
    # see link 1 ( to epsg codes ), link 2 ( to pyproj doc )
    transformer = Transformer.from_crs( epsg_standards[0], epsg_standards[1] )
    
    coordX, coordY = transformer.transform( coordX, coordY )

    center = Point( float(coordX), float(coordY) )

    out = data.intersects(center)
    res = data.loc[out]
    laz_path = res["url_telech"].to_numpy()[0]
    dirname = res["nom_pkk"].to_numpy()[0]
    fname = dirname + ".7z"

    print("returning the details of corresponding coorindate{},{}:{}{}{}".append(coordX,coordY,laz_path, dirname,dirname))
    
    return laz_path, fname, dirname



def generate_pdal_pipeline( dirname: str,pipeline_template_ipfs: str, username: str, epsg_srs:str =  "EPSG:2154" ):
    """
    generates the pipeline json for the given tile structure in the pipeline based on the given template stored on ipfs.
    :dirname: is the directory where the user pipeline files are stored 
    :pipeline_template_ipfs: is the reference of the pipeline template is stored.  
    :epsg_srs: is the coordinate standard corresponding to the given template position.
    """
   
    path_datas = os.path.join(os.getcwd() + "/datas" + username) 
    
    url = 'https://' + pipeline_template_ipfs + '.ipfs.w3s.link/pipeline_template.json' 
       
    try:
        filedownload = run(['wget', '-U Mozilla/5.0', url , '-O', path_datas + 'pipeline_template.json'])

    except IOError as e:
        print("error to download file"+e)
    
    pipeline_filedir = path_datas +'pipeline_template.json'
    
    # Pdal pipeline is specified by a json
    # basically it's a list of filters which can specify actions to perform
    # each filter is a dict
    # Open template file to get the pipeline struct 
    
    with open( pipeline_filedir, 'r' ) as file_pipe_in:
        file_str = file_pipe_in.read()
    
    pdal_pipeline = json.loads( file_str )

    # List files extracted
    # Now we don't check extension and validity
    file_list = os.listdir( dirname )

    # Builds the list of dicts and filetags ( fname without ext )
    ftags = []
    las_readers = []
    for fname in file_list:
        tag = fname[:-4]
        ftags.append( tag )
        las_readers.append( { "type": "readers.las", "filename": fname, "tag": tag, "default_srs":epsg_srs } )
    
    # Insert file tags in the list of inputs to merge
    # Must be done before next insertion because we know the place of merge filter in the list at this moment
    for ftag in ftags:
        pdal_pipeline['pipeline'][0]['inputs'].insert( 0, ftag )

    # Insert the list of las file readers dicts
    for las_reader in las_readers:
        pdal_pipeline['pipeline'].insert( 0, las_reader )
    
    pipeline_generated = "pipeline_gen_" + username + ".json"
    
    with open( pipeline_generated, "w" ) as file_pipe_out:
        json.dump( pdal_pipeline, file_pipe_out )

    if os.path.isfile(pipeline_generated):
        print(" pdal pipeline file is stored in the given directory  as {}".format(pipeline_generated))

    return pdal_pipeline


## cli functions:
""" functions to seting up the input and then georender pipeline. 
"""
def upload_files():
    """
    uploads the  along with all the shp files into the given web3 storage provider (pipeline and shp files).
    
    georender.py  upload_files -l  testfile.json test.las, test2.las, ..... 
    """
    parser=argparse.ArgumentParser(description="takes the name of files (pipeline.json / shp files) and stores to the given storage provider")
    parser.add_argument('-l',nargs='+', help='<Required> Set -l flag', required=True)
    
    loaded_files_cid = []
    args = parser.parse_args
    filecounter = 0
    for fileIter in args:
       if os.path.exists(fileIter):
            filecounter += 1          
            loaded_files_cid.append(w3.post_upload(fileIter))
            print("File {} uploaded successfully on cid: {} ".format(fileIter, loaded_files_cid[filecounter]))
    return loaded_files_cid

## Pipeline creation
def run_georender_pipeline_point():
    """
    this function the rendering data pipeline of various .laz file and generate the final 3Dtile format.
    :coordinateX: lattitude coordinate 
    :coordinateY: longitude coordinate 
    username: username of the user profile
    ipfs_cid:  ipfs addresses of the files that you need to run the operation, its the list of the following parameters
    - pipeline template file address
    - shp files address that you want to process
    
    filename: name of the file stored on the given ipfs.
    """
    # Uses geopanda and shapely to intersect gps coord with available laz tiles files
    # Returns corresponding download url and filename
    
    args = argparse.ArgumentParser(description="runs the georender pipeline based on the given geometric point")
    args.add_argument("coordinateX", help="write lattitude in source coordinate system")
    args.add_argument("coordinateY", required=True)
    args.add_argument("username")
    args.add_argument("ipfs_shp_files", required=True)
    args.add_argument("ipfs_template_files", required=True)
    args.add_argument("filename_template")
    
    parameters = args.parse_args()
    
    laz_path, fname, dirname = get_tile_details_point(parameters.coordinateX, parameters.coordinateY, parameters.userprofile, parameters.filename, parameters.ipfs_cid)

    os.chdir( os.getcwd() + "/data") 
    os.mkdir(parameters.userprofile)
    
    # Causes in case if the file has the interrupted downoad.
    if not os.path.isfile( fname ): 
        check_call( ["wget", "--user-agent=Mozilla/5.0", laz_path])
    # Extract it
    
    check_call( ["7z", "-y", "x", fname] ) 
    pipeline_ipfs = parameters["ipfs_template_files"]
    pipeline_file = generate_pdal_pipeline( dirname, pipeline_ipfs, parameters["username"] )

    # run pdal pipeline with the generated json :
    os.chdir( dirname )
    # todo : There should be further doc and conditions on this part
    #        Like understanding why some ign files have it and some don't
    # In case the WKT flag is not set :
    # need to handle the edge cases with different EPSG coordinate standards
    for laz_fname in os.listdir( '.' ):
        f = open( laz_fname, 'rb+' )
        f.seek( 6 )
        f.write( bytes( [17, 0, 0, 0] ) )
        f.close()
    ## now running the command to generate the 3d tile from the stored pipeline 
    os.chdir()
    check_call(["pdal", "pipeline",pipeline_file])
    
    shutil.move( 'result.las', '../result.las' )
    print('resulting rendering successfully generated, now uploading the files to ipfs')
    cid = w3.post_upload('result.las')
    return cid

def run_georender_pipeline_polygon(cliargs=None):
    """
    This function allows to run pipeline for the given bounded location and gives back the rendered 3D tileset
    :coordinates: a list of 4 coordinates [lattitude_max, lattitude_min, longitude_max, longitude_min ]
    ::    
    """
    args = argparse.ArgumentParser(description="runs the georender pipeline based on the given geometric polygon")
    args.add_argument("coordinates", nargs=4, help="writes the bounding coordinates (longitude max/ min and then lattitude points separated by ,)")
    args.add_argument("username")
    args.add_argument("ipfs_cid",nargs='+',help="compulsory: adds the ipfs of the raw cloud image and the corresponding pipeline template. add first the cid of laz file and then of the pipeline template (separated by the space)", required=True)
    args.add_argument("filename", help="defines the filename of the given laz file that you want to generate 3D points for")
    parameters = args.parse_args(cliargs)
    
    laz_path, fname, dirname = get_tile_details_point(parameters.coordinateX, parameters.coordinateY, parameters.userprofile, parameters.filename, parameters.ipfs_cid)

    os.chdir( os.getcwd() + "/data") 
    os.mkdir(parameters.userprofile)
    
    # Causes in case if the file has the interrupted downoad.
    if not os.path.isfile( fname ): 
        check_call( ["wget", "--user-agent=Mozilla/5.0", laz_path])
    # Extract it
    check_call( ["7z", "-y", "x", fname] ) 
    pipeline_ipfs = parameters["ipfs_cid"][0]
    generate_pdal_pipeline( dirname, pipeline_ipfs, parameters["username"] )

    # run pdal pipeline with the generated json :
    os.chdir( dirname )
    
    for laz_fname in os.listdir( '.' ):
        f = open( laz_fname, 'rb+' )
        f.seek( 6 )
        f.write( bytes( [17, 0, 0, 0] ) )
        f.close()
    ## now running the command to generate the 3d tile from the stored pipeline 
    pipeline_template = parameters["ipfs_cid"][1] 
    check_call( ["pdal", "pipeline",pipeline_template] )
    
    shutil.move( 'result.las', '../result.las' )
    print('resulting rendering successfully generated, now uploading the files to ipfs')
    w3.post_upload('result.las')
    
def las_to_tiles_conversion(username: str):
    """
    this function runs the dockerised version of the py3Dtiles in order to take in the las file
    generated in the `run_georender_pipeline_point` and convert it to the 3D tiles.
    based on the pipeline generataed for the pdal. 
    
    las_file: corresponds to the las file generated as the result
    """
        
    last_las_file = os.path.abspath("/app/usr/georender/src/data/" + username + "/result.las")
        
    destination_tile_file = os.getcwd() + username + '/3dtiles'
    # run the dockerised version of the py3dtiles application
    check_call( ["docker", "run", "-it", "--rm" ,
            "--mount-type=bind, source= ${}/data".format(os.getcwd()) ,
            " --target /app/data/" +  destination_tile_file   
            + "registry.gitlab.com/oslandia/py3dtiles:142-create-docker-image" , "convert " , "app/usr/data/" + last_las_file  + "--out" + destination_tile_file ])

    file_name = os.listdir(destination_tile_file)
        # Causes in case if the file has the interrupted downoad.
    if os.path.isdir( destination_tile_file ): 
        print("uploading the final tile files")
        w3.post_upload(files=file_name)




def laz_to_las_conversion(in_laz, out_las):
    """
    conversion of the other vector file format into las for further pre-processing
    in_laz: user supplied file.
    out_las: resulting transformed file.
    """
    las = laspy.read(in_laz)
    return las.write(laspy.convert(las))



def laz_to_ply_conversion():
    """
    conversion from the vector file format to polygon mesh format 
    note: ( only for testing purposes, as its still not optimized for better rendering putposes)
    
    """


def main(cliargs=None):

    args = argparse.ArgumentParser().parse_args(cliargs)

    ## TODO: setting up choice to run both the point and polygon submission jobs. 
    run_georender_pipeline_point(sys.argv[1:])
    print("now storing the tiled files to the destination web3.storage")
    las_to_tiles_conversion(cliargs["username"])

if __name__ == "__main__":
    main(sys.argv)