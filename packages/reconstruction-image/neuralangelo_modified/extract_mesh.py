

import argparse
import json
import os
import sys
import numpy as np
from functools import partial

sys.path.append(os.getcwd())

from neuralangelo_modified.utils.config import Config, recursive_update_strict, parse_cmdline_arguments 
from neuralangelo_modified.utils.gpu_jobs import init_dist, get_world_size, is_master, master_only_print as print  
from neuralangelo_modified.utils.misc import set_affinity, get_trainers, extract_mesh, extract_texture


def parse_args():
    parser = argparse.ArgumentParser(description="Extracting mesh from the preprocessed data image")
    parser.add_argument("--config", required=True, help="Path to the training config file.")
    parser.add_argument("--checkpoint", default="", help="Checkpoint path.")
    parser.add_argument('--local_rank', type=int,help="defines the compute node seed in order to train the dataset randomly", default=os.getenv('LOCAL_RANK', 0))
    parser.add_argument("--bacalhau", action="store_true")
    parser.add_argument("--resolution", default=512, type=int, help="Marching cubes resolution")
    parser.add_argument("--block_res", default=64, type=int, help="Block-wise resolution for marching cubes")
    parser.add_argument("--output_file", default="mesh.ply", type=str, help="Output file name")
    parser.add_argument("--textured", action="store_true", help="Export mesh with texture")
    parser.add_argument("--keep_lcc", action="store_true",
                        help="Keep only largest connected component. May remove thin structures.")
    
    
    args, commands_config  = parser.parse_known_args()
    return args, commands_config


def main():
    args, commands_config = parse_args()
    configuraton = Config(args.config)
    
    ## getting the parameters in the listed format as input for the function.
    configuration_command = parse_cmdline_arguments(commands_config)
    recursive_update_strict(configuraton, commands_config)
    
    ## if the distributed parallel training is activated, we'll be deactivating the distributed data parallel
    
    if not args.single_gpu:
        # this disables nccl timeout
        os.environ["NCLL_BLOCKING_WAIT"] = "0"
        os.environ["NCCL_ASYNC_ERROR_HANDLING"] = "0"
        configuraton.local_rank = args.local_rank
        init_dist(configuraton.local_rank, rank=-1, world_size=-1)
    print(f"Running mesh extraction with {get_world_size()} GPUs.")

    ## setting up the data pipeline along w/ previous trained checkpoint object
    trainer = get_trainers(configuraton, is_inference=True, seed=0)
    trainer.checkpointer.load(args.checkpoint, load_opt=False, load_sch=False)
    trainer.model.eval()
    
    # Set the coarse-to-fine levels.
    trainer.current_iteration = trainer.checkpointer.eval_iteration
    if configuraton.model.object.sdf.encoding.coarse2fine.enabled:
        trainer.model_module.neural_sdf.set_active_levels(trainer.current_iteration)
        if configuraton.model.object.sdf.gradient.mode == "numerical":
            trainer.model_module.neural_sdf.set_normal_epsilon()

    meta_fname = f"{configuraton.data.root}/transforms.json"
    with open(meta_fname) as file:
        meta = json.load(file)

    if "aabb_range" in meta:
        bounds = (np.array(meta["aabb_range"]) - np.array(meta["sphere_center"])[..., None]) / meta["sphere_radius"]
    else:
        bounds = np.array([[-1.0, 1.0], [-1.0, 1.0], [-1.0, 1.0]])

    sdf_func = lambda x: -trainer.model_module.neural_sdf.sdf(x)  # noqa: E731
    texture_func = partial(extract_texture, neural_sdf=trainer.model_module.neural_sdf,
                           neural_rgb=trainer.model_module.neural_rgb,
                           appear_embed=trainer.model_module.appear_embed) if args.textured else None
    mesh = extract_mesh(sdf_func=sdf_func, bounds=bounds, intv=(2.0 / args.resolution),
                        block_res=args.block_res, texture_func=texture_func, filter_lcc=args.keep_lcc)

    if is_master():
        print(f"vertices: {len(mesh.vertices)}")
        print(f"faces: {len(mesh.faces)}")
        if args.textured:
            print(f"colors: {len(mesh.visual.vertex_colors)}")
        # center and scale
        mesh.vertices = mesh.vertices * meta["sphere_radius"] + np.array(meta["sphere_center"])
        mesh.update_faces(mesh.nondegenerate_faces())
        os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
        mesh.export(args.output_file)
        
if __name__ == "__main__":
    main()