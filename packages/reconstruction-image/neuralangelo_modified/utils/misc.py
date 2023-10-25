
import collections
import functools
import os
import signal
import time
from collections import OrderedDict
import random
import torch
import torch.nn.functional as F
import wandb
import numpy as np
import mcubes 
from neuralangelo_modified.utils.gpu_jobs import get_rank, is_master, broadcast_object_list
from neuralangelo_modified.utils.config import Device, WrappedModel, LatticeGrid, get_lattice_grid_loader
from neuralangelo_modified.dataset.sampler import DistributedSamplerPreemptable
from neuralangelo_modified.utils.misc import WrappedModel,ModelAverage
from neuralangelo_modified.dataset.base import MultiEpochsDatasetLoader
import importlib
import pynvml
import yaml
import datetime

import torch.distributed as dist

from torch.nn import init
import torch.backends.cudnn as cudnn





## tuple that conssit of naming parameters along with binary format of the tensor info.
string_classes = (str, bytes)


def _create_logdir(_config_path, _logdir, _root_dir: str, makedir: bool):
    config_file = os.path.basename(_config_path)
    date_uid = str(datetime.datetime.now().strftime("%Y_%m%d_%H%M_%S")) ## defining the random logging dir name based on the 
    # example: logs/2019_0125_1047_58_spade_cocostuff
    _log_file = '_'.join([date_uid, os.path.splitext(config_file)[0]])
    if _logdir is None:
        _logdir = os.path.join(_root_dir, _log_file)
    if makedir:
        print('Make folder {}'.format(_logdir))
        os.makedirs(_logdir, exist_ok=True)
    return _logdir


## initialization functions


def init_cudnn(deterministic, benchmark):
    r"""Initialize the cudnn module. The two things to consider is whether to
    
    initialize the version of the cudnn (either the deterministic or the benchmark) 
    based on the configuration during training process
    
    Args:
        deterministic (bool): Whether to use cudnn deterministic.
        benchmark (bool): Whether to use cudnn benchmark.
    """
    cudnn.deterministic = deterministic
    cudnn.benchmark = benchmark
    print('cudnn benchmark: {}'.format(benchmark))
    print('cudnn deterministic: {}'.format(deterministic))


def init_logging(config_path, logdir, makedir=True):
    r"""
    storing the logs for acting as checkpoints.
    Args:
        config_path (str): Path to the configuration file.
        logdir (str or None): Log directory name
        makedir (bool): Make a new dir or not
    Returns:
        str: Return log dir
    """
    
    root_dir = 'logs'
    if dist.is_available():
        if dist.is_initialized():
            message = [None]
            if is_master():
                logdir = _create_logdir(config_path, logdir, root_dir)
                message = [logdir]

            # Send logdir from master to all workers.
            message = broadcast_object_list(message=message, src=0)
            logdir = message[0]
        else:
            logdir = _create_logdir(config_path, logdir, root_dir)
    else:
        logdir = _create_logdir(config_path, logdir, root_dir)

    return logdir



def requires_grad(model, require=True):
    r""" Set a model to require gradient or not.

    Args:
        model (nn.Module): Neural network model.
        require (bool): Whether the network requires gradient or not.

    Returns:

    """
    for p in model.parameters():
        p.requires_grad = require




def parse_cmdline_arguments(args):
    """
    Parse arguments from command line arguments for cli.
    Syntax: --key1.key2.key3=value --> value
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



def set_random_seed(seed, by_rank=False):
    r"""Set random seeds for the functions or parameters that require randomness during the training process, 
    like random, numpy, torch.manual_seed, torch.cuda_manual_seed.
    torch.cuda.manual_seed_all is not necessary (included in torch.manual_seed)

    Args:
        seed (int): Random seed.
        by_rank (bool): if true, each gpu will use a different random seed.
    """
    if by_rank:
        seed += get_rank()
    print(f"Using random seed {seed}")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)         # sets seed on the current CPU & all GPUs
    torch.cuda.manual_seed(seed)    # sets seed on current GPU
    torch.cuda.manual_seed_all(seed)  # included in torch.manual_seed


def set_affinity():
    r"""Set GPU affinity

    Args:
        gpu_id (int): Which gpu device.
    """
    if gpu_id is None:
        gpu_id = int(os.getenv('LOCAL_RANK', 0))

    try:
        dev = Device(gpu_id)
        # os.sched_setaffinity() method in Python is used to set the CPU affinity mask of a process indicated
        # by the specified process id.
        # A process’s CPU affinity mask determines the set of CPUs on which it is eligible to run.
        # Syntax: os.sched_setaffinity(pid, mask)
        # pid=0 means the current process
        os.sched_setaffinity(0, dev.get_cpu_affinity())
        # list of ints
        # representing the logical cores this process is now affinitied with
        return os.sched_getaffinity(0)

    except pynvml.NVMLError:
        print("(Setting affinity with NVML failed, skipping...)")
        
        

def alarm_handler(timeout_period):
    # What to do when the process gets stuck. For now, we simply end the process.
    error_message = f"Timeout error! More than {timeout_period} seconds have passed since the last iteration. Most " \
                    f"likely the process has been stuck due to node failure or PBSS error."
    ngc_job_id = os.environ.get('NGC_JOB_ID', None)
    if ngc_job_id is not None:
        error_message += f" Failed NGC job ID: {ngc_job_id}."
    # Let's reserve `wandb.alert` for this purpose.
    wandb.alert(title="Timeout error!", text=error_message, level=wandb.AlertLevel.ERROR)
    exit()



## conversion util functions


def apply_imagenet_normalization(input):
    r"""Normalize using ImageNet mean and std.

    Args:
        input (4D tensor NxCxHxW): The input images, assuming to be [-1, 1].

    Returns:
        Normalized inputs using the ImageNet normalization.
    """
    # normalize the input back to [0, 1]
    normalized_input = (input + 1) / 2
    # normalize the input using the ImageNet mean and std
    mean = normalized_input.new_tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
    std = normalized_input.new_tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
    output = (normalized_input - mean) / std
    return output

def random_shift(x, offset=0.05, mode='bilinear', padding_mode='reflection'):
    r"""Randomly shift the input tensor.

    Args:
        x (4D tensor): The input batch of images.
        offset (int): The maximum offset ratio that is between [0, 1].
        The maximum shift is offset * image_size for each direction.
        mode (str): The resample mode for 'F.grid_sample'.
        padding_mode (str): The padding mode for 'F.grid_sample'.

    Returns:
        x (4D tensor) : The randomly shifted image.
    """
    assert x.dim() == 4, "Input must be a 4D tensor."
    batch_size = x.size(0)
    theta = torch.eye(2, 3, device=x.device).unsqueeze(0).repeat(
        batch_size, 1, 1)
    theta[:, :, 2] = 2 * offset * torch.rand(batch_size, 2) - offset
    grid = F.affine_grid(theta, x.size())
    x = F.grid_sample(x, grid, mode=mode, padding_mode=padding_mode, align_corners=False)
    return x


def gradient_norm(model):
    r"""Return the gradient norm of model for debugging or checking the convergence of the hyperparams

    Args:
        model (PyTorch module): Your network.

    """
    total_norm = 0
    for p in model.parameters():
        if p.grad is not None:
            param_norm = p.grad.norm(2)
            total_norm += param_norm.item() ** 2
    return total_norm ** ( 1. / 2 )




def random_shift(x, offset=0.05, mode='bilinear', padding_mode='reflection'):
    r"""Randomly shift the input tensor.

    Args:
        x (4D tensor): The input batch of images.
        offset (int): The maximum offset ratio that is between [0, 1].
        The maximum shift is offset * image_size for each direction.
        mode (str): The resample mode for 'F.grid_sample'.
        padding_mode (str): The padding mode for 'F.grid_sample'.

    Returns:
        x (4D tensor) : The randomly shifted image.
    """
    assert x.dim() == 4, "Input must be a 4D tensor."
    batch_size = x.size(0)
    theta = torch.eye(2, 3, device=x.device).unsqueeze(0).repeat(
        batch_size, 1, 1)
    theta[:, :, 2] = 2 * offset * torch.rand(batch_size, 2) - offset
    grid = F.affine_grid(theta, x.size())
    x = F.grid_sample(x, grid, mode=mode, padding_mode=padding_mode, align_corners=False)
    return x


def get_nested_attr(cfg, attr_name, default):
    r"""Iteratively try to get the attribute from cfg. If not found, return
    default.

    Args:
        cfg (obj): Config file.
        attr_name (str): Attribute name (e.g. XXX.YYY.ZZZ).
        default (obj): Default return value for the attribute.

    Returns:
        (obj): Attribute value.
    """
    names = attr_name.split('.')
    atr = cfg
    for name in names:
        if not hasattr(atr, name):
            return default
        atr = getattr(atr, name)
    return atr

def get_and_setattr(cfg, name, default):
    r"""Get attribute with default choice. If attribute does not exist, set it
    using the default value.

    Args:
        cfg (obj) : Config options.
        name (str) : Attribute name.
        default (obj) : Default attribute.

    Returns:
        (obj) : Desired attribute.
    """
    if not hasattr(cfg, name) or name not in cfg.__dict__:
        setattr(cfg, name, default)
    return getattr(cfg, name)


def get_nested_attr(cfg, attr_name, default):
    r"""Iteratively try to get the attribute from cfg. If not found, return
    default.

    Args:
        cfg (obj): Config file.
        attr_name (str): Attribute name (e.g. XXX.YYY.ZZZ).
        default (obj): Default return value for the attribute.

    Returns:
        (obj): Attribute value.
    """
    names = attr_name.split('.')
    atr = cfg
    for name in names:
        if not hasattr(atr, name):
            return default
        atr = getattr(atr, name)
    return atr


## adding functions for fetching the training, validation 
## training classes 
## credits to NVIDIA neuralangelo implementation.

from neuralangelo_modified.dataset.sampler import DistributedPreemptableScheduler

def _get_train_dataset_objects(cfg, subset_indices=None):
    r"""Return dataset objects for the training set.
    Args:
        cfg (obj): Global configuration file.
        subset_indices (sequence): Indices of the subset to use.

    Returns:
        train_dataset (obj): PyTorch training dataset object.
    """
    dataset_module = importlib.import_module(cfg.data.type)
    train_dataset = dataset_module.Dataset(cfg, is_inference=False)
    if subset_indices is not None:
        train_dataset = torch.utils.data.Subset(train_dataset, subset_indices)
    print('Train dataset length:', len(train_dataset))
    return train_dataset


def _get_val_dataset_objects(cfg, subset_indices=None):
    r"""Return dataset objects for the validation set.
    Args:
        cfg (obj): Global configuration file.
        subset_indices (sequence): Indices of the subset to use.
    Returns:
        val_dataset (obj): PyTorch validation dataset object.
    """
    dataset_module = importlib.import_module(cfg.data.type)
    if hasattr(cfg.data.val, 'type'):
        for key in ['type', 'input_types', 'input_image']:
            setattr(cfg.data, key, getattr(cfg.data.val, key))
        dataset_module = importlib.import_module(cfg.data.type)
    val_dataset = dataset_module.Dataset(cfg, is_inference=True)

    if subset_indices is not None:
        val_dataset = torch.utils.data.Subset(val_dataset, subset_indices)
    print('Val dataset length:', len(val_dataset))
    return val_dataset


def _get_test_dataset_object(cfg, subset_indices=None):
    r"""Return dataset object for the test set

    Args:
        cfg (obj): Global configuration file.
        subset_indices (sequence): Indices of the subset to use.
    Returns:
        (obj): PyTorch dataset object.
    """
    dataset_module = importlib.import_module(cfg.test_data.type)
    test_dataset = dataset_module.Dataset(cfg, is_inference=True, is_test=True)
    if subset_indices is not None:
        test_dataset = torch.utils.data.Subset(test_dataset, subset_indices)
    return test_dataset


def _get_data_loader(cfg, dataset, batch_size, not_distributed=False,
                     shuffle=True, drop_last=True, seed=0, use_multi_epoch_loader=False,
                     preemptable=False):
    r"""Return data loader .

    Args:
        cfg (obj): Global configuration file.
        dataset (obj): PyTorch dataset object.
        batch_size (int): Batch size.
        not_distributed (bool): Do not use distributed samplers.
        shuffle (bool): Whether to shuffle the data
        drop_last (bool): Whether to drop the last batch is the number of samples is smaller than the batch size
        seed (int): random seed.
        preemptable (bool): Whether to handle preemptions.
    Return:
        (obj): Data loader.
    """
    not_distributed = not_distributed or not dist.is_initialized()
    if not_distributed:
        sampler = None
    else:
        if preemptable:
            sampler = DistributedSamplerPreemptable(dataset, shuffle=shuffle, seed=seed)
        else:
            sampler = torch.utils.data.distributed.DistributedSampler(dataset, shuffle=shuffle, seed=seed)
    num_workers = getattr(cfg.data, 'num_workers', 8)
    persistent_workers = getattr(cfg.data, 'persistent_workers', False)
    data_loader = (MultiEpochsDatasetLoader if use_multi_epoch_loader else torch.utils.data.DataLoader)(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle and (sampler is None),
        sampler=sampler,
        pin_memory=True,
        num_workers=num_workers,
        drop_last=drop_last,
        persistent_workers=persistent_workers if num_workers > 0 else False
    )
    return data_loader


def get_train_dataloader(
        cfg, shuffle=True, drop_last=True, subset_indices=None, seed=0, preemptable=False):
    r"""Return dataset objects for the training and validation sets.
    Args:
        cfg (obj): Global configuration file.
        shuffle (bool): Whether to shuffle the data
        drop_last (bool): Whether to drop the last batch is the number of samples is smaller than the batch size
        subset_indices (sequence): Indices of the subset to use.
        seed (int): random seed.
        preemptable (bool): Flag for preemption handling
    Returns:
        train_data_loader (obj): Train data loader.
    """
    train_dataset = _get_train_dataset_objects(cfg, subset_indices=subset_indices)
    train_data_loader = _get_data_loader(
        cfg, train_dataset, cfg.data.train.batch_size, not_distributed=False,
        shuffle=shuffle, drop_last=drop_last, seed=seed,
        use_multi_epoch_loader=cfg.data.use_multi_epoch_loader,
        preemptable=preemptable
    )
    return train_data_loader


def get_val_dataloader(cfg, subset_indices=None, seed=0):
    r"""Return dataset objects for the training and validation sets.
    Args:
        cfg (obj): Global configuration file.
        subset_indices (sequence): Indices of the subset to use.
        seed (int): random seed.
    Returns:
        val_data_loader (obj): Val data loader.
    """
    val_dataset = _get_val_dataset_objects(cfg, subset_indices=subset_indices)
    not_distributed = getattr(cfg.data, 'val_data_loader_not_distributed', False)
    # We often use a folder of images to represent a video. As doing evaluation, we like the images to preserve the
    # original order. As a result, we do not want to distribute images from the same video to different GPUs.
    not_distributed = 'video' in cfg.data.type or not_distributed
    drop_last = getattr(cfg.data.val, 'drop_last', False)
    # Validation loader need not have preemption handling.
    val_data_loader = _get_data_loader(
        cfg, val_dataset, cfg.data.val.batch_size, not_distributed=not_distributed,
        shuffle=False, drop_last=drop_last, seed=seed,
        preemptable=False
    )
    return val_data_loader


def get_test_dataloader(cfg, subset_indices=None):
    r"""Return dataset objects for testing

    Args:
        cfg (obj): Global configuration file.
        subset_indices (sequence): Indices of the subset to use.
    Returns:
        (obj): Test data loader. It may not contain the ground truth.
    """
    test_dataset = _get_test_dataset_object(cfg, subset_indices=subset_indices)
    not_distributed = getattr(
        cfg.test_data, 'val_data_loader_not_distributed', False)
    not_distributed = 'video' in cfg.test_data.type or not_distributed
    test_data_loader = _get_data_loader(
        cfg, test_dataset, cfg.test_data.test.batch_size, not_distributed=not_distributed,
        shuffle=False)
    return test_data_loader




# train_dataset = dataset_module.Dataset(cfg, is_inference=False)
#     if subset_indices is not None:
#         train_dataset = torch.utils.data.Subset(train_dataset, subset_indices)
#     print('Train dataset length:', len(train_dataset))





def santize_args(name, locals_fn):
    args = {k: v for k, v in locals_fn.items()}
    if 'kwargs' in args and args['kwargs']:
        unused = args['kwargs']
        print(f'{name}: Unused kwargs\n{unused}')

    keys_to_remove = ['self', 'kwargs']
    for k in keys_to_remove:
        args.pop(k, None)
    print(f'{name}: Used args\n{args}', 'green')
    return args


def split_labels(labels, label_lengths):
    r"""Split concatenated labels into their parts.

    Args:
        labels (torch.Tensor): Labels obtained through concatenation.
        label_lengths (OrderedDict): Containing order of labels & their lengths.

    Returns:

    """
    assert isinstance(label_lengths, OrderedDict)
    start = 0
    outputs = {}
    for data_type, length in label_lengths.items():
        end = start + length
        if labels.dim() == 5:
            outputs[data_type] = labels[:, :, start:end]
        elif labels.dim() == 4:
            outputs[data_type] = labels[:, start:end]
        elif labels.dim() == 3:
            outputs[data_type] = labels[start:end]
        start = end
    return outputs


def to_device(data, device):
    r"""Move all tensors inside data to device.

    Args:
        data (dict, list, or tensor): Input data.
        device (str): 'cpu' or 'cuda'.
    """
    if isinstance(device, str):
        device = torch.device(device)
    assert isinstance(device, torch.device)

    if isinstance(data, torch.Tensor):
        data = data.to(device)
        return data
    elif isinstance(data, collections.abc.Mapping):
        return type(data)({key: to_device(data[key], device) for key in data})
    elif isinstance(data, collections.abc.Sequence) and not isinstance(data, string_classes):
        return type(data)([to_device(d, device) for d in data])
    else:
        return data


def to_cuda(data):
    r"""Move all tensors inside data to gpu.

    Args:
        data (dict, list, or tensor): Input data.
    """
    return to_device(data, 'cuda')


def to_cpu(data):
    r"""Move all tensors inside data to cpu.

    Args:
        data (dict, list, or tensor): Input data.
    """
    return to_device(data, 'cpu')


def to_half(data):
    r"""Move all floats to half.

    Args:
        data (dict, list or tensor): Input data.
    """
    if isinstance(data, torch.Tensor) and torch.is_floating_point(data):
        data = data.half()
        return data
    elif isinstance(data, collections.abc.Mapping):
        return type(data)({key: to_half(data[key]) for key in data})
    elif isinstance(data, collections.abc.Sequence) and not isinstance(data, string_classes):
        return type(data)([to_half(d) for d in data])
    else:
        return data


def to_float(data):
    r"""Move all halfs to float.

    Args:
        data (dict, list or tensor): Input data.
    """
    if isinstance(data, torch.Tensor) and torch.is_floating_point(data):
        data = data.float()
        return data
    elif isinstance(data, collections.abc.Mapping):
        return type(data)({key: to_float(data[key]) for key in data})
    elif isinstance(data, collections.abc.Sequence) and not isinstance(data, string_classes):
        return type(data)([to_float(d) for d in data])
    else:
        return data


def slice_tensor(data, start, end):
    r"""Slice all tensors from start to end.
    Args:
        data (dict, list or tensor): Input data.
    """
    if isinstance(data, torch.Tensor):
        data = data[start:end]
        return data
    elif isinstance(data, collections.abc.Mapping):
        return type(data)({key: slice_tensor(data[key], start, end) for key in data})
    elif isinstance(data, collections.abc.Sequence) and not isinstance(data, string_classes):
        return type(data)([slice_tensor(d, start, end) for d in data])
    else:
        return data    
    
def extract_texture(xyz, neural_rgb, neural_sdf, appear_embed):
    num_samples, _ = xyz.shape
    xyz_cuda = torch.from_numpy(xyz).float().cuda()[None, None]
    sdfs, feats = neural_sdf(xyz_cuda)
    gradients, _ = neural_sdf.compute_gradients(xyz_cuda, training=False, sdf=sdfs)
    normals = F.normalize(gradients, dim=-1)
    if appear_embed is not None:
        feat_dim = appear_embed.embedding_dim  # [1,1,N,C]
        app = torch.zeros([1, 1, num_samples, feat_dim], device=sdfs.device)  # TODO: hard-coded to zero. better way?
    else:
        app = None
    rgbs = neural_rgb.forward(xyz_cuda, normals, -normals, feats, app=app)  # [1,1,N,3]

## functions for initializing the weights

def weights_init(init_type: str, gain, bias=None):
    """
    initializing the weights in the network
    init_type(str): defines the type of initialization techniques
    gain:  corresponding value for the initialization technique
    bias(Object): defines the bias value, by default its None that defines for the initialization.
    returns:        
    (obj): init function to be applied
    """
    
    def init_func(m):
        r"""Init function

        Args:
            m: module to be weight initialized.
        """
        class_name = m.__class__.__name__
        if hasattr(m, 'weight') and (
                class_name.find('Conv') != -1 or
                class_name.find('Linear') != -1 or
                class_name.find('Embedding') != -1):
            lr_mul = getattr(m, 'lr_mul', 1.)
            gain_final = gain / lr_mul
            if init_type == 'normal':
                init.normal_(m.weight.data, 0.0, gain_final)
            elif init_type == 'xavier':
                init.xavier_normal_(m.weight.data, gain=gain_final)
            elif init_type == 'xavier_uniform':
                init.xavier_uniform_(m.weight.data, gain=gain_final)
            elif init_type == 'kaiming':
                init.kaiming_normal_(m.weight.data, a=0, mode='fan_in')
                with torch.no_grad():
                    m.weight.data *= gain_final
            elif init_type == 'kaiming_linear':
                init.kaiming_normal_(
                    m.weight.data, a=0, mode='fan_in', nonlinearity='linear'
                )
                with torch.no_grad():
                    m.weight.data *= gain_final
            elif init_type == 'orthogonal':
                init.orthogonal_(m.weight.data, gain=gain_final)
            elif init_type == 'none':
                pass
            else:
                raise NotImplementedError(
                    'initialization method [%s] is '
                    'not implemented' % init_type)
        if hasattr(m, 'bias') and m.bias is not None:
            if init_type == 'none':
                pass
            elif bias is not None:
                bias_type = getattr(bias, 'type', 'normal')
                if bias_type == 'normal':
                    bias_gain = getattr(bias, 'gain', 0.5)
                    init.normal_(m.bias.data, 0.0, bias_gain)
                else:
                    raise NotImplementedError(
                        'initialization method [%s] is '
                        'not implemented' % bias_type)
            else:
                init.constant_(m.bias.data, 0.0)
    return init_func


def weights_rescale():
    """
    function for scaling the weights based on the initialization parameters

    """
    def init_func(m):
        if hasattr(m, 'init_gain'):
            for name, p in m.named_parameters():
                if 'output_scale' not in name:
                    p.data.mul_(m.init_gain)
    return init_func

from neuralangelo_modified.utils.config import Config



## trainer util function



def get_trainers(cfg, is_inference=True, seed=0):
    r"""
    fetches the object initialized by the trainer class
    
    Args:
        cfg (Config): Loaded config object.
        is_inference (bool): Inference mode.
    Returns:
        (obj): Trainer object.
    """
    trainer_lib = importlib.import_module(cfg.trainer.type)
    trainer = trainer_lib.Trainer(cfg, is_inference=is_inference, seed=seed)
    return trainer



def cal_model_parameters(model: torch.nn.Module):
    '''
    Args:
    model (obj): object identifying the model which is to be trained
    '''
    init_params = 0
    for p in model.parameters():
        if p.requires_grad:
            init_params += p.numel()
    return init_params
    


def wrap_model(cfg, model):
    r""" provides wrapper function on top of pytorch distributed data parallel training 
    model / or the model average
    
    Args:
    cfg (obj): Global configuration.
    model (obj): Model object.

    Returns:
        (dict):
          - model (obj): Model object.    
    """


    # Apply model average wrapper.
    if cfg.trainer.ema_config.enabled:
        model = ModelAverage(model,
                             cfg.trainer.ema_config.beta,
                             cfg.trainer.ema_config.start_iteration,
                             )
 # Apply DDP wrapper.
    if dist.is_available() and dist.is_initialized():
        model = torch.nn.parallel.DistributedDataParallel(
            model,
            device_ids=[cfg.local_rank],
            output_device=cfg.local_rank,
            find_unused_parameters=cfg.trainer.ddp_config.find_unused_parameters,
            static_graph=cfg.trainer.ddp_config.static_graph,
            broadcast_buffers=False,
        )
    else:
        model = WrappedModel(model)
   
   

## functions for doing isometric extraction of the features.
@torch.no_grad()
def extract_mesh(sdf_func, bounds, intv, block_res=64, texture_fn= None, filter_lcc=False):
    """
    fetches the mesh details from the given regenerated images function given the corresponding neural differential function
    sdf_func: 
    
    
    """
    lattice_grid = LatticeGrid(bounds, intv=intv, block_res=block_res)
    data_loader = get_lattice_grid_loader(lattice_grid)
    mesh_blocks=[]
    for it, data in enumerate(data_loader):
        xyz = data["xyz"][0]
        xyz_cuda = xyz.cuda()
        sdf_cuda = sdf_func(xyz_cuda)[..., 0]
        sdf = sdf_cuda.cpu()
        mesh = marching_cubes_algorithm(sdf.numpy(), xyz.numpy(), intv, texture_fn, filter_lcc)
        mesh_blocks.append(mesh)

    
import trimesh

def filter_points_outside_bounding_sphere(old_mesh):
    
    mask = np.linalg.norm(old_mesh.vertices, axis=-1) < 1.0
    if np.any(mask):
        indices = np.ones(len(old_mesh.vertices), dtype=int) * -1
        indices[mask] = np.arange(mask.sum())
        faces_mask = mask[old_mesh.faces[:, 0]] & mask[old_mesh.faces[:, 1]] & mask[old_mesh.faces[:, 2]]
        new_faces = indices[old_mesh.faces[faces_mask]]
        new_vertices = old_mesh.vertices[mask]
        new_colors = old_mesh.visual.vertex_colors[mask]
        new_mesh = trimesh.Trimesh(new_vertices, new_faces, vertex_colors=new_colors)
    else:
        new_mesh = trimesh.Trimesh()
    return new_mesh
    
import mesh

def filter_largest_cc():
    r""" it filters the largest mesh that has the availablity of the image information  
    
    """
    components = mesh.split()
    areas = np.array([c.area for c in components], dtype=float)

    if len(areas) > 0 and mesh.vertices.shape[0] > 0:
        new_mesh = components[areas.argmax()]
    else:
        new_mesh = trimesh.Trimesh()
    return new_mesh

def marching_cubes_algorithm(sdf, xyz, intv, texture_func, filter_lcc):
        r""" implementation of the marching cubes algorithm that gives the polygon mesh from the iso-surface    
        """
        V, F = mcubes.marching_cubes(sdf, 0.)
        if V.shape[0] > 0:
            V = V * intv + xyz[0, 0, 0]
            if texture_func is not None:
                C = texture_func(V)
                mesh = trimesh.Trimesh(V, F, vertex_colors=C)
            else:
                mesh = trimesh.Trimesh(V, F)
            mesh = filter_points_outside_bounding_sphere(mesh)
            mesh = filter_largest_cc(mesh) if filter_lcc else mesh
        else:
            mesh = trimesh.Trimesh()
        return mesh

