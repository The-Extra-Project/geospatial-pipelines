"""
This package script is for cropping and operation the the  point clouds generated from terestrial datasets
"""

import openai
import argparse
import laspy    
import json
from shapely.geometry import Polygon, Point
from shapely.ops import transform
import os
import open3d as o3d
import laspy
from pyproj import Transformer, Proj
from functools import partial
from typing import List
from shapely import LineString
from subprocess import check_call
import shutil
import laspy
import shapefile
from llm.pipeline_generation import PDAL_json_generation_template
import pycrs
import pylas
class CroppingUtilsLas():
    """   
    This package reads the las files from terrestrial scans, and then allows user to fetch any section of the geocoordinate region 
    from the shp file and fetches the output as las file
    """
    def __init__(self,_shp_file,_pipeline_file, username, _epsg_standard):
        """
        _shp_file: is the shape file that you want to parse.
        username: identity of the user which has commanded the Cropping job.
        cols_assembly_shapefile: its the columns of the assembly shapefile that consist of mapping between the laz filename and coresponding URL        
        epsg_standard: defines the coordinate standards for which the given given coordinate values are to be transformed
            - by default the coordinates will be taken for french standard and converted from the normal GPS coordinate standard , but can be defined based on specific regions.
        _pipeline_file: its the pipeline file that is taken as the input.
        """
        
        self.shp_file = _shp_file
        self.shp_reader = shapefile.Reader(self.shp_file)
        ## credits to the pyshp script to get the records: https://github.com/GeospatialPython/pyshp/blob/master/README.md#reading-records
        self.cols_assembly_shapefile = [fields[0] for fields in self.shp_reader.fields[1:]] 
        self.epsg_standard = _epsg_standard
        self.openAIObject = PDAL_json_generation_template()
        self.username = username
        self.pipeline_file = _pipeline_file
        
    def shp_file_path(self) -> str:
        """
        fetches the abspath of the shp file that is referenced during instantiation. this file is stored in the data/ 
        folder everytime when the user creates the instance of bacalhau from the given IPFS file.
        """
        return os.path.abspath(os.path.join('.', "data",self.shp_file ))

    def create_bounding_box(latitude_max: int, lattitude_min: int, longitude_max: int, longitude_min: int):
        """
        Create a bounding box which the user selects to crop the given region for surface reconstruction analysis.
        """
        return Polygon([(longitude_min, lattitude_min), (longitude_max, lattitude_min), (longitude_max, latitude_max), (longitude_min, latitude_max), (longitude_min, lattitude_min)])
    

    def create_bounding_box(latitude_max: int, lattitude_min: int, longitude_max: int, longitude_min: int):
        """
        Create a bounding box which the user selects to crop the given region for surface reconstruction analysis.
        """
        return Polygon([(longitude_min, lattitude_min), (longitude_max, lattitude_min), (longitude_max, latitude_max), (longitude_min, latitude_max), (longitude_min, lattitude_min)])

    def get_pointcloud_details_polygon(self, pointargs: List[any]):
        """
        Parameters
        -----------
        function for cropping the region defined by specific boundation defined by the user on the given shp file with coordinate standard
        pointargs: list of input points defining the boundation ( as lattitude_max, lattitude_min, longitude_max, longitude_min)
        Returns:
        
        - laz file url which is to be downloaded
        - fname: corresponding file that is to be downloaded
        - dirname: resulting access path to the directory in the given container envionment
        """
        print( "Running tiling with the parameters lat_max={}, lat_min={}, long_max={}, long_min={}, for the user={}".format( pointargs[0], pointargs[1], pointargs[2], pointargs[3]))

    # this is the docker path of file, will be changed to the w3storagea
        print("reading the shp file")
        path = self.get_shp_file_path()
        data = laspy.read_file(path)
    
        polygonRegion = self.create_bounding_box(pointargs[0], pointargs[1], pointargs[2], pointargs[3])

        ## credits from : https://gis.stackexchange.com/questions/127427/transforming-shapely-polygon-and-multipolygon-objects

        projection = partial(
            Transformer.transform, Proj(self.epsg_standard[0]), Proj(self.epsg_standard[1])
        )
    
        polygonTransform = Transformer.transform(projection, polygonRegion)
    
        out = data.intersects(polygonTransform)
        res = data.loc[out]
    
        laz_path = res[self.cols_assembly_shapefile[0]].to_numpy()[0]
        dirname = res[self.cols_assembly_shapefile[1]].to_numpy()[0]
    
        fname = path + '/' + dirname + ".7z"
        
        print("generating the resuls of the given pointcloud foundation {}:{}{}".append(pointargs,laz_path, dirname))

        return laz_path, fname, dirname

    def get_tile_details_point(self,coordX, coordY):
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
        fp = self.get_shp_file_path()
        
        data = laspy.read(fp)

        transformer = Transformer.from_crs( self.epsg_standards[0], self.epsg_standards[1] )
        
        coordX, coordY = transformer.transform( coordX, coordY )

        center = Point( float(coordX), float(coordY) )
        out = data.intersects(center)
        res = data.loc[out]
        laz_path = res[self.cols_assembly_shapefile[0]].to_numpy()[0]
        dirname = res[self.cols_assembly_shapefile[1]].to_numpy()[0]
        fname = dirname + ".7z"

        print("returning the details of corresponding coorindate{},{}:{}{}{}".append(coordX,coordY,laz_path, dirname,dirname))
        
        return laz_path, fname, dirname


    def generate_pdal_pipeline(self,pipeline_template: str, epsg_srs:str =  "EPSG:4326" ):
        """
        generates the pipeline json (i.e series of transformation operation description) based on the stages of the cropping oepration.
        :dirname: is the directory where the user pipeline files are stored (by default in /username/)
        :pipeline_template: is the reference of the pipeline template is created in the mounted storage.  
        :epsg_srs: is the coordinate standard in which the output pointcloud is represented.
        """
    
        path_datas = os.path.join(__file__  + "/datas/")     
        os.chdir(path_datas)    
        
        # Pdal pipeline is specified by a json generated by openAI
        # basically it's a list of filters which can specify actions to perform
        # each filter is a dict
        # Open template file to get the pipeline struct 
        try:
            self.openAIObject.define_assistant_parameter("pipeline")
        
            self.openAIObject.creating_message_thread(
                "I want you to use the template file of pattern" + pipeline_template + " and based on the cropping transformation" + pipeline_template + " containing the PDAL pipeline conversion" ,
                )   
            with open( pipeline_template, 'r' ) as file_pipe_in:
                file_str = file_pipe_in.read()
        
            pdal_pipeline = json.loads( file_str )
        except openai._exceptions.APIError as e:
            print("in function generate_pdal_pipeline:" + str(e))
        return pdal_pipeline 

## Pipeline creation
    def run_georender_pipeline_point(self,coordinateX,coordinateY ):
        """
        This function the rendering data pipeline of various .laz file and generate the final 3Dtile format.
        coordinateX: lattitude coordinate 
        coordinateY: longitude coordinate 
        username: username of the user profile
        filename: name of the file stored on the given ipfs.
        """
        parameters = [coordinateX,coordinateY]
        
        filepath = os.getcwd() + "/"
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        os.chdir(filepath)
        ## TODO: generate the point based pipeline 
        
        
        laz_path, fname, dirname = self.get_tile_details_point(coordX=coordinateX,coordY=coordinateY)    
        
        # Causes in case if the file has the interrupted downoad.
        if not os.path.isfile( fname ): 
            check_call( ["wget", "--user-agent=Mozilla/5.0 ", laz_path])
        
        # Extract it
        
        check_call( ["7z", "-y", "x", fname] ) 
        pipeline_ipfs = parameters.ipfs_template_files
        pipeline_file = self.generate_pdal_pipeline( dirname, pipeline_ipfs, parameters.username)

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
        check_call(["pdal", "pipeline",pipeline_file])
        
        # shutil.move( 'result.las', '../result.las' )
        print('resulting rendering successfully generated, now uploading the files to ipfs')
        return os.path.abspath(pipeline_file)

def run_georender_pipeline_polygon(self,coordinates: list(str), filepath, pointargs):
    """
    This function allows to run pipeline for the given bounded location and gives back the rendered 3D tileset
    :coordinates: a list of 4 coordinates [lattitude_max, lattitude_min, longitude_max, longitude_min ].
    filepath: path of the shp file.
    
    """
    
    laz_path, fname, dirname = self.get_pointcloud_details_polygon(pointargs=pointargs)
    filepath = os.getcwd() + self.username + "/datas"
    os.mkdir(filepath)
    os.chdir(filepath)
    
    # Causes in case if the file has the interrupted downoad.
    if not os.path.isfile( fname ): 
        check_call( ["wget", "--user-agent=Mozilla/5.0", laz_path])
    
    
    # Extract it
    check_call( ["7z", "-y", "x", fname] ) 
    pipeline_ipfs = self.ipfs_cid
    self.generate_pdal_pipeline( dirname, pipeline_ipfs, self.username )
    # run pdal pipeline with the generated json :
    
    os.chdir( dirname )
    ## here the laz filename is written based on the various categories of the pointclouds for the given region        
    for laz_fname in os.listdir( '.' ):            
        f = open( laz_fname, 'rb+' )
        f.seek( 6 )
        f.write( bytes( [17, 0, 0, 0] ) )
        f.close()
    ## now running the command to generate the 3d tile from the stored pipeline 
    pipeline_template = self.pipeline_file 
    check_call( ["pdal", "pipeline",pipeline_template] )
    
    print('resulting rendering successfully generated, now uploading the files to ipfs')

    def fetch_classification_laz(coordinates,laz_fname):
        """
        function that takes in the
        coordinates (2 in case of point cropping or 4 in case of the polygon cropping) 
        
        and then defines the categorisation
        for the given region boundation.
        
        This checks for the shp and corresponding proj file to define the parameters.
        
        """
        ## checks for the nature of the laz_classification files:
        if len(coordinates) == 2:
            ## here the laz filename is written based on the various categories of the pointclouds for the given region        
            f = open( laz_fname, 'rb+' )
            lasfile = pylas.read('input.laz')
            crs = lasfile.header
            shape_projected = shapefile
            # f.seek( 6 )
            # f.write( bytes( [17, 0, 0, 0] ) )
            # f.close()
