
"""georender package script
It crops the specific region from the given geoordinate (from lidarHD) consisting of
large scale shape files of the geographic region.
and then regenerates it into the laz file for reconstruction.
"""

import argparse
import geopandas as gpd
import json
from shapely.geometry import Polygon, Point
from shapely.ops import transform
import os
from subprocess import run
import laspy
import open3d  
from pyproj import Transformer, Proj
from functools import partial
from typing import List

from subprocess import check_call
import shutil


def fetch_shp_file(_filename,username) -> str:
    """
    gets the shape file from the mounted storage as input in order to run the surface reconstruction pipeline
    Parameters:

    :_filename: is the name of the file to be downloaded (with the extension .shp)
    :username: is in which folder the given file is to be stored for maintaining the result separation.
    """
    return (os.getcwd() + "/datas/" + username + "/" + _filename)


def create_bounding_box(latitude_max: int, lattitude_min: int, longitude_max: int, longitude_min: int):
    """
    Create a bounding box which the user selects to crop the given region for surface reconstruction analysis.
    """
    return Polygon([(longitude_min, lattitude_min), (longitude_max, lattitude_min), (longitude_max, latitude_max), (longitude_min, latitude_max), (longitude_min, lattitude_min)])


def creating_3D_cuboid_cropping( MaxP, MinP):
    """
    creates the boundation box based on the UI application cropping specific regions of the model as the bounding box
    """
    
    p1= [MaxP[0], MaxP[1], MinP[2]]
    p2= [MaxP[0],MinP[1],MinP[2]]
    p3= [MinP[0],MaxP[1],MinP[2]]
    p4= MinP
    p5= MaxP
    p6= [MinP[0],MaxP[1],MaxP[2]]
    p7= [MinP[0],MinP[1],MaxP[2]]
    p8= [MaxP[0],MinP[1], MaxP[2]]

    listPoints1 = [p1,p3,p4,p2]
    listPoints2 = [p5,p6,p7,p8]

    print("bounding points from {} to {}".format(listPoints1, listPoints2))    
    

def get_pointcloud_details_polygon(pointargs: List[any], username: str, filename: str, cols_assembly_shapefile: List[str],  epsg_standard: any = ['EPSG:4326', 'EPSG:2154']):
    """
    Parameters
    -----------
    function for cropping the region defined by specific boundation defined by the user on the given shp file with given coordinate standard
    
    pointargs: list of input points defining the boundation ( as lattitude_max, lattitude_min, longitude_max, longitude_min)
    
    ipfs_cid: cid of the corresponding shp file from which the result is to be cropped.
    username: user that has executed the pipeline operation.
    filename: name of the shape file to be accessed.
    cols_assembly_shapefile: its the columns of the assembly shapefile that consist of mapping between the laz filename and coresponding URL
        - used for generating the pipeline for execution.
        
    epsg_standard: defines the coordinate standards for which the given given coordinate values are to be transformed
        - by default the coordinates will be taken for french standard and converted from the normal GPS coordinate standard , but can be defined based on specific regions.
    Returns:
    
    - laz file url which is to be downloaded
    - fname: corresponding file that is to be downloaded
    - dirname: resulting access path to the directory in the given container envionment
    """
    print( "Running tiling with the parameters lat_max={}, lat_min={}, long_max={}, long_min={}, for the user={}".format( pointargs[0], pointargs[1], pointargs[2], pointargs[3], username))

    # this is the docker path of file, will be changed to the w3storagea
    print("reading the shp file")
    
    path = fetch_shp_file(filename, username)
    data = gpd.read_file(path)
    
    polygonRegion = create_bounding_box(pointargs[0], pointargs[1], pointargs[2], pointargs[3])

    ## credits from : https://gis.stackexchange.com/questions/127427/transforming-shapely-polygon-and-multipolygon-objects

    projection = partial(
        transform, Proj(epsg_standard[0]), Proj(epsg_standard[1])
    )
    
    polygonTransform = transform(projection, polygonRegion)
    
    out = data.intersects(polygonTransform)
    res = data.loc[out]
   
    laz_path = res[cols_assembly_shapefile[0]].to_numpy()[0]
    dirname = res[cols_assembly_shapefile[1]].to_numpy()[0]
   
    fname = path + '/' + dirname + ".7z"
    
    print("returning the cooridnates of given polygon boundation{}:{}{}{}".append(pointargs,laz_path, dirname,dirname))

    return laz_path, fname, dirname

def get_tile_details_point(coordX, coordY,username, filename, cols_assembly_shapefile: List[str], epsg_standards: any = ['EPSG:4326', 'EPSG:2154'] ):
    """
    utility function to get the tile information for the given coordinate centrer
    :coordX: X coordinate of the given tile 
    :coordY: Y coordinate of the given tile
    :username: username of the user profile
    :filename: name of the given SHP file format that you want to read. 
    :cols_assembly_shapefile: are the column parameters in the assembly shapefile that is being referenced name index and the URL to download tile for cropping purposes.
    these can be fetched via the analysis.  
    :epsg_standards: coordinate standard initial and the final reference defined as [input cooridnate standard, destination standard]
        - normally set for the input as EPSG:4326 (WGS) and destination as EPSG:2154 (french standard).
    """
    print( "Running with X={}, Y={}".format( coordX, coordY ) )
    ## function  to download file from ipfs to given path in the docker.
    fp = fetch_shp_file(_filename= filename, username= username)
    
    data = gpd.read_file(fp)

    # todo : how to avoid rewriting too much code between bounding box mode and center mode ?
    # todo : Document input format and pyproj conversion
    # see link 1 ( to epsg codes ), link 2 ( to pyproj doc )
    transformer = Transformer.from_crs( epsg_standards[0], epsg_standards[1] )
    
    coordX, coordY = transformer.transform( coordX, coordY )

    center = Point( float(coordX), float(coordY) )

    out = data.intersects(center)
    res = data.loc[out]
    laz_path = res[cols_assembly_shapefile[0]].to_numpy()[0]
    dirname = res[cols_assembly_shapefile[1]].to_numpy()[0]
    fname = dirname + ".7z"

    print("returning the details of corresponding coorindate{},{}:{}{}{}".append(coordX,coordY,laz_path, dirname,dirname))
    
    return laz_path, fname, dirname


def get_tile_details_cuboid():
    """

    """
    pass

def generate_pdal_pipeline( dirname: str,pipeline_template: str, username: str, epsg_srs:str =  "EPSG:4326" ):
    """
    generates the pipeline json (i.e series of transformation operation description) based on the stages of the cropping oepration.
    :dirname: is the directory where the user pipeline files are stored (by default in /username/)
    :pipeline_template: is the reference of the pipeline template is created in the mounted storage.  
    :epsg_srs: is the coordinate standard in which the output pointcloud is represented.
    """
   
    path_datas = os.path.join(__file__ + '/'  + username + "/datas/")     
    os.chdir(path_datas)    
    
    
    # Pdal pipeline is specified by a json
    # basically it's a list of filters which can specify actions to perform
    # each filter is a dict
    # Open template file to get the pipeline struct 
    
    with open( pipeline_template, 'r' ) as file_pipe_in:
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
        las_readers.append({ "type": "readers.las", "filename": fname, "tag": tag, "default_srs":epsg_srs } )
    
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

## Pipeline creation
def run_georender_pipeline_point(cliargs):
    """
    This function the rendering data pipeline of various .laz file and generate the final 3Dtile format.
    coordinateX: lattitude coordinate 
    coordinateY: longitude coordinate 
    username: username of the user profile
    filename: name of the file stored on the given ipfs.
    """
    # Uses geopanda and shapely to intersect gps coord with available laz tiles files
    # Returns corresponding download url and filename    
    parameters = cliargs
    
    filepath = os.getcwd() + "/" + parameters.username
    if not os.path.exists(filepath):
        os.mkdir(filepath)
    os.chdir(filepath)
    
    ## TODO: generate the various 
    
    laz_path, fname, dirname = get_tile_details_point(parameters.Xcoord, parameters.Ycoord, parameters.username,  parameters.filename_template)    
    
    # Causes in case if the file has the interrupted downoad.
    if not os.path.isfile( fname ): 
        check_call( ["wget", "--user-agent=Mozilla/5.0", laz_path])
    
    # Extract it
    
    check_call( ["7z", "-y", "x", fname] ) 
    pipeline_ipfs = parameters.ipfs_template_files
    pipeline_file = generate_pdal_pipeline( dirname, pipeline_ipfs, parameters.username)

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
    
    # shutil.move( 'result.las', '../result.las' )
    print('resulting rendering successfully generated, now uploading the files to ipfs')
    cid = w3.post_upload('result.las')
    return cid

def run_georender_pipeline_polygon(cliargs):
    """
    This function allows to run pipeline for the given bounded location and gives back the rendered 3D tileset
    :coordinates: a list of 4 coordinates [lattitude_max, lattitude_min, longitude_max, longitude_min ]
    ::    
    """
    args = argparse.ArgumentParser(description="runs the georender pipeline based on the given geometric polygon")
    parameters = cliargs

    if cliargs.longitude_range_polygon:
        params_longitude = cliargs.longitude_range_polygon.split(',')

    if cliargs.lattitude_range_polygon:
        params_lattitude = cliargs.lattitude_range_polygon.split(',')

    pointargs = [params_longitude[0], params_lattitude[0], params_longitude[1], params_lattitude[1]]
    
    laz_path, fname, dirname = get_pointcloud_details_polygon(pointargs=pointargs,ipfs_cid=cliargs.ipfs_shp_files, username= cliargs.username)
    filepath = os.getcwd() + parameters.username + "/datas"
    os.mkdir(filepath)
    os.chdir(filepath)
    
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
    
    print('resulting rendering successfully generated, now uploading the files to ipfs')
    w3.post_upload('result.las')
    
def las_to_tiles_conversion(username: str):
    """
    this function runs the dockerised version of the py3Dtiles in order to take in the las file
    generated in the `run_georender_pipeline_point` and convert it to the 3D tiles.
    based on the pipeline generataed for the pdal. 
    
    las_file: corresponds to the las file generated as the result
    """
        
    last_las_file = os.path.abspath("/app/usr/georender/src/datas/" + username + "/result.las")
        
    destination_tile_file = os.getcwd() + '/'+ username + '/3dtiles'
    # run the dockerised version of the py3dtiles application
    check_call( ["docker", "run", "-it", "--rm" ,
            "--mount-type=bind, source= ${}/datas".format(os.getcwd() + "/" + username),
            " --target /app/datas/" +  destination_tile_file   
            + "registry.gitlab.com/oslandia/py3dtiles:142-create-docker-image" , "convert " , "app/usr/datas/" + last_las_file  + "--out" + destination_tile_file ])

    file_name = os.listdir(destination_tile_file)
        # Causes in case if the file has the interrupted downoad.
    if os.path.isdir( destination_tile_file ): 
        print("uploading the final tile files")
        w3.post_upload(files=file_name)




def laz_to_las_conversion(in_laz):
    """
    conversion of the other vector file format into las for further pre-processing
    in_laz: user supplied file.
    out_las: resulting transformed file.
    """
    las = laspy.read(in_laz)
    return las.write(laspy.convert(las))




def main(cliargs):
    ## here the sys.argv selects the operation of the pipeline that you want to generate
    if cliargs.option == "0":
        run_georender_pipeline_point(cliargs=cliargs)
    if cliargs.option  == "1":
        run_georender_pipeline_polygon(cliargs=cliargs)
    if cliargs.option == "2":
        print('TODO')
        #creating_3D_point_cloud(cliargs=cliargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crops the given 3D point cloud for the user")
    # Define parent parser for selecting the point cloud cropping category
    parent_parser = parser.add_subparsers(title="Point Cloud Cropping Category", dest="parent")

    # Define subparser for point cloud cropping
    point_cropping_parser = parent_parser.add_parser(
        "point", help="Crops point cloud based on a specified point"
    )
    point_cropping_parser.add_argument(
        "--Xcoord", type=float, required=False, help="Longitude of the cropping point"
    )
    point_cropping_parser.add_argument(
        "--Ycoord", type=float, required=False, help="Latitude of the cropping point"
    )
    point_cropping_parser.add_argument(
        "--username", type=str, required=True, help="Username of the user running the job"
    )
    point_cropping_parser.add_argument(
        "--filename_template", required=True, help="Name of the template file to be added"
    )

    # Define subparser for polygon-based point cloud cropping
    polygon_cropping_parser = parent_parser.add_parser(
        "polygon", help="Crops point cloud based on a specified polygon"
    )
    polygon_cropping_parser.add_argument(
        "--longitude_range_polygon", type=str, required=False, help="Range of longitudes for cropping"
    )
    polygon_cropping_parser.add_argument(
        "--lattitude_range_polygon", type=str, required=False, help="Range of latitudes for cropping"
    )
    polygon_cropping_parser.add_argument(
        "--username", type=str, required=True, help="Username of the user running the job"
    )
    polygon_cropping_parser.add_argument(
        "--filename_template", required=True, help="Name of the template file to be added"
    )

    # Parse the arguments
    args = parser.parse_args()

    if args.parent == "point":
        # Execute point-based cropping
        run_georender_pipeline_point(args)
    elif args.parent == "polygon":
        # Execute polygon-based cropping
        run_georender_pipeline_polygon(args)
    elif args.parent == "cuboid":
        print("currently not implemented")
    else:
        print("Invalid cropping category. Please choose 'point', 'polygon' or  'cuboid'")
