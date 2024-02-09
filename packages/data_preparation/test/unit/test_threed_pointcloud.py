import pytest
import open3d as o3d
import sys
import os

sys.path.append("../")
from data_preparation.threed_pointcloud import PointCloud3D


def test_reading_point_cloud():
    dataset_test = o3d.data.PCDPointCloud()
    dataset_test_path = dataset_test.path
    threed_object = PointCloud3D(dataset_test_path)
    print("example nature of the pointcloud data:" + str(threed_object.pcd))
    assert threed_object.pcd is not None
    
def test_create_dataset_model():
    path_laz_example_url = "https://bafybeic7vjtoffchve57v2j3p32v3nuflhtey37bii3v4j6mwzyfowfc7e.ipfs.w3s.link/07ED4844.las"
    test_dataset_path = "./datas/bunny.pcd" ## taken from pcl example library and stored in the local file : https://github.com/PointCloudLibrary/pcl/blob/master/test/bunny.pcd
    dataset_obj = PointCloud3D(test_dataset_path)
    dataset_obj.create_dataset_model(path_laz_example_url)
    assert dataset_obj.stored_model is not None
    

demo_test: o3d.data = o3d.data.PCDPointCloud()

    
def test_downsample_pcd(demo_test: o3d.data = o3d.data.PCDPointCloud()):
    voxel_size = 0.02
    demo_test.downsample_pcd(voxel_size)
    
    