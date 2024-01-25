"""
script that uses the python bindings of nerfstudio and colmap in order to:
- Pull and parse the images for the correction on colmap.
- running the colmap operations for the image recalibration along with other operation.

CREDITS: the code here is taken from the sdfstudio process_data:  https://github.com/autonomousvision/sdfstudio/blob/master/scripts/process_data.py#L33
"""




from nerfstudio.process_data import (
    colmap_utils, hloc_utils, polycam_utils, record3d_utils, process_data_utils
)
import sys
from nerfstudio.utils import install_checks
#import pycolmap
import cv2
from subprocess import check_call
import os
from PIL import Image, ExifTags
import pathlib
from rich.console import Console
from typing_extensions import Annotated, Literal
from dataclasses import dataclass
import json


@dataclass
class ColmapDataParsing():
    """
    filepath: is the ciurrent folder path for the given images / videos
    type: 0 for the image and 1 for photos that are decked.
    """
    datafolder:pathlib.Path
    datatype:int ## whether its an video (0) or an image(1)
    output_dir:pathlib.Path ## stores the output images (that are recalibrated).
    def __init__(self,filepath, type):
        datafolder = filepath

    def fetch_frame(self,downsampling_rate, count):  
        video = cv2.VideoCapture(datafolder)
        video.set(cv2.CAP_PROP_POS_MSEC, downsampling_rate * 1000)
        frame, image = video.read()
        if frame:
            cv2.imwrite(os.absself.filepath+"filepath_ds_" + downsampling_rate + str(count) + ".jpg",image)
        return frame

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
    def get_image_metadata(imagepath):
        """
        fetches the metadata from the frames in order to get the geolocation of the given frame and fetch the corresponding geolocal information
        NOTE: this needs to be enabled by the mobile or device that is capturing the image/video in order to fetch the corresponding GPS information.
        """
        img = Image.open("test_image_1.JPG")
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

    def analyze_colmap_images():
        """
        this function lets user to:
        - read the generated transforms.json and the associated alligned images.
        - lets user to allign the bounding sphere and orientation values of the camera for the specific frames that're missaligned
        - and then registers the new parameter in the transforms.json in order to then be passed to the training stage. 
        """
        
        pass




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
                    camera_model= process_data_utils.CAMERA_MODELS[self.camera_type],
                    gpu=self.gpu,
                    verbose= self.verbose,
                    matching_method=self.matching_method,
                    colmap_cmd=self.colmap_cmd                    
                )
            
            elif sfm_tool == "hloc":
                hloc_utils.run_hloc(
                    image_dir=image_dir,
                    colmap_dir=colmap_dir,
                    camera_model=process_data_utils.CAMERA_MODELS[self.camera_type],
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
                    camera_model=process_data_utils.CAMERA_MODELS[self.camera_type],
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
                    camera_model=CAMERA_MODELS[camera_type],
                    gpu=gpu,
                    verbose=verbose,
                    matching_method=matching_method,
                    colmap_cmd=colmap_cmd,
                )
            elif sfm_tool == "hloc":
                hloc_utils.run_hloc(
                    image_dir=image_dir,
                    colmap_dir=colmap_dir,
                    camera_model=CAMERA_MODELS[camera_type],
                    verbose=verbose,
                    matching_method=matching_method,
                    feature_type=feature_type,
                    matcher_type=matcher_type,
                )
            else:
                CONSOLE.log("[bold red]Invalid combination of sfm_tool, feature_type, and matcher_type, exiting")
                sys.exit(1)

        # Save transforms.json
        if (colmap_dir / "sparse" / "0" / "cameras.bin").exists():
            with CONSOLE.status("[bold yellow]Saving results to transforms.json", spinner="balloon"):
                num_matched_frames = colmap_utils.colmap_to_json(
                    cameras_path=colmap_dir / "sparse" / "0" / "cameras.bin",
                    images_path=colmap_dir / "sparse" / "0" / "images.bin",
                    output_dir=output_dir,
                    camera_model=CAMERA_MODELS[camera_type],
                )
                summary_log.append(f"Colmap matched {num_matched_frames} images")
            summary_log.append(colmap_utils.get_matching_summary(num_extracted_frames, num_matched_frames))
        else:
            CONSOLE.log("[bold yellow]Warning: could not find existing COLMAP results. Not generating transforms.json")

        CONSOLE.rule("[bold green]:tada: :tada: :tada: All DONE :tada: :tada: :tada:")

        for summary in summary_log:
            CONSOLE.print(summary, justify="center")
        CONSOLE.rule()
