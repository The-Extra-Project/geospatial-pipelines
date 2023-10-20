import functools
import torch.distributed as dist
from contextlib import contextmanager
import torch
from neuralangelo_modified.utils.config import Model
from torch.optim import lr_scheduler
import ctypes


def master_only(func):
    r"""Apply this function only to the master GPU."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        r"""Simple function wrapper for the master function"""
        if get_rank() == 0:
            return func(*args, **kwargs)
        else:
            return None
    return wrapper

@master_only
def master_only_print(*args):
    r"""master-only print"""
    print(*args)

## trainer jobs

@master_only
def get_optimizer(cfg_optim, model: Model ):
    r""" return the optimizers
        Args:
            cfg_optim(obj): Configuration for specific optimization module.
            model(obj): Pytorch network module
        Return
            object:  object corresponding to pytorch optimizer 
    """
    return (model.get_param_groups(cfg_optim)  if hasattr(model, 'get_param_groups') else model.parameters())        



@master_only
def get_scheduler(cfg_optim, optim):
    """
    getting the scheduler object of the various training jobs. here based on the configuration defining the category of training in configuration
    Args:
        cfg_optim (obj): Config for the specific optimization module (gen/dis).
        optim (obj): PyTorch optimizer object.

    Returns:
        (obj): Scheduler
    """
    
    if cfg_optim.sched.type == "linear_warmup":
        x = (x / cfg_optim.sched.warmup if x < cfg_optim.sched.warmup else  1.0)
        scheduler = lr_scheduler.LambdaLR(optimizer=optim, lr_lambda=(x,))
    elif cfg_optim.sched.type == 'step':
        scheduler = lr_scheduler.StepLR(optim,
                                        step_size=cfg_optim.sched.step_size,
                                        gamma=cfg_optim.sched.gamma)
    elif cfg_optim.sched.type == 'constant':
        scheduler = lr_scheduler.LambdaLR(optim, lambda x: 1)
        
    elif cfg_optim.sched.type == 'cosine_warmup':

        warmup_scheduler = lr_scheduler.LinearLR(
            optim,
            start_factor=1.0 / cfg_optim.sched.warmup,
            end_factor=1.0,
            total_iters=cfg_optim.sched.warmup
        )
        T_max_val = cfg_optim.sched.decay_steps - cfg_optim.sched.warmup
        cosine_lr_scheduler = lr_scheduler.CosineAnnealingLR(
            optim,
            T_max=T_max_val,
            eta_min=getattr(cfg_optim.sched, 'eta_min', 0),
        )
        scheduler = lr_scheduler.SequentialLR(
            optim,
            schedulers=[warmup_scheduler, cosine_lr_scheduler],
            milestones=[cfg_optim.sched.warmup]
        )
        
        
    elif cfg_optim.sched.type == 'linear':
        # Start linear decay from here.
        decay_start = cfg_optim.sched.decay_start
        # End linear decay here.
        # Continue to train using the lowest learning rate till the end.
        decay_end = cfg_optim.sched.decay_end
        # Lowest learning rate multiplier.
        decay_target = cfg_optim.sched.decay_target
        
        decay = ((x - decay_start) * decay_target + decay_end - x) / (decay_end - decay_start)
        
        scheduler = lr_scheduler.LambdaLR(optim, lambda x: decay)
    elif cfg_optim.sched.type == 'step_with_warmup':
        # The step_size and gamma follows the signature of lr_scheduler.StepLR.
        step_size = cfg_optim.sched.step_size,
        gamma = cfg_optim.sched.gamma
        # An additional parameter defines the warmup iteration.
        warmup_step_size = cfg_optim.sched.warmup_step_size
        
        lr_after_warmup = gamma ** (warmup_step_size // step_size)
        
        lr_lambda = gamma ** (x // step_size)
        
        scheduler = lr_scheduler.LambdaLR(optim, lambda x: lr_lambda)
        
    else:
        return NotImplementedError('Learning rate policy {} not implemented.'.format(cfg_optim.sched.type))
    
    return scheduler


def is_master():
    r"""check if current process is the master"""
    return get_rank() == 0


def get_rank():
    r"""Get rank of the thread."""
    rank = 0
    if dist.is_available():
        if dist.is_initialized():
            rank = dist.get_rank()
    return rank

@master_only
def master_print(*args):
    r"""Print function that only runs on master GPU."""
    print(*args)



def get_world_size():
    r"""Get world size. How many GPUs are available in this job."""
    world_size = 1
    if dist.is_available():
        if dist.is_initialized():
            world_size = dist.get_world_size()
    return world_size


def dist_all_gather_tensor(tensor):
    r""" gather to all ranks """
    world_size = get_world_size()
    if world_size < 2:
        return [tensor]
    tensor_list = [
        torch.ones_like(tensor) for _ in range(dist.get_world_size())]
    with torch.no_grad():
        dist.all_gather(tensor_list, tensor)
    return tensor_list




def dist_all_reduce_tensor(tensor, reduce='mean'):
    r""" Reduce to all ranks """
    world_size = get_world_size()
    if world_size < 2:
        return tensor
    with torch.no_grad():
        dist.all_reduce(tensor)
        if reduce == 'mean':
            tensor /= world_size
        elif reduce == 'sum':
            pass
        else:
            raise NotImplementedError
    return tensor



def collate_test_data_batches(data_batches):
    """Aggregate the list of test data from all gpu's and process the results.
    Args:
        data_batches (list): List of (hierarchical) dictionaries, where leaf entries are tensors.
    Returns:
        data_gather (dict): (hierarchical) dictionaries, where leaf entries are concatenated tensors.
    """
    data_gather = dict()
    for key in data_batches[0].keys():
        data_list = [data[key] for data in data_batches]
        if isinstance(data_batches[0][key], dict):
            data_gather[key] = collate_test_data_batches(data_list)
        elif isinstance(data_batches[0][key], torch.Tensor):
            data_gather[key] = torch.cat(data_list, dim=0)
            data_gather[key] = torch.cat(dist_all_gather_tensor(data_gather[key].contiguous()), dim=0)
        else:
            raise TypeError
    return data_gather


def get_unique_test_data(data_gather, idx):
    """Aggregate the list of test data from all devices and process the results.
    Args:
        data_gather (dict): (hierarchical) dictionaries, where leaf entries are tensors.
        idx (tensor): sample indices.
    Returns:
        data_all (dict): (hierarchical) dictionaries, where leaf entries are tensors ordered by idx.
    """
    data_all = dict()
    for key, value in data_gather.items():
        if isinstance(value, dict):
            data_all[key] = get_unique_test_data(value, idx)
        elif isinstance(value, torch.Tensor):
            data_all[key] = []
            for i in range(max(idx) + 1):
                # If multiple occurrences of the same idx, just choose the first one. If no occurrence, just ignore.
                matches = (idx == i).nonzero(as_tuple=True)[0]
                if matches.numel() != 0:
                    data_all[key].append(value[matches[0]])
            data_all[key] = torch.stack(data_all[key], dim=0)
        else:
            raise TypeError
    return data_all


def trim_test_samples(data, max_samples=None):
    for key, value in data.items():
        if isinstance(value, dict):
            data[key] = trim_test_samples(value, max_samples=max_samples)
        elif isinstance(value, torch.Tensor):
            if max_samples is not None:
                data[key] = value[:max_samples]
        else:
            raise TypeError

def broadcast_object_list(message, src=0):
    r"""broadcast the messages from across the GPU nodes"""
    if dist.is_available():
        if dist.is_initialized():
            torch.distributed.broadcast_object_list(message, src=src)
    return message


def init_dist(local_rank, backend='nccl', **kwargs):
    r""" start training across multiple distributed instances if enabled
    """
    if dist.is_available():
        if dist.is_initialized():
            return torch.cuda.current_device()
        torch.cuda.set_device(local_rank)
        dist.init_process_group(backend=backend, init_method='env://', **kwargs)

    _libcudart = ctypes.CDLL('libcudart.so')
    pValue = ctypes.cast((ctypes.c_int * 1)(), ctypes.POINTER(ctypes.c_int))
    _libcudart.cudaDeviceSetLimit(ctypes.c_int(0x05), ctypes.c_int(128))
    _libcudart.cudaDeviceGetLimit(pValue, ctypes.c_int(0x05))

    