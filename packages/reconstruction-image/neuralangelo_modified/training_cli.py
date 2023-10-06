"""
runs the command (either locally via CLI or via orchestrator) in order to train the model for the batch of images
"""

import utils.gpu_jobs
import utils.misc 
import argparse
from neuralangelo_modified.utils.config import Config, recursive_update, recursive_update_strict, DEBUG
from neuralangelo_modified.utils.misc import init_cudnn, set_affinity, set_random_seed, init_logging, get_trainers
from neuralangelo_modified.utils.gpu_jobs import broadcast_object_list, is_master
import yaml
import os




def parse_args():
    parser = argparse.ArgumentParser(description="train the batch of images/video on neuralangelo for generating the reconstruction")
    parser.add_argument('--config', help='path to the yaml config file', required=True)
    parser.add_argument('--input_data',help="defines the category of the input data" ,choices=['images','video'],required=True)
    parser.add_argument('--dir', help='path to directory containing corresponding image/video of given area to be reconstructed')
    parser.add_argument('--checkpoint', help="path corresponding to the previous training epochs")
    parser.add_argument('--seed',type=int, default=0, help='Random number for deterining the start of training batch')
    parser.add_argument('--local_rank',help="defines the details for the local rank of the model", type=int, default=os.getenv('LOCAL_RANK', 0))
    parser.add_argument('--bacalhau_deployment', choices=[True, False], default=True, help="Whether to deploy the model on bacalhau or locally")
    parser.add_argument('--single_node', choices=[True, False], default=False, help="whether the training session is to be done on the single node compute cluster" )
    parser.add_argument('--debug', help="verbose description of the blogs on the terminal",action='store_true')
    parser.add_argument('--logger', action='store_true', help="Enable using W&B to store the training statistics")
    args, config_args = parser.parse_known_args()
    return args, config_args



def parse_cli(args: list(any)):
    """
    Helper method that takes the string representation of the cmd and then gets the result: 
    checks for regex patterns:
            --key1.key2.key3=value --> value
            --key1.key2.key3=      --> None
            --key1.key2.key3       --> True
            --key1.key2.key3!      --> False    
    
    """
    cfg_cmd = {}
    for arg in args:
        assert arg.startswith("--")
        if "=" not in arg[2:]:
            key_str, value = (arg[2:-1], "false") if arg[-1] == "!" else (arg[2:], "true")
        else:
            key_str, value = arg[2:].split("=")
        keys_sub = key_str.split(".")
        cfg_sub = cfg_cmd
        for k in keys_sub[:-1]:
            cfg_sub.setdefault(k, {})
            cfg_sub = cfg_sub[k]
        assert keys_sub[-1] not in cfg_sub, keys_sub[-1]
        cfg_sub[keys_sub[-1]] = yaml.safe_load(value)
    return cfg_cmd





def main():
    argument_parsed, config_params = parse_args()
    
    set_affinity(argument_parsed.local_rank)  
    cfg = Config(argument_parsed.config)
    
    updated_config = parse_cli(config_params)
    
    recursive_update_strict(cfg, updated_config)
    
    # if running the training set on the single GPU, we will only assign one training node 
    # (either the bacalhau or the traditional training GPU instance).
    if not argument_parsed.single_node:
        os.environ["NCLL_BLOCKING_WAIT"] = "0"
        os.environ["NCCL_ASYNC_ERROR_HANDLING"] = "0"
        cfg.local_rank = argument_parsed.local_rank
        
    ## setting random training seed along with debugging mode
    set_random_seed(argument_parsed.seed, argument_parsed.local_rank)
    
    DEBUG = argument_parsed.debug
    
    cfg.logdir = init_logging(argument_parsed.config, argument_parsed.logdir, makedir=True)
    
    ## TODO: also define the function that instantiates the formatting of the bacalhau output.
    
    if is_master():
        cfg.print_config()
        cfg.save_config(cfg.logdir)
    
    ## create the cudnn training library
    init_cudnn(cfg.cudnn.deterministic, cfg.cudnn.benchmark)

    
    trainer =  get_trainers(cfg, is_inference=False, seed=argument_parsed.seeds)
    ## split the data into test and valuation components 
    
    trainer.set_data_loader(cfg, split="train")
    trainer.set_data_loader(cfg, split="val")
    trainer.checkpointer.load(argument_parsed.checkpoint, argument_parsed.resume, load_sch=True, load_opt=True)
 
    ## TODO: eventually need to handle the case of setup the wandb integration with flyte in order to get the batch training performance
    
    # Initialize Wandb.
    trainer.init_wandb(cfg,
                       project=argument_parsed.wandb_name,
                       mode="disabled" if argument_parsed.debug or not argument_parsed.wandb else "online",
                       resume=argument_parsed.resume,
                       use_group=True)

    trainer.mode = 'train'
    # Start training.
    trainer.train(cfg,
                  trainer.train_data_loader,
                  single_gpu=argument_parsed.single_gpu,
                  profile=argument_parsed.profile,
                  show_pbar=argument_parsed.show_pbar)

    # Finalize training.
    trainer.finalize(cfg)





if __name__ == "__main__":
    main()
