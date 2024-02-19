"""
script that uses the python bindings of nerfstudio and colmap in order to:
- Pull and parse the images for the correction on colmap.
- running the colmap operations for the image recalibration along with other operation.
CREDITS: the code here is taken from the sdfstudio process_data:  https://github.com/autonomousvision/sdfstudio/blob/master/scripts/process_data.py#L33
"""
from data_preparation.cameras.colmap.scripts.python.read_write_model import read_model

from nerfstudio.process_data import (
    colmap_utils, hloc_utils, process_data_utils
)

import sys
import plotly.graph_objs as go

from nerfstudio.utils import install_checks

import matplotlib.pyplot as plt
import cv2
from subprocess import check_call
import os
from PIL import Image, ExifTags
import pathlib
from rich.console import Console
from typing_extensions import Annotated, Literal
from dataclasses import dataclass
import json
from collections import OrderedDict
import torch
import numpy as np

@dataclass
class ColmapDataParsing():
    """
    filepath: is the current folder path for the given images / videos
    type: 0 for the image and 1 for photos that are decked.
    """
    datafolder:pathlib.Path ## stores the path of the video / or the initial version of the images from the user.
    output_dir:pathlib.Path ## stores the output images (that are  recalibrated and the generated point cloud from).
    def __init__(self,filepath, output_dir):
        self.datafolder = filepath
        self.output_dir = output_dir
        
    def convert_video_to_photo(self, downsampling_rate):
        """
        using opencv in order to slicing the images from the video.
        downsampling_rate defines the intervals (in sec) that are to be taken in order to slice images.
        """
        clock = 0
        frameRate = 1/downsampling_rate
        count = 1
        ## for transferring to another arhitecture.
        os.chdir(self.filepath + "/images_raw")
        success = self.fetch_frame(downsampling_rate,count)
        while success:
            count +=1
            sec += frameRate
            sec = round(sec,2)
            success = self.fetch_frame(downsampling_rate, count)
    
    def get_image_metadata(imagepath:str):
        """
        fetches the metadata from the frames in order to get the geolocation of the given frame and fetch the corresponding geolocal information
        NOTE: this needs to be enabled by the mobile or device that is capturing the image/video in order to fetch the corresponding GPS information.
        """
        img = Image.open(imagepath)
        exif = {
            ExifTags.TAGS[k]: v
            for k,v in img.getexif().items()
            if k in ExifTags.TAGS
                }
        return exif
    def colmap_transformation(self):
        ## first defining the various path of image operation
        mvs_path = self.output_dir / "mvs"
        database_path = self.output_dir / "database.db"
 
        check_call(["colmap", 
                    "feature_extractor", "--database_path=${database_path}", 
                    "-image_path=${database_path}/images_raw",
                    "--ImageReader.camera_model=SIMPLE_RADIAL", ## https://colmap.github.io/cameras.html#camera-models
                    "--ImageReader.single_camera=true",
                    "--SiftExtraction.use_gpu=true",
                    "--SiftExtraction.num_threads=32"
                    ])
        
        check_call([
                    "colmap",
                    "sequential_matcher",
                    "--database_path=database.db",
                    "--SiftMatching.use_gpu=true"            
                    ])

        os.mkdir(self.filepath + "/sparse")
        
        check_call([
        "colmap", "mapper" ,
        "--database_path=${database_path}",
        "--image_path=${self.datapath}/images_raw",
        "--output_path=${self.datapath}/sparse",
        ])
        
        check_call(['cp', os.path.join(self.datafolder, 'sparse/0/*.bin'), os.path.join(self.datafolder, 'sparse')])
                
        # Loop through all subdirectories in 'sparse'
        for path in os.listdir(os.path.join(self.datafolder, 'sparse')):
            if not os.path.isdir(os.path.join(self.datafolder, 'sparse', path)):
                continue

            # Get the name of the subdirectory
            m = os.path.basename(path)

            # Check if the subdirectory name is not "0"
            if m != '0':
                # Perform model merging
                check_call(['colmap', 'model_merger', '--input_path1', os.path.join(self.datafolder, 'sparse'), '--input_path2', os.path.join(self.datafolder, 'sparse', m), '--output_path', os.path.join(self.datafolder, 'sparse')])

                # Perform bundle adjustment
                check_call(['colmap', 'bundle_adjuster', '--input_path', os.path.join(self.datafolder, 'sparse'), '--output_path', os.path.join(self.datafolder, 'sparse')])

        # Perform image undistortion
        check_call(['colmap', 'image_undistorter', '--image_path', os.path.join(self.datafolder, 'images_raw'), '--input_path', os.path.join(self.datafolder, 'sparse'), '--output_path', os.path.join(self.datafolder, 'undistorted_images'), '--output_type', 'COLMAP'])    

    def analyze_colmap_images(self,camera_bin_path, transform_file, camera_depth, coordinates_adjust = ["0", "0", "0", "1"] ):
        """
        this function lets user to:
        - read the generated transforms.json and inspects the data.
        - lets user to allign the bounding sphere and orientation values of the camera for the specific frames that're missaligned
        - and then registers the new parameter in the transforms.json
        - gets the result of the images as the plotly figure
        - then its stores the transform.json and thus can be used in training stage. 
        ---------
        camera_bin_path: is the path corresponding to the camera.bin file generated after the reconstruction pipeline
        transform_file is the path of the transforms.json file corresponding to the given path.
        coordinates_adjust: is the array  that consist of the following values : length of viewbox around (x, y, z) and the scale of viewing the values
        Credits to the nvidia neuralangelo collab notebook explaining the process
        """
        
        camera, imgs, points_3D = read_model(path=camera_bin_path, ext=".bin")
        
        assert imgs is not None
        images = OrderedDict(sorted(imgs.items()))
        ## now representing the images into the tensors as Q and T description in eigen format:
        qvecs = torch.from_numpy(np.stack([image.qvec for image in images.values()]))
        tvecs = torch.from_numpy(np.stack([image.tvec for image in images.values()]))
        Rs = camera.quaternion.q_to_R(qvecs)
        poses = torch.cat([Rs, tvecs[..., None]], dim=-1)  # [N,3,4]
        print(f"# images: {len(poses)}")
        # Get the sparse 3D points and the colors.
        xyzs = torch.from_numpy(np.stack([point.xyz for point in points_3D.values()]))
        rgbs = np.stack([point.rgb for point in points_3D.values()])
        rgbs_int32 = (rgbs[:, 0] * 2**16 + rgbs[:, 1] * 2**8 + rgbs[:, 2]).astype(np.uint32)
        print(f"# points: {len(xyzs)}")

        transform_fname = transform_file
        with open(transform_fname) as file:
            meta = json.load(file)
        center = meta["sphere_center"]
        radius = meta["sphere_radius"]
        
        ## now adjusting the parameters in order to make bounding sphere fit corresponding to the region of interest 
        ## approximatively wrt each of the images these coordinates should be fitting .
        
        center += np.array([coordinates_adjust[0],coordinates_adjust[1],coordinates_adjust[2]])
        radius *= coordinates_adjust[3]
        
        ## creating some random points for determining thr nature of the mis-alignment
        sphere_points = np.random.randn(100000, 3)
        sphere_points = sphere_points / np.linalg.norm(sphere_points, axis=-1, keepdims=True)
        sphere_points = sphere_points * radius + center
        
        vis_depth = camera_depth 
        colors = rgbs / 255.0
        ## plotly values
        x, y, z = *xyzs.T,
        sphere_x, sphere_y, sphere_z = *sphere_points.T,
        sphere_colors = ["#4488ff"] * len(sphere_points)
        traces_poses = self.plotly_visualize_pose(poses, vis_depth=vis_depth, xyz_length=0.02, center_size=0.01, xyz_width=0.005, mesh_opacity=0.05)
        trace_points = go.Scatter3d(x=x, y=y, z=z, mode="markers", marker=dict(size=1, color=colors, opacity=1), hoverinfo="skip")
        trace_sphere = go.Scatter3d(x=sphere_x, y=sphere_y, z=sphere_z, mode="markers", marker=dict(size=0.5, color=sphere_colors, opacity=0.7), hoverinfo="skip")
        traces_all = traces_poses + [trace_points, trace_sphere]
        layout = go.Layout(scene=dict(xaxis=dict(showspikes=False, backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(0,0,0,0.1)"),
                                    yaxis=dict(showspikes=False, backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(0,0,0,0.1)"),
                                    zaxis=dict(showspikes=False, backgroundcolor="rgba(0,0,0,0)", gridcolor="rgba(0,0,0,0.1)"),
                                    xaxis_title="X", yaxis_title="Y", zaxis_title="Z", dragmode="orbit",
                                    aspectratio=dict(x=1, y=1, z=1), aspectmode="data"), height=800)
        fig = go.Figure(data=traces_all, layout=layout)
        fig.show()
        
        
    ## other extra functions that are fetched from the neuralangelo.nerf libraries 
    def plotly_vizualize_pose(self,poses,vis_depth,xyz_length, center_size,xyz_width=5, mesh_opacity=0.05):
        """
        function for generating the vizualization poses for the given user
        poses: a tensor defining the reltive allignment of the given structure to be reconstructed.
        vis_depth: is the depth settings of the camera (in meters)
        xyz_length: is the relative box lengthwise in the various directions.
        
        """
        def get_xyz_indicators(pose, length=0.1):
            xyz = torch.eye(4, 3)[None] * length
            xyz = self.transform_pts(xyz, pose)
            return xyz
        
        def get_camera_mesh(pose, depth=1):
            vertices = torch.tensor([[-0.5, -0.5, 1],
                                    [0.5, -0.5, 1],
                                    [0.5, 0.5, 1],
                                    [-0.5, 0.5, 1],
                                    [0, 0, 0]]) * depth  # [6,3]
            faces = torch.tensor([[0, 1, 2],
                                [0, 2, 3],
                                [0, 1, 4],
                                [1, 2, 4],
                                [2, 3, 4],
                                [3, 0, 4]])  # [6,3]
            vertices = self.transform_pts(vertices[None], pose)  # [N,6,3]
            wireframe = vertices[:, [0, 1, 2, 3, 0, 4, 1, 2, 4, 3]]  # [N,10,3]
            return vertices, faces, wireframe
        def merge_meshes(vertices, faces):
            mesh_N, vertex_N = vertices.shape[:2]
            faces_merged = torch.cat([faces + i * vertex_N for i in range(mesh_N)], dim=0)
            vertices_merged = vertices.view(-1, vertices.shape[-1])
            return vertices_merged, faces_merged
        
        def merge_wireframes_plotly(wireframe):
            wf_dummy = wireframe[:, :1] * np.nan
            wireframe_merged = torch.cat([wireframe, wf_dummy], dim=1).view(-1, 3)
            return wireframe_merged
        
        def merge_xyz_indicators_plotly(xyz):  # [N,4,3]
            xyz = xyz[:, [[-1, 0], [-1, 1], [-1, 2]]]  # [N,3,2,3]
            xyz_0, xyz_1 = xyz.unbind(dim=2)  # [N,3,3]
            xyz_dummy = xyz_0 * np.nan
            xyz_merged = torch.stack([xyz_0, xyz_1, xyz_dummy], dim=2)  # [N,3,3,3]
            xyz_merged = xyz_merged.view(-1, 3)
            return xyz_merged


        N = len(poses)    
        centers_cam = torch.zeros(N, 1, 3)
        centers_world = self.transform_pts(centers_cam, poses)
        centers_world = centers_world[:, 0]
        # Get the camera wireframes.
        vertices, faces, wireframe = get_camera_mesh(poses, depth=vis_depth)
        xyz = get_xyz_indicators(poses, length=xyz_length)
        vertices_merged, faces_merged = merge_meshes(vertices, faces)
        wireframe_merged = merge_wireframes_plotly(wireframe)
        
        xyz_merged = merge_xyz_indicators_plotly(xyz)
        # Break up (x,y,z) coordinates.
        wireframe_x, wireframe_y, wireframe_z = wireframe_merged.unbind(dim=-1)
        xyz_x, xyz_y, xyz_z = xyz_merged.unbind(dim=-1)
        centers_x, centers_y, centers_z = centers_world.unbind(dim=-1)
        vertices_x, vertices_y, vertices_z = vertices_merged.unbind(dim=-1)
        # Set the color map for the camera trajectory and the xyz indicators.
        color_map = plt.get_cmap("gist_rainbow")
        center_color = []
        faces_merged_color = []
        wireframe_color = []
        xyz_color = []
        x_color, y_color, z_color = *np.eye(3).T,
        for i in range(N):
            # Set the camera pose colors (with a smooth gradient color map).
            r, g, b, _ = color_map(i / (N - 1))
            rgb = np.array([r, g, b]) * 0.8
            wireframe_color += [rgb] * 11
            center_color += [rgb]
            faces_merged_color += [rgb] * 6
            xyz_color += [x_color] * 3 + [y_color] * 3 + [z_color] * 3
        # Plot in plotly.
        plotly_traces = [
            go.Scatter3d(x=wireframe_x, y=wireframe_y, z=wireframe_z, mode="lines",
                        line=dict(color=wireframe_color, width=1)),
            go.Scatter3d(x=xyz_x, y=xyz_y, z=xyz_z, mode="lines", line=dict(color=xyz_color, width=xyz_width)),
            go.Scatter3d(x=centers_x, y=centers_y, z=centers_z, mode="markers",
                        marker=dict(color=center_color, size=center_size, opacity=1)),
            go.Mesh3d(x=vertices_x, y=vertices_y, z=vertices_z,
                    i=[f[0] for f in faces_merged], j=[f[1] for f in faces_merged], k=[f[2] for f in faces_merged],
                    facecolor=faces_merged_color, opacity=mesh_opacity),
        ]
        return plotly_traces
                            
    def homogenise_coord(X):    
        return torch.cat([X,torch.ones_like(X[..., :1])], dim=-1)
    
    def transform_pts(self,X,pose: torch.tensor):
        homogenise_coord = self.homogenise_coord(X)
        return homogenise_coord @ pose.transform(-1,-2) 

presentation_console = Console(width=120)

"""
    class to parse the video / image of the clients to nerfstudio for image reallignment.
    borrowed from the sdfstudio implementation here: https://github.com/autonomousvision/sdfstudio/blob/master/scripts/process_data.py
    this also allows the user to choose the category of SFM tool either colmap or hloc in order to get pre-alligned image in order to be then processed and trained by the reconstruction/ module 
"""

@dataclass
class NerfStudioCameraUtils():        
    def processing_images(self, 
    path: pathlib.Path,
    output_dir: pathlib.Path,
    num_frames_target: int, ## defines the nulber of frames that are to be sampled per second.Target number of frames to use for the dataset, results may not be exact.
    camera_type: Literal["perspective", "fisheye"] = "perspective",
    sfm_tool: Literal["any", "colmap", "hloc"] = "any",
     #  """Type of features to extract from the images "using colmap / hloc". these are described  here: https://github.com/cvg/sfm-disambiguation-colmap#1-correspondence"""
    feature_type: Literal[
        "any",
        "sift",
        "superpoint",
        "superpoint_aachen",
        "superpoint_max",
        "superpoint_inloc",
        "r2d2",
        "d2net-ss",
        "sosnet",
        "disk",
    ] = "any",


    
    matcher_type: Literal[
        "any", "NN", "superglue", "superglue-fast", "NN-superpoint", "NN-ratio", "NN-mutual", "adalam"
    ] = "any",

    #"""If True, skips COLMAP and generates transforms.json if possible."""
    colmap_cmd: str = "colmap",
    # """How to call the COLMAP executable."""
    gpu: bool = True,
    #"""If True, use GPU."""
    verbose: bool = False,          
        ):
        install_checks.check_colmap_installed()
        install_checks.check_ffmpeg_installed()

        output_dir.mkdir(parents=True, exist_ok=True)
        image_dir = output_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        
        image_data_log = []
        ## transferring the files to the output dir
        num_frames = process_data_utils.copy_images(path, image_dir=image_dir, verbose=verbose)
        image_data_log.append(f"Starting with {num_frames} images")

        # Downscale images
        image_data_log.append(process_data_utils.downscale_images(image_dir, self.num_downscales, verbose=self.verbose))


        # Run COLMAP
        colmap_dir = self.output_dir / "colmap"
        if not self.skip_colmap:
            colmap_dir.mkdir(parents=True, exist_ok=True)
            (sfm_tool, feature_type, matcher_type) = process_data_utils.find_tool_feature_matcher_combination(self.sfm_tool, self.feature_type, self.matcher_type )
            
            ## now selection of the appropriate tool by the nerfstudio to automatically generate the transforms.json
            
            if sfm_tool == "colmap":
                colmap_utils.run_colmap(
                    image_dir=image_dir,
                    colmap_dir= colmap_dir,
                    camera_model= process_data_utils.process_data_utils.CAMERA_MODELS[self.camera_type],
                    gpu=self.gpu,
                    verbose= self.verbose,
                    matching_method=self.matching_method,
                    colmap_cmd=self.colmap_cmd                    
                )
            
            elif sfm_tool == "hloc":
                hloc_utils.run_hloc(
                    image_dir=image_dir,
                    colmap_dir=colmap_dir,
                    camera_model=process_data_utils.process_data_utils.CAMERA_MODELS[self.camera_type],
                    verbose=self.verbose,
                    matching_method=self.matching_method,
                    feature_type=feature_type,
                    matcher_type=matcher_type,
                )
            else:
                presentation_console.log("[bold red]Invalid combination of the sfm tools w/ features found, exiting")
                sys.exit(1)
        
        ## generate the transforms.json
        ## TODO: integrate function from storage in order to fetch the output of transforms.json to the user details
        if (colmap_dir / "sparse" / "0" / "cameras.bin").exists():
            with presentation_console.status("[bold yellow]Saving results to transforms.json", spinner="balloon"):
                num_matched_frames = colmap_utils.colmap_to_json(
                    cameras_path=colmap_dir / "sparse" / "0" / "cameras.bin",
                    images_path=colmap_dir / "sparse" / "0" / "images.bin",
                    output_dir=self.output_dir,
                    camera_model=process_data_utils.process_data_utils.CAMERA_MODELS[self.camera_type],
                )
                image_data_log.append(f"Colmap matched {num_matched_frames} images")
                
                with open("transform_" + self.path + ".json", "wb+") as fp:
                    json.dump(fp=fp,obj=num_matched_frames)
                
            image_data_log.append(colmap_utils.get_matching_summary(num_frames, num_matched_frames))
            
        else:
            presentation_console.log("error while generating the transforms.json, retry with other parameters")
        
        presentation_console.rule("Generation completed")

        for output_line in image_data_log:
            presentation_console.print(output_line, justify="center")
        presentation_console.rule("completed")


    def process_video(
        data: pathlib.Path,
        output_dir: pathlib.Path, #"""Path to the output directory."""
    num_frames_target: int = 300,
    #"""Target number of frames to use for the dataset, results may not be exact."""
    camera_type: Literal["perspective", "fisheye"] = "perspective",
    #"""Camera model to use."""
    matching_method: Literal["exhaustive", "sequential", "vocab_tree"] = "vocab_tree",
    # """Feature matching method to use. Vocab tree is recommended for a balance of speed and
    #     accuracy. Exhaustive is slower but more accurate. Sequential is faster but should only be used for videos."""
    sfm_tool: Literal["any", "colmap", "hloc"] = "any",
    # """Structure from motion tool to use. Colmap will use sift features, hloc can use many modern methods
    #    such as superpoint features and superglue matcher"""
    feature_type: Literal[
        "any",
        "sift",
        "superpoint",
        "superpoint_aachen",
        "superpoint_max",
        "superpoint_inloc",
        "r2d2",
        "d2net-ss",
        "sosnet",
        "disk",
    ] = "any",
    #"""Type of feature to use."""
    matcher_type: Literal[
        "any", "NN", "superglue", "superglue-fast", "NN-superpoint", "NN-ratio", "NN-mutual", "adalam"
    ] = "any",
    #"""Matching algorithm."""
    num_downscales: int = 3,
    # """Number of times to downscale the images. Downscales by 2 each time. For example a value of 3
    #     will downscale the images by 2x, 4x, and 8x."""
    skip_colmap: bool = False,
    # """If True, skips COLMAP and generates transforms.json if possible."""
    colmap_cmd: str = "colmap",
    # """How to call the COLMAP executable."""
    gpu: bool = True,
    # """If True, use GPU."""
    verbose: bool = False
    # """If True, print extra logging."""):
    #     """
    #     function to process the videos for image realignment and reconstruction
    #     """   
    ):
        install_checks.check_ffmpeg_installed()
        install_checks.check_colmap_installed()

        output_dir.mkdir(parents=True, exist_ok=True)
        image_dir = output_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)

        # Convert video to images
        summary_log, num_extracted_frames = process_data_utils.convert_video_to_images(
            data, image_dir=image_dir, num_frames_target=num_frames_target, verbose=verbose
        )

        # Downscale images
        summary_log.append(process_data_utils.downscale_images(image_dir, num_downscales, verbose=verbose))

        # Run Colmap
        colmap_dir = output_dir / "colmap"
        if not skip_colmap:
            colmap_dir.mkdir(parents=True, exist_ok=True)

            (sfm_tool, feature_type, matcher_type) = process_data_utils.find_tool_feature_matcher_combination(
                sfm_tool, feature_type, matcher_type
            )

            if sfm_tool == "colmap":
                colmap_utils.run_colmap(
                    image_dir=image_dir,
                    colmap_dir=colmap_dir,
                    camera_model=process_data_utils.CAMERA_MODELS[camera_type],
                    gpu=gpu,
                    verbose=verbose,
                    matching_method=matching_method,
                    colmap_cmd=colmap_cmd,
                )
            elif sfm_tool == "hloc":
                hloc_utils.run_hloc(
                    image_dir=image_dir,
                    colmap_dir=colmap_dir,
                    camera_model=process_data_utils.CAMERA_MODELS[camera_type],
                    verbose=verbose,
                    matching_method=matching_method,
                    feature_type=feature_type,
                    matcher_type=matcher_type,
                )
            else:
                presentation_console.log("[bold red]Invalid combination of sfm_tool, feature_type, and matcher_type, exiting")
                sys.exit(1)

        # Save transforms.json
        if (colmap_dir / "sparse" / "0" / "cameras.bin").exists():
            with presentation_console.status("[bold yellow]Saving results to transforms.json", spinner="balloon"):
                num_matched_frames = colmap_utils.colmap_to_json(
                    cameras_path=colmap_dir / "sparse" / "0" / "cameras.bin",
                    images_path=colmap_dir / "sparse" / "0" / "images.bin",
                    output_dir=output_dir,
                    camera_model=process_data_utils.CAMERA_MODELS[camera_type],
                )
                summary_log.append(f"Colmap matched {num_matched_frames} images")
            summary_log.append(colmap_utils.get_matching_summary(num_extracted_frames, num_matched_frames))
        else:
            presentation_console.log("[bold yellow]Warning: could not find existing COLMAP results. Not generating transforms.json")

        presentation_console.rule("[bold green]:tada: :tada: :tada: All DONE :tada: :tada: :tada:")

        for summary in summary_log:
            presentation_console.print(summary, justify="center")
        presentation_console.rule()
